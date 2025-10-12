from __future__ import annotations
from contextlib import suppress
from datetime import datetime
from itertools import product
from re import findall
from typing import TYPE_CHECKING, Iterable

from loguru import logger

from numpy import sum as np_sum
from pandas import Series, to_datetime
from pandas.api.types import is_datetime64_any_dtype

from pm4mkb.baza import TimeErrors, string_datetime_parser, verify_in_enum


if TYPE_CHECKING:
    from pandas import DataFrame
    from pm4mkb.baza import DateTime


class DateTimeManager:
    datetime_columns: Iterable[str]
    time_format: str | None
    dayfirst: bool
    yearfirst: bool
    utc: bool

    _converted_timestamps: Series

    __slots__ = __annotations__

    def __init__(self, **kwargs):
        """
        Initialize a manager to adjust given datetime columns. To cast data types, format datetime
        and process errors.

        Parameters
        ----------
        datetime_columns : Iterable[str]
            Iterable of strings, representing column names that contain datetime data.
        time_format : Optional[str]
            Optional string representing the demanded time format for the datetime strings.
        dayfirst : bool
            If to parse dates with the day first order.
        yearfirst : bool
            If to parse dates with the year first order.
        utc : bool
            If UTC time localization is required.
        """
        self._converted_timestamps = Series()

        for name, argument in kwargs.items():
            setattr(self, name, argument)

    def adjust_datetime(
        self,
        data: DataFrame,
        time_errors: TimeErrors,
    ) -> None:
        """
        Convert data of specified datetime columns in a given DataFrame to the `time_format`. Cast
        to datetime, if needed.

        Parameters
        ----------
        data : pandas.DataFrame
            Dataframe containing datetime columns to adjust.
        time_errors : TimeErrors
            A TimeErrors enum object indicating how date-time conversion errors will be handled.
        """
        verify_in_enum(time_errors, TimeErrors)

        if self.time_format is None and any(self.datetime_columns):
            self.__log_unknown_time_format()

        # Ensure each time column is in datetime format
        for time_column in self.datetime_columns:
            # Skip datetime cast if is already a datetime
            if is_datetime64_any_dtype(data[time_column]):
                # Format to self.time_format datetime
                data[time_column] = self._format_timestamp(data[time_column])
                continue

            # Convert with specified options or automatically
            if time_errors == TimeErrors.AUTO_CONVERT:
                self._auto_cast_to_datetime(
                    data[time_column],
                )
            else:
                self._converted_timestamps = self._cast_to_datetime(
                    data[time_column],
                    format=self.time_format,
                    errors=time_errors,  # raise or coerce
                )

            data[time_column] = self._converted_timestamps

    def _format_timestamp(self, timestamp_series: Series[DateTime]) -> Series[DateTime]:
        """
        Format a given timestamp series with the `self.time_format`.

        Parameters
        ----------
        timestamp_series : Series
            The timestamp series to be formatted.

        Returns
        -------
        Series
            The formatted timestamp series.

        Raises
        ------
        ValueError
            If the series cannot be casted to the
            original timestamp dtype and the format is invalid.
        """
        if self.time_format:
            timestamp_dtype = timestamp_series.dtype
            not_nat_mask = ~timestamp_series.isna()

            timestamp_series = timestamp_series.mask(
                not_nat_mask,
                other=timestamp_series[not_nat_mask].apply(
                    datetime.strftime,
                    format=self.time_format,
                ),
            )

            try:
                timestamp_series = timestamp_series.astype(timestamp_dtype)
            except ValueError as err:
                # Possible reason - single number time format like %m
                raise ValueError("Wrong time format") from err  # TODO custom exception

        return timestamp_series

    def _cast_to_datetime(
        self, datetime_column: Series, **kwargs: str | None | TimeErrors | bool
    ) -> Series[DateTime]:
        """
        Casts a given pandas Series of string datetime-like values to datetime.
        If `time_errors` is set as 'raise' and datetime cast has failed,
            seek for an adequate `dayfirst` `yearfirst` combination.

        Parameters
        ----------
        datetime_column : Series
            A pandas Series of datetime-like values.

        **kwargs
            Additional keyword arguments to pass to the `to_datetime` function.
                format, time_errors, utc

        Returns
        -------
        Series
            A pandas Series of datetime values.
        """
        # keep capability to drop timezone with time format
        if kwargs.get("utc") is None:
            kwargs["utc"] = self.utc

        # Try to convert timestamps to datetime
        try:
            return to_datetime(
                datetime_column,
                dayfirst=self.dayfirst,
                yearfirst=self.yearfirst,
                **kwargs,
            )
        except ValueError as err:
            (full_message,) = err.args

            quote = r"\""
            failed_record, datetime_format = findall(f"{quote}[^{quote}]+{quote}", full_message)

            logger.info(
                f"В колонке '{datetime_column.name}' не получилось преобразовать "
                f"строку {failed_record} к формату {datetime_format}\n"
                "Это может быть связано с неправильным выбором параметров `dayfirst`, `yearfirst`. "
                "Ищем эти параметры..."
            )

        casted_datetime = None
        for dayfirst, yearfirst in product((False, True), repeat=2):
            with suppress(ValueError):
                casted_datetime = to_datetime(
                    datetime_column,
                    dayfirst=dayfirst,
                    yearfirst=yearfirst,
                    **kwargs,
                )

            if is_datetime64_any_dtype(casted_datetime):
                logger.info(f"Были применены {dayfirst = }, {yearfirst = }")

                self.dayfirst = dayfirst
                self.yearfirst = yearfirst

                return casted_datetime

        logger.error("Ни одна комбинация параметров не сработала.")
        # TODO custom exception
        raise ValueError(
            f"В колонке '{datetime_column.name}' не получилось преобразовать "
            f"строку {failed_record} к формату {datetime_format}\n"
        )

    def _auto_cast_to_datetime(self, datetime_series: Series) -> None:
        """
        Try to automatically cast (to datetime) a pandas Series of various datetime format strings.

        Parameters
        ----------
        datetime_series : Series
            The Series of datetime strings to convert.
        """
        # * _converted_timestamps series's going to mutate a few times
        self._converted_timestamps = self._cast_to_datetime(
            datetime_series,
            errors=TimeErrors.COERCE,  # cast as much as possible
        )

        # Find erroneous timestamps
        # ! nan can be present in log, before to_datetime
        nat_mask = self._converted_timestamps.isna()
        self.__parse_erroneous_timestamps(datetime_series, nat_mask)

        remaining_nat_mask = self._converted_timestamps.isna()
        self.__format_converted_timestamps(remaining_nat_mask)

        if remaining_nat_mask.any():
            # Log any remaining erroneous timestamps
            self._log_invalid_datetimes(datetime_series, remaining_nat_mask)
        if self._converted_timestamps.any():
            # Notify about successfully converted erroneous timestamps
            self.__log_datetime_conversions(
                datetime_series,
                nat_mask ^ remaining_nat_mask,  # logical xor na mask
            )

        self._converted_timestamps = self._cast_to_datetime(
            self._converted_timestamps,
            format=self.time_format,
            errors=TimeErrors.COERCE,  # cast strftime formatted with optional na values
            utc=False,  # timezone is formatted already
        )

    def __parse_erroneous_timestamps(self, datetime_series: Series, nat_mask: Series[bool]) -> None:
        """
        Find and convert erroneous timestamps (which failed to convert with `_cast_to_datetime`) in
        a Series of datetime strings. Converts to pandas Timestamp.

        Parameters
        ----------
        datetime_series : pandas.Series
            The Series of datetime strings to convert.
        nat_mask : Series[bool]
            A pandas Series representing which values are NaT.
        """
        erroneous_timestamps = datetime_series[nat_mask]

        if erroneous_timestamps.any():
            # Determine whether to parallelize string parsing
            parallel_records_threshold = 1000
            parallelize = np_sum(nat_mask) > parallel_records_threshold

            # Parse erroneous timestamps as strings and convert to datetime
            parsed_erroneous = string_datetime_parser(erroneous_timestamps, self.utc, parallel=parallelize)
            self._converted_timestamps[nat_mask] = parsed_erroneous

    def __format_converted_timestamps(self, remaining_nat_mask: Series[bool]) -> None:
        """
        Formats timestamps in the given datetime Series, successfully converted to pandas Timestamp
        on the previous step.

        Parameters
        ----------
        remaining_nat_mask : Series[bool]
            A pandas Series representing which values are NaT.
        """
        # Set converted erroneous timestamps with main time_format
        formatted_timestamp_series = self._converted_timestamps[~remaining_nat_mask].apply(
            datetime.strftime,
            format=self.time_format,
        )
        # Replace the pandas timestamps in self._converted_timestamps with formatted ones,
        # have to temporarily change dtype for the original series
        self._converted_timestamps = self._converted_timestamps.astype("object")
        self._converted_timestamps[~remaining_nat_mask] = formatted_timestamp_series

    def __log_unknown_time_format(self) -> None:
        """
        Logs a warning message indicating that the timestamp format will be auto-detected.

        Parameters
        ----------
        dayfirst : bool
            indicator, whether day should be parsed first.
        yearfirst : bool
            indicator, whether year should be parsed first.
        """
        logger.warning(
            "Не задан параметр 'time_format' для DataHolder.\n"
            "Рекомендуется указать общий формат времени для корректного парсинга данных, "
            "например, time_format='%d-%m-%Y %H:%M:%S'.\n"
            "Подробнее о допустимых форматах на "
            "https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes"
        )
        logger.warning(
            "Будет произведена попытка подобрать формат времени автоматически.\n"
            "C учетом параметров DataHolder: "
            f"dayfirst = {self.dayfirst}, yearfirst = {self.yearfirst}.",
        )

    def __log_datetime_conversions(self, datetime_column: Series, nat_mask: Series[bool]) -> None:
        """
        Logs successful datetime conversions for a given datetime_column, as well as the original
        string values of datetime.

        Parameters
        ----------
        datetime_column : Series
            A pandas Series containing datetime values.
        nat_mask : Series[bool]
            A pandas Series representing which values were NaT after `_cast_to_datetime`,
                but then converted with help of `string_datetime_parser`.
        """
        logger.info(
            (
                "Пожалуйста, проверьте, "
                "что следующие данные были правильно преобразованы "
                f"в режиме 'auto_convert' к формату '{self.time_format}'\n"
                "Изначальные временные метки:\n"
                f"{datetime_column[nat_mask].to_list()}\n"
                "Преобразованные к формату datetime:\n"
                f"{self._converted_timestamps[nat_mask].to_list()}"
            )
        )

    @staticmethod
    def _log_invalid_datetimes(datetime_column: Series, remaining_nat_mask: Series[bool]) -> None:
        """
        Logs a warning message for datetime values that have been failed to convert.

        Parameters
        ----------
        datetime_column : Series
            A pandas Series with partially converted datetime values.
        remaining_nat_mask : Series[bool]
            A pandas Series representing which values are NaT.
        """
        logger.warning(
            (
                "Не получилось определить формат с опцией 'auto_convert' "
                "для следующих временных меток:\n"
                f"{datetime_column[remaining_nat_mask].to_list()}\n"
                "Они заменены в данных на nan"
            )
        )
