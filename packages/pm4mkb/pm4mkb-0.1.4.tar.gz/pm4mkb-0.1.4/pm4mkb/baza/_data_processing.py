from __future__ import annotations
from multiprocessing import cpu_count
from re import IGNORECASE, compile as compile_regex
from typing import TYPE_CHECKING, Callable, Iterable

from loguru import logger

from numpy import nan, sum as np_sum, zeros
from pandarallel import pandarallel
from pandas import DataFrame

from pm4mkb.baza import SyntheticColumns

from .managers import (
    CalendarManager,
    DTypeManager,
    DateTimeManager,
    DurationManager,
    SortingManager,
    SuccessManager,
)


if TYPE_CHECKING:
    from re import Pattern
    from pandas import Series
    from pm4mkb.baza import DurationUnits, TimeErrors, DataHolder, HolderColumns, SuccessInputs


def _apply_wrapper(data: DataFrame) -> Callable:
    """
    Selects the apply or parallel_apply method for the given data

    Parameters
    ----------
        data: DataFrame
            The Pandas DataFrame to apply the function to.

    Returns
    -------
        Callable: The apply function to use with the given DataFrame.
    """

    def get_number_of_cores(data_on_load: DataFrame) -> int:
        """
        Calculates the number of cores to be used for the data load.
        The number is based on the amount of data memory usage.

        Parameters
        ----------
            data_on_load : DataFrame
                The data to be processed, probably in parallel.

        Returns
        -------
            int: The number of logical cores to be used.
        """
        mem_gigabytes = data_on_load.memory_usage().sum() // 1e9

        if mem_gigabytes < 2:  # memory below 2 GB
            return 1

        if mem_gigabytes >= 5:  # memory above 5 GB
            multiplier = 0.9
        elif mem_gigabytes >= 3:  # memory between 3 and 5 GB
            multiplier = 0.8
        elif mem_gigabytes == 2:  # memory between 2 and 3 GB
            multiplier = 0.5

        return max(1, int(multiplier * cpu_count()))

    parallel_cores = get_number_of_cores(data)

    if parallel_cores > 1:
        pandarallel.initialize(nb_workers=parallel_cores, progress_bar=False, use_memory_fs=False, verbose=0)

        return data.parallel_apply
    return data.apply


def _unify_missing_values(data: DataFrame, dtypes: str | Iterable[str] = "object") -> None:
    """
    Replaces various missing value representations in selected data with a single one: 'nan' in
    numpy, or 'NaN'/'NaT'... in pandas.

    Parameters
    ----------
    data : DataFrame
        The data with missing values
    dtypes: str | Iterable[str], default="object"
        Data types to engage in the replacement
    """

    def set_missing_as_nan(literal_series: Series, literal_na_pattern: Pattern) -> Series:
        """
        Replace null-like string values in a pandas Series to NaN based on a given regex pattern.

        Parameters
        ----------
        literal_series : Series
            The data for the replace operation.
        literal_na_pattern : Pattern
            The pattern to match for null-like string values.

        Returns
        -------
        Series
            The Series object with missing values as NaN, if any found.
        """
        initial_na_amount = np_sum(literal_series.isna())

        # find the values where literal pattern is matched
        literal_na_mask = literal_series.astype("string").str.fullmatch(
            literal_na_pattern,
            na=True,  # handle na values as match
        )

        na_matched_amount = np_sum(literal_na_mask) - initial_na_amount
        if na_matched_amount:
            logger.info(
                f"В текстовой колонке '{literal_series.name}' "
                f"дополнительно найдено {na_matched_amount} пропущенных значений"
            )

        return literal_series.mask(
            literal_na_mask,
            other=nan,
        )  # replace matched with nan

    logger.info("Определяем пропуски в текстовых данных...")
    # regex patterns for various missing value representations
    na_options = [
        rf"\s*{option}\s*"  # ignore any spaces
        for option in (
            "<?na[nt]?>?",
            r"n\/a",
            "none",
            "null",
            "<?unknown>?",
            r"\-+",
            "—+",
            r"\.+",
            "",
        )  # a few na forms, hyphen/dash/dot or bare spaces, and even empty string
    ]
    # assemble with 'or' condition and compile regex patterns of `na_options`
    literal_na_pattern = compile_regex(f"({')|('.join(na_options)})", IGNORECASE)

    # replace various representations with NaN, for selected dtypes
    literal_data = data.select_dtypes(dtypes)
    literal_data = _apply_wrapper(literal_data)(set_missing_as_nan, axis=0, literal_na_pattern=literal_na_pattern)

    # reset operated columns in the original data
    data.loc[:, literal_data.columns] = literal_data[:]


def _drop_incomplete_rows(data: DataFrame, viable_columns: Iterable[str | None]) -> None:
    """
    Drops rows having na values in viable_columns.

    Parameters
    ----------
    data : DataFrame
        The data with potential missing values in viable columns
    viable_columns : Iterable[str]
        Selected column names, where missing values are inappropriate
    """
    # create a boolean mask to identify rows with missing values in viable_columns
    na_mask = zeros(len(data), dtype=bool)

    for column in filter(None, viable_columns):
        column_isna = data[column].isna()

        if np_sum(column_isna):
            # log a message if there are missing values in the column
            logger.warning(
                f"В критичной для process mining колонке '{column}' "
                f"найдено {np_sum(column_isna)} пустых значений, строки с пропусками будут удалены"
            )
        na_mask = na_mask | column_isna

    # drop rows with missing values
    data.drop(data.index[na_mask], axis=0, inplace=True)


class DataEditor:
    SYNTHETIC_DURATION_NAMES = ("col_start_time", "col_end_time", "col_duration")
    SYNTHETIC_SUCCESS_NAME = "col_case_success"

    data: DataFrame
    holder_columns: HolderColumns

    __slots__ = __annotations__

    def setup(self, data, holder_columns) -> None:
        self.data = data
        # ! final data holder might has more or less columns, depends on UNSTEADY_COLUMNS
        self.holder_columns = holder_columns

        _unify_missing_values(self.data)
        _drop_incomplete_rows(
            self.data,
            viable_columns=(getattr(holder_columns, "case", None), getattr(holder_columns, "stage", None)),
        )

    def adjust_data_types(self) -> None:
        """
        Adjusts the data types of the given data frame to reduce memory consumption.

        Following data types are possible after all:
        - string
        - number
        - datetime
        - bool
        - category

        Parameters
        ----------
        data : pandas.DataFrame
            The data obtained through DataHolder initialization.
        """
        logger.info("Производится оптимизация типов данных...")
        DTypeManager(self.data).adjust_data_types()

    def adjust_datetime(self, **kwargs: Iterable[str] | str | bool | TimeErrors):
        """
        Adjust the data present in datetime_columns.

        Confirm that the data values are of datetime data type or convert to the same.
        """
        DateTimeManager(
            datetime_columns=[
                column for column in kwargs["datetime_columns"] if not isinstance(column, SyntheticColumns)
            ],
            time_format=kwargs["time_format"],
            dayfirst=kwargs["dayfirst"],
            yearfirst=kwargs["yearfirst"],
            utc=kwargs["utc"],
        ).adjust_datetime(self.data, kwargs["time_errors"])

    def adjust_stages_duration(
        self, holder: DataHolder, duration_unit: DurationUnits, duration_errors: TimeErrors
    ) -> None:
        """
        Adjust the stages duration
            1. guarantee the duration values are numeric
            2. multiply the duration values with the duration unit value

        TODO Raises...
        """
        DurationManager(
            self.data, holder, duration_unit=duration_unit, duration_errors=duration_errors
        ).adjust_stages_duration(self.data, self.holder_columns.duration)

        DurationManager.log_incorrect_durations(self.data[self.holder_columns.duration], synthetic=False)

    def adjust_case_success(self):
        """
        Adjust the case success data of the event log.
            1. guarantee values indicating success are boolean,
                whereas missing values are replaced with False
            2. confirm success values are definitive (True/False) for each case ID
        Ensure the data holder case ID data for corresponding success.

        TODO Raises...
        """
        SuccessManager.verify_has_case_id(self.holder_columns)
        self.data[self.holder_columns.case_success] = SuccessManager.adjust_case_success(
            self.data[self.holder_columns.case_success],
            self.data[self.holder_columns.case],
        )

    def calculate_duration(self, holder: DataHolder) -> None:
        """
        Calculate duration of the event data operations and update the data holder. Synthetic column
        names will be set / wiped from the data holder event data, based on the errors in duration
        calculations. User will be notified about any incorrect durations found.

        Parameters
        ----------
        holder : DataHolder
            The data holder instance it currently processes.

        Raises
        ------
        RuntimeError
            # TODO message
            If an error occurs while calculating the duration.
        """
        try:
            DurationManager(data=self.data, data_holder=holder).calculate_duration(
                self.data, self.holder_columns.duration
            )
        except RuntimeError as err:
            logger.error(f"calculate duration error: {err}")  # TODO exception

            for column_attribute in self.SYNTHETIC_DURATION_NAMES:
                column_name = getattr(holder, column_attribute)

                if isinstance(column_name, SyntheticColumns):
                    # wipe synthetic column names from the data holder
                    object.__delattr__(holder, column_attribute)
        else:
            logger.info(f"Рассчитаны длительности операций - см. колонку {self.holder_columns.duration}")
            DurationManager.log_incorrect_durations(self.data[self.holder_columns.duration], synthetic=True)

    def indicate_case_success(self, holder: DataHolder, success_inputs: SuccessInputs) -> None:
        """
        Add an indicator column of case ID success to the holder event log.
        Handle `success_inputs` argument, verify user inputs are correct,
            cancel success indication if no inputs provided.
        Under the circumstances of any errors in `success_inputs`, case success calculations,
            1. notify about the errors in success inputs entries
            2. wipe the indicator column (`SYNTHETIC_SUCCESS_NAME`) attribute from the data holder
        Given no errors and indication result, log a message with computed case ID success ratio.

        Parameters
        ----------
        holder : DataHolder
            The data holder instance it currently processes.
        success_inputs : SuccessInputs
            The successful entry inputs for the holder case ID success.
        """
        # check if success_inputs isn't set - empty by default
        # or col_case_success is set as None
        if not any(success_inputs) or not hasattr(self.holder_columns, "case_success"):
            # do not delete as parameter simply was skipped, were no errors
            object.__setattr__(holder, self.SYNTHETIC_SUCCESS_NAME, None)
            return

        try:
            SuccessManager.verify_has_case_id(self.holder_columns)
            # success_inputs.column can be empty - use col_stage by default
            SuccessManager(
                SuccessManager.guarantee_column_of_entries(success_inputs, self.holder_columns)
            ).indicate_case_success(
                self.data,
                self.holder_columns.case,
                self.holder_columns.case_success,
            )
        except (AttributeError, ValueError) as err:
            logger.error(err)
            # wipe synthetic 'case success' column from the data holder
            object.__delattr__(holder, self.SYNTHETIC_SUCCESS_NAME)
        else:
            SuccessManager._guarantee_holder_success_column(
                holder, self.SYNTHETIC_SUCCESS_NAME, self.holder_columns.case_success
            )

            success_ratio = SuccessManager.compute_case_success_ratio(
                self.data, self.holder_columns.case, self.holder_columns.case_success
            )
            logger.info(
                f"Определены успешные процессы ({success_ratio:.3%}) "
                f"по параметру `success_inputs` - см. колонку {self.holder_columns.case_success}"
            )

    def skip_calendar_days(
        self, skip_weekends: bool, skip_holidays_list: Iterable[str], datetime_columns: Iterable[str]
    ) -> None:
        """
        Adjust the calendar days - skip ones based on certain user-provided conditions:
            1. If to skip weekends
            2. If there are any holidays

        Parameters
        ----------
        skip_weekends : bool
            Whether or not to skip weekends.
        skip_holidays_list : Iterable[str]
            List representation of holidays to skip.
        datetime_columns : Iterable[str]
            Column names corresponding to real datetime columns in the event data.
        """
        if skip_weekends or skip_holidays_list:
            logger.info("Данные будут отфильтрованы по параметрам `skip_weekends` и `skip_holidays_list`")

        # Both times are missing
        if not any(datetime_columns):
            # TODO logger if skip_weekends or skip_holidays_list
            return

        actual_data_size = len(self.data)

        manager = CalendarManager(
            skip_weekends,
            CalendarManager.parse_provided_holidays(skip_holidays_list),
        )
        manager.skip_calendar_days(self.data, datetime_columns)
        manager.log_skipped_calendar(actual_data_size)

    def sort_event_data(self) -> None:
        """
        Sorts the data in `DataHolder` instance based on the given sorting columns.

        If no datetime columns are given, applies case-stage sorting.
        On top of that, if no case id column is given, it raises an exception.

        Raises
        ------
        LogWithoutTimestampError
            If no case id and datetime columns are given (stages only).
        """
        manager = SortingManager(self.holder_columns, self.data)

        logger.info(f"Данные будут отсортированы по следующим колонкам: {manager.columns_to_sort}")
        manager.sort_event_data(self.data)
