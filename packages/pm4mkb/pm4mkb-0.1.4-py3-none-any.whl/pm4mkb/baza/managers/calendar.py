from __future__ import annotations
from collections import deque
from typing import TYPE_CHECKING, Iterable

from dateparser import parse as date_parse
from loguru import logger

from pandas import date_range


if TYPE_CHECKING:
    from pandas import DataFrame, Series
    from pm4mkb.baza import DateTime


class CalendarManager:
    DATE_RANGE_SEP = "-"
    DAY_MONTH_SEP = "/"
    HOLIDAY_FORMAT = "%d/%m"

    WEEKDAY_MIN = 0  # stands for Monday
    WEEKDAY_MAX = 4  # stands for Friday

    skip_weekends: bool
    holidays_list: Iterable[str]

    _weekend_excluded: int
    _holiday_excluded: int

    __slots__ = __annotations__

    def __init__(self, skip_weekends, skip_holidays_list) -> None:
        self.skip_weekends = skip_weekends
        self.holidays_list = skip_holidays_list
        self._weekend_excluded, self._holiday_excluded = 0, 0

    def skip_calendar_days(self, data: DataFrame, datetime_columns: Iterable[str]) -> None:
        """
        Adjusts the provided data in-place by:
            1. excluding weekends from records
            2. excluding 'holidays' - the user-specified list of month calendar days

        Skips the afore mentioned records in the specified columns and removes it from the data.

        Parameters
        ----------
        data : pandas.DataFrame
            A pandas DataFrame with calendar data to be excluded.
        datetime_columns : Iterable[str]
            An iterable of column names corresponding to datetime columns in the provided DataFrame.
        """
        for timestamp_column in datetime_columns:
            if self.skip_weekends:
                self._exclude_weekends(data, timestamp_column)
            if self.holidays_list:
                self._exclude_user_holidays(data, timestamp_column)

    def log_skipped_calendar(self, full_calendar_size: int) -> None:
        """
        Log skipped calendar operations. Write messages both for:

            - excluded weekends
            - excluded holidays

        Parameters
        ----------
        full_calendar_size : int
            The size of the raw data.
        """
        message = "Удалено {} операций в {} дни"

        if self._weekend_excluded:
            logger.info(
                message.format(
                    f"{self._weekend_excluded} ({self._weekend_excluded / full_calendar_size:.3%})", "выходные"
                )
            )
        if self._holiday_excluded:
            logger.info(
                message.format(
                    f"{self._holiday_excluded} ({self._holiday_excluded / full_calendar_size:.3%})",
                    "указанные праздничные",
                )
            )

    def _exclude_weekends(self, data: DataFrame, timestamp_column: str) -> None:
        """
        Modifies the data in-place, removing any records that occurred in the timestamp column
        between WEEKDAY_MIN and WEEKDAY_MAX, currently on weekends (Saturday or Sunday).

        Parameters:
        -----------
        data : pandas.DataFrame
            The DataFrame to filter.
        timestamp_column : str
            The name of the DataFrame column containing timestamps.
        """
        # * able to use `.dt`: the datetime data was already parsed in data holder preprocessing
        weekend_mask = ~data[timestamp_column].dt.weekday.between(self.WEEKDAY_MIN, self.WEEKDAY_MAX)
        self._weekend_excluded += len(data[weekend_mask])
        # drop stages on weekends, keep workdays
        data.drop(data[weekend_mask].index, inplace=True)

    def _exclude_user_holidays(self, data: DataFrame, timestamp_column: str) -> None:
        """
        Modifies the data in-place, removing records that occur on any of the user-defined holidays.
        What records are 'holidays' is based on intersections of day-month bundles in the
        `timestamp_column` and the `holidays_list`.

        Parameters
        ----------
        data : pandas.DataFrame
            A pandas DataFrame containing the data to be filtered.
        timestamp_column : str
            The name of the column containing the timestamps to be filtered.
        """

        def get_days_as_string(datetime_series: Series[DateTime]) -> Series[str]:
            return datetime_series.dt.day.astype("string").str.rjust(width=2, fillchar="0")

        def get_months_as_string(datetime_series: Series[DateTime]) -> Series[str]:
            return datetime_series.dt.month.astype("string").str.rjust(width=2, fillchar="0")

        def construct_series_of_day_month(datetime_series: Series[DateTime]) -> Series[str]:
            return get_days_as_string(datetime_series).str.cat(
                get_months_as_string(datetime_series), sep=self.DAY_MONTH_SEP
            )

        # * able to use `.dt`: the datetime data was already parsed in data holder preprocessing
        holiday_mask = construct_series_of_day_month(data[timestamp_column]).isin(self.holidays_list)
        self._holiday_excluded += len(data[holiday_mask])
        # drop stages on holidays (day-month bundles known from holidays_list)
        data.drop(data[holiday_mask].index, inplace=True)

    @classmethod
    def parse_provided_holidays(cls, days_list: Iterable[str]) -> deque[str]:
        """
        Parses the provided list of holidays and returns a deque of actual day-month records.

        Parameters
        ----------
        days_list : Iterable[str]
            User-defined strings representing holidays of calendar year.

        Returns
        -------
        deque[str]
            A deque of formatted holidays from the provided list, e. g. 01/05, 01/06, 02/06, 08/03.
        """
        all_holidays: deque[str] = deque()

        for holiday in map(lambda date: date.strip(), days_list):
            parsed_holidays: str | Iterable[str] = cls._parse_day_month(holiday)  # type: ignore[assignment]

            if isinstance(parsed_holidays, str):
                all_holidays.append(parsed_holidays)
            else:
                all_holidays.extend(parsed_holidays)

        if all_holidays:
            logger.info(f"Сформирован список из {len(all_holidays)} праздничных дней (в году)")

        return all_holidays

    @classmethod
    def _parse_day_month(cls, date: str) -> str | Iterable[str] | None:
        if cls.DATE_RANGE_SEP in date:
            # get sequence from day range
            return cls._extract_days_range(date)

        try:
            # get a single day
            return date_parse(date).strftime(cls.HOLIDAY_FORMAT)
        except AttributeError as err:  # date_parse returned None
            logger.error(f"Проверьте формат следующей даты в `skip_holidays_list`: {date}.\n")
            raise ValueError("Праздничный день не распознан") from err  # TODO custom exception

    @classmethod
    def _extract_days_range(cls, day_range: str) -> list[str] | None:
        try:
            start, end = map(date_parse, day_range.split(cls.DATE_RANGE_SEP))

            day_sequence = [
                *map(lambda date: date.strftime(cls.HOLIDAY_FORMAT), date_range(start, end, freq="1D"))
            ]
            assert day_sequence, "Пустой диапазон дат - проверьте порядок дней"

            return day_sequence
        except (AssertionError, NameError, ValueError) as err:
            logger.error(
                f"Проверьте правильность заполнения следующего интервала для `skip_holidays_list`: {day_range}.\n"
                "Список праздничных дней не сформирован"
            )

            raise ValueError("Список праздничных дней не сформирован") from err  # TODO custom exception
