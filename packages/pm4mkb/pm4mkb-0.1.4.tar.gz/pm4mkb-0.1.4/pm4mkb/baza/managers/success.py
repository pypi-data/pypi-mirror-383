from __future__ import annotations
from typing import TYPE_CHECKING

from distutils.util import strtobool
from loguru import logger

from numpy import all as np_all, sum as np_sum
from pandas import DataFrame, Series, concat, unique
from pandas.api.types import is_bool_dtype


if TYPE_CHECKING:
    from pm4mkb.baza import DataHolder, HolderColumns, SuccessInputs, Case, Stage


def _falsify_missing_success(success_data: Series[int | bool], missing_success_number: int) -> Series[bool]:
    """
    Replace missing success values in the success_data Series with False. Resulting success_data
    will have int dtype; Initial success_data can have as int as string dtype. Log a warning message
    showing the number of missing success values.

    Parameters
    ----------
    success_data : Series
        The user-provided data indicating case ID success.
    missing_success_number : int
        The amount of missing success values.
    """
    # log a warning message showing the number of missing success values
    logger.warning(
        (
            f"В колонке переданной как `case_success` содержится {missing_success_number} "
            f"({missing_success_number / success_data.size:.3%}) пропусков. "
            "Они будут заменены в данных на 'False'."
        )
    )

    try:
        # replace missing values with False
        return success_data.fillna(False, inplace=True)
    except TypeError:
        # Handle values presented with pdcast as pyarrow strings or int8 (needs string cast)
        # 1. Use "False" instead of False to avoid string error
        # 2. Map strtobool to unify "True", "False", "0", "1"... before binary casting
        return success_data.astype("string").fillna("False").map(strtobool)


def _cast_binary_to_bool(success_data: Series[int]) -> Series[bool]:
    """
    Casts binary success data to a boolean data type.

    Raises
    ------
    ValueError: If the success data is not binary.
    """
    # Raise an error if the data is not binary
    if not np_all(success_data.isin([0, 1])):  # "0" "1" would be casted via pdcast
        raise ValueError("Can't cast to boolean data type, success_data must be binary")  # TODO custom exception

    logger.info("Бинарные значения для `case_success` приведены к типу bool")
    return success_data.astype(bool)


def _verify_singular_success(case_data: Series[Case], success_data: Series[int | bool]) -> None:
    """
    Verifies that the success values in data do not alter within each case. All success values for a
    case have to be True or False.

    Raises
    ------
    ValueError
        If any case has both 'True' and 'False' success values.
    """
    # find case IDs with values that alter within the case
    success_number_by_case = concat([case_data, success_data], axis=1).groupby(case_data.name).nunique()
    invalid_case_number = success_number_by_case.index[success_number_by_case[success_data.name] > 1].size

    # raise an error if there are cases with both 'True' and 'False' success values
    if invalid_case_number:
        raise ValueError(
            f"В {invalid_case_number} кейс ID одновременно 'True' и 'False' значения успеха.\n"
            "Исправьте эти значения для колонки, переданной как `case_success` (либо успешный кейс, либо нет)."
        )


class SuccessManager:
    successful_entries: set[str]
    column_of_entries: str | None

    __slots__ = __annotations__

    def __init__(self, success_inputs: SuccessInputs) -> None:
        """
        Determine success indicators for case ID, based on the provided successful entries. Add case
        success indicators to the data holder data, at the `success_column`.

        Parameters
        ----------
        success_inputs : SuccessInputs
            The data holder inputs argument for case success.
        """
        if success_inputs.entries is not None:
            # ensure iterable is a non-empty set
            self.successful_entries = set(filter(None, success_inputs.entries))
        else:
            self.successful_entries = set()
        self.column_of_entries = success_inputs.column

    def indicate_case_success(
        self,
        data: DataFrame,
        case_column: str,
        success_column: str,
    ) -> None:
        """
        Indicate the success of each case ID in the data holder data. Validate the entries of
        success inputs.

        Parameters
        ----------
        data : DataFrame
            The data holder data to indicate case success
        case_column : str
            The case ID column name
        success_column : str
            The case success column name, column to store the success indicator
        """

        def search_for_success(data_to_search: DataFrame, column_of_entries: str) -> Series[bool]:
            case_data, data_of_entries = data_to_search[case_column], data_to_search[column_of_entries]
            success_indices = data_of_entries[data_of_entries.isin(self.successful_entries)].index

            return case_data.isin(case_data[success_indices])

        self.__validate_column_of_entries(case_column, data)
        self.__validate_successful_entries(data[self.column_of_entries])

        data[success_column] = search_for_success(data, self.column_of_entries)

    def __validate_column_of_entries(self, case_column: str, data: DataFrame) -> None:
        """
        Validates the provided success_inputs `column` of entries in the data holder.

        Raises
        ------
        ValueError
            If the column of entries is the case column.
            If the column of entries is not in the data.
        """
        if self.column_of_entries == case_column:
            raise ValueError("Case ID column can't be provided for success records")
        if self.column_of_entries not in data:
            # TODO custom exception
            raise ValueError(
                f"Переданная `success_inputs` `column` '{self.column_of_entries}' не найдена в данных"
            )

    def __validate_successful_entries(self, data_with_entries: Series) -> None:
        """
        Validates the entries indicating case success, from the given `data_with_entries` series.

        Parameters
        ----------
        data_with_entries : Series
            The series of `column_of_entries`, containing the data for successful entries.

        Raises
        ------
        ValueError
            If no successful entries are provided in the data holder.
        ValueError
            If any of the user-provided successful entries are not found in the data.
        ValueError
            If successful entries represent all the unique values of the `data_with_entries`.
        """
        # no successful entries are provided
        if not self.successful_entries:
            raise ValueError(
                "Вы не передали маркеры успеха для аргумента `success_inputs` `entries`.\n"
                "Необходимо выбрать значения в данных `success_inputs` `column` "
                "или среди этапов `col_stage`, если вы не выбрали колонку."
            )
        # any of the successful entries are not found in the data
        if any(entry not in data_with_entries.values for entry in self.successful_entries):
            raise ValueError(
                "Следующие маркеры успеха из `success_inputs` `entries` не найдены в данных: "
                f"{self.successful_entries.difference(unique(data_with_entries))}.\n"
                "Проверьте их наличие в колонке данных, правописание / лишние пробелы."
            )
        # all the data unique values are in successful entries
        if len(self.successful_entries) == len(unique(data_with_entries)):
            raise ValueError(
                "Вы передали в качестве `entries` все уникальные значения из `success_inputs` `column`:\n"
                f"'{self.successful_entries}'. Выберите лишь несколько примеров успеха."
            )

    @staticmethod
    def adjust_case_success(success_data: Series[int | bool], case_data: Series[Case]) -> Series[bool]:
        """
        Verify and adjust the user-provided case success data. Guarantee the boolean case success
        data for the data holder.

        Parameters
        ----------
        success_data : Series
            The user-provided data indicating case ID success.
        case_data : Series
            The data representing case ID.
        """
        missing_success_number = np_sum(success_data.isna())

        if missing_success_number:
            success_data = _falsify_missing_success(success_data, missing_success_number)
        _verify_singular_success(case_data, success_data)

        return success_data if is_bool_dtype(success_data) else _cast_binary_to_bool(success_data)

    @staticmethod
    def guarantee_column_of_entries(
        success_inputs: SuccessInputs, holder_columns: HolderColumns
    ) -> SuccessInputs | None:
        """
        Check if the user-provided success inputs has a 'column' attribute. If not, set a default
        column of stages as the 'success_inputs' column.

        Parameters
        ----------
        success_inputs : SuccessInputs
            The data holder inputs argument for case success.
        holder_columns : HolderColumns
            The named tuple representing available data holder columns.

        Raises
        ------
        AttributeError
            If default 'stage' is not present among the data holder columns.
        """
        if success_inputs.column is None:
            try:
                holder_columns.stage
            except AttributeError as err:
                raise AttributeError(
                    "Stage column is required for success records as long as no success column passed"
                ) from err

            return success_inputs._replace(column=holder_columns.stage)

        return success_inputs

    @staticmethod
    def verify_has_case_id(holder_columns: HolderColumns) -> None:
        """
        Verify if the data holder columns have 'case ID' name.

        Parameters
        ----------
        holder_columns : HolderColumns
            The named tuple representing available data holder columns.

        Raises
        ------
        AttributeError
            If 'case ID' is not present among the data holder columns.
        """
        try:
            holder_columns.case
        except AttributeError as err:
            # TODO custom message
            raise AttributeError("Case column is required to compute success records") from err

    @staticmethod
    def _guarantee_holder_success_column(
        data_holder: DataHolder,
        success_column_attribute: str,
        success_column_name: str,
    ) -> None:
        """
        Ensure that after the case success has been computed via `indicate_case_success` method,
            the `DataHolder` instance case success column is not None.

        Parameters:
        -----------
        data_holder: DataHolder
            An instance of the DataHolder class.
        success_column_attribute: str
            The name of the success attribute in DataHolder class
        success_column_name: str
            The name of the column for the success attribute.
            Would be synthetic if not set by user.
        """
        if getattr(data_holder, success_column_attribute) is None:
            logger.info(
                f"Аттрибуту DataHolder `{success_column_attribute}`=None "
                f"присвоено значение `{success_column_name}`"
            )
            object.__setattr__(data_holder, success_column_attribute, success_column_name)

    @staticmethod
    def compute_case_success_ratio(
        data: DataFrame,
        case_column: str,
        success_column: str,
    ) -> float:
        """
        Compute the success ratio of cases in the data holder, when success data is obtained by
        calling `indicate_case_success`.

        Returns
        -------
        float
            The success ratio in the the data holder data,
            the number of successful cases divided by the total number of cases.
        """
        case_data = data[case_column]

        # compute counts of total and successful cases
        case_count, successful_case_count = (
            case_data.nunique(),
            case_data[data[success_column]].nunique(),  # boolean success mask
        )

        return successful_case_count / case_count

    # TODO later, not case specific
    # success stage as well as success case
    @staticmethod
    def guarantee_success_activity(
        success_activity: Stage, holder: DataFrame, col_case: str, col_stage: str
    ) -> Stage:
        """
        If success_activity is None, then identify the successful stage as the most frequent last
        stage in the col_case instances.
        """
        if success_activity is None:
            return (holder.data.groupby(col_case)[col_stage].last().mode())[0]
        elif isinstance(success_activity, (str, int, float)):
            return success_activity
        else:
            raise ValueError(f"success_activity must be str, int or float, not {type(success_activity)}")
