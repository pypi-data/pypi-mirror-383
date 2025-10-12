from __future__ import annotations
from enum import Enum
from itertools import repeat
from typing import TYPE_CHECKING

from loguru import logger

from numpy import isnan, sum as np_sum
from pandas import Timedelta, to_numeric, to_timedelta
from pandas.api.types import is_numeric_dtype

from pm4mkb.baza import DurationUnits, SyntheticColumns, TimeErrors, verify_in_enum


if TYPE_CHECKING:
    from pandas import DataFrame, Series
    from pm4mkb.baza import DataHolder, DateTime, Duration


class ShiftOptions(int, Enum):  # TODO move utils / annotations
    START = -1
    END = 1


class DurationManager:
    TIME_COLUMNS = dict(start_time="col_start_time", end_time="col_end_time")

    unit: DurationUnits
    errors: TimeErrors

    case: Series | None
    start_time: Series[DateTime] | None
    end_time: Series[DateTime] | None

    _holder: DataHolder | None
    _start_case: Series | None
    _end_case: Series | None

    __slots__ = __annotations__

    def __init__(
        self,
        data: DataFrame,
        data_holder: DataHolder,
        duration_unit=DurationUnits.SECOND,
        duration_errors=TimeErrors.RAISE,
    ) -> None:
        """
        Initialize a manager to adjust or intentionally compute DataHolder stages duration.

        Parameters
        ----------
        duration_unit : DurationUnits
            Time unit of the considered duration data, e.g. minute, hour multiplier
        duration_errors : TimeErrors
            An option that specifies the way to handle non-numeric duration errors.
        """

        self.unit = duration_unit
        self.errors = duration_errors

        self.case, self.start_time, self.end_time = map(
            data.get,
            [data_holder.col_case, data_holder.col_start_time, data_holder.col_end_time],
        )

        self._holder = data_holder
        self._start_case, self._end_case = None, None

    def adjust_stages_duration(self, data: DataFrame, duration_column: str) -> None:
        """
        Adjust the stages duration in DataHolder event log
            1. guarantee the duration values are numeric
            2. multiply the duration values with the duration unit value
            3. compute and set a missing start time (end time) column
                if there is end time (start time) column
        """
        verify_in_enum(self.unit, DurationUnits)

        # Ensure that the duration values are numeric
        self._guarantee_numeric_duration(data, duration_column)
        # Multiply the duration values with the duration unit value
        data[duration_column] *= self.unit

        self._set_residual_time(data, duration_column)

    # TODO docstring
    def _set_residual_time(self, data: DataFrame, duration_column: str) -> None:
        residual_name = ""

        if self._holder._has_start_time and not self._holder._has_end_time:
            residual_name, accessible_series = "end_time", self.start_time
            timedelta_sign = +1
        elif self._holder._has_end_time and not self._holder._has_start_time:
            residual_name, accessible_series = "start_time", self.end_time
            timedelta_sign = -1

        if residual_name:
            data[
                SyntheticColumns.__members__[residual_name.upper()]
            ] = accessible_series + timedelta_sign * to_timedelta(
                data[duration_column], errors=self.errors, unit="second"
            )

            self._guarantee_holder_time_columns(self._holder, residual_name)
            logger.info(
                f"Данные для колонки `{self.TIME_COLUMNS[residual_name]}` были рассчитаны на основе "
                f"данных из `{duration_column}` и `{accessible_series.name}`.\n"
                f"Параметр `DataHolder` `time_format` не применяется к рассчитанному столбцу."
            )

    def calculate_duration(self, data: DataFrame, duration_column: str) -> None:
        """
        Calculates numeric duration in seconds between start and end times for different scenarios
        in the data.

        Scenarios: has both times / start / end / none. In detail:
            1. start time or end time columns are missing - raises a RuntimeError
            2. has both start and end timestamps - calculates duration just by their difference.
            3. only one of the columns is missing (start or end) -
                calculates the missing column by shifting next or previous rows.
                Finally calculates the duration heuristically by next - previous row difference.
                If the case ID changes over two different rows, sets the duration to None.
        """
        times_missing = self.start_time is None or self.end_time is None

        # Skip if both start and end times are present,
        # and immediately calculate duration by their difference
        if times_missing:
            self.__validate_columns()
            # calculate and set approximate time data for missing column
            self.__set_missing_time(data)

        # Calculate duration as the difference between start and end times
        # divide Timedelta by Timedelta unit to cast to numpy number
        self.start_time: Series[DateTime]
        self.end_time: Series[DateTime]
        data[duration_column] = (self.end_time - self.start_time) / Timedelta(seconds=1)  # cast to number

        if times_missing:
            self.__handle_terminal_stages(data, duration_column)

    def _guarantee_numeric_duration(self, data: DataFrame, duration_column: str) -> None:
        """
        Ensure that the data in the specified duration column is of numeric type.

        If it is not, try to convert to numeric type according to the duration_errors parameter.
        """
        # if duration_errors is AUTO_CONVERT, change to COERCE and warn
        if self.errors == TimeErrors.AUTO_CONVERT:
            logger.warning(
                f"Найдены данные для col_duration = {duration_column}, "
                f"при этом параметр time_errors задан как {self.errors}.\n"
                f"Параметр time_errors для проверки 'duration' будет использован как {TimeErrors.COERCE}. "
            )
            self.errors = TimeErrors.COERCE  # type: ignore[assignment]

        # convert duration data to numeric, check if needed
        if not is_numeric_dtype(data[duration_column]):
            try:
                # convert data to numeric
                data[duration_column] = to_numeric(data[duration_column], errors=self.errors)
            except ValueError as err:  # catches error when TimeErrors.RAISE
                raise ValueError(
                    f"В данных для col_duration = {duration_column} произошли ошибки"
                    "при конвертации к числовому типу"
                ) from err  # TODO custom exception

    def __validate_columns(self):
        """
        Validates the columns required to calculate duration with a single timestamp.

        Raises:
        ------
        RuntimeError
            If both DataHolder `col_start_time` and `col_end_time` are None.
            If `col_start_time` or `col_end_time` exist, still there is no case ID to reference.
        """
        # Both times are missing
        if all(map(isinstance, self._holder.timestamp_columns, repeat(SyntheticColumns))):
            raise RuntimeError(  # TODO custom exception, not runtime
                ('Cannot calculate time difference, because both "col_start_time" and "col_end_time" are None.')
            )

        # One time is present, no case ID to reference
        if self._holder.col_case is None:
            raise RuntimeError(("Forgot case ID"))  # TODO custom exception, not runtime

    def __set_missing_time(self, data: DataFrame) -> None:
        # If one of the start or end times is missing,
        # calculate the missing time by shifting next or previous original rows
        if self.start_time is None:
            self._start_case, self.start_time = self._mock_missing_time_data(
                self.case,
                self.end_time,
                ShiftOptions.END,
            )
            self._end_case = self.case

            data[SyntheticColumns.START_TIME] = self.start_time
            self._guarantee_holder_time_columns(self._holder, "start_time")
        elif self.end_time is None:
            self._end_case, self.end_time = self._mock_missing_time_data(
                self.case,
                self.start_time,
                ShiftOptions.START,
            )
            self._start_case = self.case

            data[SyntheticColumns.END_TIME] = self.end_time
            self._guarantee_holder_time_columns(self._holder, "end_time")

    # TODO option approximate_missing_values
    def __handle_terminal_stages(self, data: DataFrame, duration_column: str) -> None:
        """
        Handle terminal stages of case ID (unknown duration with single timestamp).

        Currently, setting the duration of the last stage to None.
        """
        case_changes_mask = self._start_case != self._end_case
        # only one time series become from shifted, take its synthetic name
        (shifted_time_name,) = data.columns.intersection((SyntheticColumns.START_TIME, SyntheticColumns.END_TIME))

        # Set the duration and shifted time data to None, when case ID changes over rows
        data.loc[case_changes_mask, [duration_column, shifted_time_name]] = None

    @classmethod
    def _guarantee_holder_time_columns(cls, data_holder: DataHolder, time_choice: str) -> None:
        """
        Ensure that `DataHolder` instance time columns are not None, if the duration was calculated
        successfully. Set synthetic names, if necessary.

        Parameters:
        -----------
        data_holder: DataHolder
            An instance of the DataHolder class.
        time_choice: ("start_time", "end_time")
            A string representing the time column option.
        """
        if getattr(data_holder, cls.TIME_COLUMNS[time_choice]) is None:
            synthetic_name = SyntheticColumns.__members__[time_choice.upper()]

            object.__setattr__(data_holder, cls.TIME_COLUMNS[time_choice], synthetic_name)
            logger.info(f"Аттрибуту DataHolder `col_{time_choice}`=None присвоено значение `{synthetic_name}`")

    @staticmethod
    def _mock_missing_time_data(
        case_data: Series, time_data: Series[DateTime], shift: ShiftOptions
    ) -> tuple[Series, Series]:
        """
        Shifts the time and case data by the given shift value.

        Parameters
        ----------
        case_data : Series
            A pandas Series containing the case data.
        time_data : Series
            A pandas Series containing the time data.
        shift : ShiftOptions
            An enum value indicating whether side and how much to shift data.

        Returns
        -------
        tuple
            A tuple containing the shifted time data and case data.
        """
        return case_data.shift(shift), time_data.shift(shift)

    @staticmethod
    def log_incorrect_durations(duration_series: Series[Duration], synthetic: bool) -> None:
        """
        Notify the user about negative durations found in a given data (event log).

        Parameters
        ----------
        duration_series : pandas.Series
            A pandas Series containing durations of the DataHolder instance.
        synthetic : bool
            A boolean indicating whether the durations were synthetically generated.
        """
        negative_quantity, missing_quantity = (
            np_sum(duration_series.values < 0),
            np_sum(isnan(duration_series.values)),
        )
        common_message = (
            "В результате расчета длительностей" if synthetic else f"В переданной колонке '{duration_series.name}'"
        )

        if negative_quantity:
            message = (
                f"обнаружено {negative_quantity} ({negative_quantity / duration_series.size:.3%}) "
                "записей с отрицательной продолжительностью"
            )
            logger.warning(f"{common_message} {message}")
        if missing_quantity:
            message = (
                "отсутствуют данные о продолжительности для "
                f"{missing_quantity} ({missing_quantity / duration_series.size:.3%}) этапов"
            )
            logger.warning(f"{common_message} {message}")
