from __future__ import annotations
from datetime import datetime
from enum import Enum
from re import search
from typing import TYPE_CHECKING, Callable

from dateparser import parse

from pandarallel import pandarallel
from pandas import DataFrame, Series, Timestamp, concat, to_datetime


if TYPE_CHECKING:
    from numpy import datetime64


COLON = ":"  # colon is used as a sort of universal datetime delimiter
# dateparser has difficulties recognizing time H:M:S with other delimiters
# still it is able to recognize date like %Y:%m:%d
REGEX_STEPS = {
    r"\s+": COLON,  # replace any spaces
    r"(a|p)(?=\.?m)(\.?m\.?)": r"\1m",  # replace a.m. or p.m. with am / pm (if found)
    r"(?!am|pm)[^\d+](?<!am|pm)": COLON,  # replace everything but digits, tz '+' and am / pm
    r":+": COLON,  # replace multiple colon with single ones
    r"^:|:$": "",  # rm colon at the begging and the end
}


# Enum with month names as keys and digits as values
class MonthOrdinals(Enum):
    JAN = f"{COLON}01{COLON}"
    FEB = f"{COLON}02{COLON}"
    MAR = f"{COLON}03{COLON}"
    APR = f"{COLON}04{COLON}"
    MAY = f"{COLON}05{COLON}"
    JUN = f"{COLON}06{COLON}"
    JUL = f"{COLON}07{COLON}"
    AUG = f"{COLON}08{COLON}"
    SEP = f"{COLON}09{COLON}"
    OCT = f"{COLON}10{COLON}"
    NOV = f"{COLON}11{COLON}"
    DEC = f"{COLON}12{COLON}"
    ЯНВ = f"{COLON}01{COLON}"
    ФЕВ = f"{COLON}02{COLON}"
    МАР = f"{COLON}03{COLON}"
    АПР = f"{COLON}04{COLON}"
    МАЙ = f"{COLON}05{COLON}"
    ИЮН = f"{COLON}06{COLON}"
    ИЮЛ = f"{COLON}07{COLON}"
    АВГ = f"{COLON}08{COLON}"
    СЕН = f"{COLON}09{COLON}"
    ОКТ = f"{COLON}10{COLON}"
    НОЯ = f"{COLON}11{COLON}"
    ДЕК = f"{COLON}12{COLON}"

    @classmethod
    def items(cls) -> tuple[tuple[str, str], ...]:
        # need __members__ items as Enum iterates over its values only (first 12 digits)
        return tuple((name, member.value) for name, member in cls.__members__.items())


# ? TODO unix seconds (%s), nanoseconds, day and week of year
class DateFormats(str, Enum):
    # date combinations without time
    # 1 known digits
    D = "%d"
    M = "%m"
    # 2 known digits
    DM = f"%d{COLON}%m"
    MD = f"%m{COLON}%d"
    MY = f"%m{COLON}%y"
    MYY = f"%m{COLON}%Y"
    YD = f"%y{COLON}%d"
    YYD = f"%Y{COLON}%d"
    YM = f"%y{COLON}%m"
    YYM = f"%Y{COLON}%m"
    # 3 known digits
    DMY = f"%d{COLON}%m{COLON}%y"
    DMYY = f"%d{COLON}%m{COLON}%Y"
    YYMD = f"%Y{COLON}%m{COLON}%d"
    YYDM = f"%Y{COLON}%d{COLON}%m"
    MDYY = f"%m{COLON}%d{COLON}%Y"
    YDM = f"%y{COLON}%d{COLON}%m"
    YMD = f"%y{COLON}%m{COLON}%d"
    MDY = f"%m{COLON}%d{COLON}%y"
    # * add %p (am pm)
    # 1
    DP = "%d{COLON}%p"
    # 2
    DMP = f"%d{COLON}%m{COLON}%p"
    MDP = f"%m{COLON}%d{COLON}%p"
    YDP = f"%y{COLON}%d{COLON}%p"
    YYDP = f"%Y{COLON}%d{COLON}%p"
    # 3
    DMYP = f"%d{COLON}%m{COLON}%y{COLON}%p"
    DMYYP = f"%d{COLON}%m{COLON}%Y{COLON}%p"
    YYMDP = f"%Y{COLON}%m{COLON}%d{COLON}%p"
    YYDMP = f"%Y{COLON}%d{COLON}%m{COLON}%p"
    MDYYP = f"%m{COLON}%d{COLON}%Y{COLON}%p"
    YDMP = f"%y{COLON}%d{COLON}%m{COLON}%p"
    YMDP = f"%y{COLON}%m{COLON}%d{COLON}%p"
    MDYP = f"%m{COLON}%d{COLON}%y{COLON}%p"

    @classmethod
    def values(cls) -> tuple[str, ...]:
        """
        Returns a tuple of nearly all possible values of datetime formats. These formats have colons
        (aka %d:%m:%Y:%H:%M:%S) and are used by dateparser library for parsing datetimes.

        The dateparser library has issues with parsing datetimes in certain formats, such as:
        - date with format of datetime
        - datetime with microseconds with format of time ending on seconds
        - when timezone is present

        This function generates various datetime formats by appending
            hours, minutes, seconds, and microseconds to the base format defined in the `cls` enum.

        Returns
        -------
        tuple[str]
            A tuple of near all datetime formats with colons (aka %d:%m:%Y:%H:%M:%S).
        """

        def append_missing_units(datetime_format: str, units_format: str) -> str:
            """
            Helper function that appends missing units to a datetime format.

            If the datetime format already ends with %p (AM/PM), the units are appended before %p.

            Parameters
            ----------
            datetime_format : str
                The base datetime format of cls to append units to.
            units_format : str
                The datetime units format to append to the datetime format.

            Returns
            -------
            str
                The datetime format with the appended units.
            """
            if datetime_format.endswith("%p"):
                return datetime_format.replace("%p", f"{units_format}{COLON}%p")
            return f"{datetime_format}{COLON}{units_format}"

        def add_hours_minutes(datetime_format: str) -> str:
            return append_missing_units(datetime_format, f"%H{COLON}%M")

        def add_minutes_hours(datetime_format: str) -> str:
            return append_missing_units(datetime_format, f"%M{COLON}%H")

        def add_seconds(datetime_format: str) -> str:
            return append_missing_units(datetime_format, "%S")

        def add_microseconds(datetime_format: str) -> str:
            return append_missing_units(datetime_format, "%f")

        # TODO itertools chain like
        return (
            *[member.value for member in cls],
            *[add_hours_minutes(member.value) for member in cls],
            *[add_minutes_hours(member.value) for member in cls],
            *[add_seconds(add_hours_minutes(member.value)) for member in cls],
            *[add_microseconds(add_seconds(add_hours_minutes(member.value))) for member in cls],
            *[add_seconds(add_minutes_hours(member.value)) for member in cls],
            *[add_microseconds(add_seconds(add_minutes_hours(member.value))) for member in cls],
        )


def _parse_date(date_str: str) -> datetime | None:
    """
    Parses a date string using the dateparser library and pre-configured settings.

    Args:
        date_str (str): The date string to parse.
        languages (list[str]): A list of language codes to use.

    Returns:
        datetime: A datetime representing the parsed date.
    """
    return parse(
        date_str,
        date_formats=DateFormats.values(),
        settings={
            "PREFER_DAY_OF_MONTH": "first",  # choose '1' as day of month, if missing
            "PARSERS": ["custom-formats"],  # use DateFormats only
        },
    )


def string_datetime_parser(timestamp_series: Series[str], utc: bool, parallel: bool = False) -> Series[datetime64]:
    """
    Parses a pandas Series of string timestamps into pandas Timestamps.

    Args:
        timestamp_series (Series[str]): The Pandas Series of string timestamps to parse.
        utc (bool): Flag to indicate whether to return UTC timestamps.
        parallel (bool): Flag to indicate whether to use parallel processing.

    Returns:
        Series[datetime]: The Pandas Series of parsed datetime objects.
    """

    def concat_datetime_timezone(datetime_: Timestamp, timezone: str) -> Timestamp:
        """
        Concatenates a datetime with a timezone string.

        Args:
            datetime_ (Timestamp): A pandas Timestamp representing a datetime.
            timezone (str): A string representing the timezone
                in the format aka "+03:00" or "-03:00".

        Returns:
            Timestamp: A pandas Timestamp representing the concatenated datetime and timezone.

        Raises:
            ValueError: If no timezone present for particular datetime_ arg
                or timezone string is not in the correct format.
        """
        # TODO two ways: num tz and code tz like ETC
        try:
            # convert to concatenated datetime and timezone
            return Timestamp(datetime_, tz=datetime.strptime(timezone, "%z").tzinfo)
        except (ValueError, TypeError):  # timezone is ""
            # return the original datetime if the timezone string is empty
            return datetime_

    def apply_wrapper(data: DataFrame) -> Callable:
        """
        Returns the apply method or parallel_apply method for a given DataFrame based on the
        parallel flag.

        Args:
            data (DataFrame): The Pandas DataFrame to apply the function to.
            parallel (bool): Flag to indicate whether to use parallel processing.

        Returns:
            Callable: The apply function to use with the given DataFrame.
        """
        if parallel:
            # ! it initializes globally, have not found terminate option
            pandarallel.initialize(progress_bar=False)

            return data.parallel_apply
        return data.apply

    # Prepare the datetime string Series for parsing
    no_tz_timestamps, timezones = _prepare_dt_for_dateparser(timestamp_series, utc)
    # Parse the datetime strings into Pandas Timestamps
    timestamps = concat(
        [apply_wrapper(no_tz_timestamps)(_parse_date), timezones], axis=1, keys=["dt", "tz"]
    ).apply(
        lambda dt_record: concat_datetime_timezone(dt_record["dt"], dt_record["tz"]),
        axis=1,
    )

    # Return parsed Timestamps or nan values for unsuccessful examples
    return to_datetime(timestamps, errors="coerce", utc=utc)


# TODO code timezones like ETC
# TODO split functions
def _cutout_timezone_digit(datetime: str) -> tuple[str, str]:
    """
    Dateparser lib fails to parse timezone in some cases. So switched to datetime tzinfo for
    timezone particularly. Formats (prepares for datetime) the timezone digit of a datetime string
    to the correct notation.

    Args:
        datetime (str): datetime string

    Returns:
        str: datetime string with correctly formatted timezone number.
    """
    # Determine the sign of the timezone
    gmt_sign = "+" if "+" in datetime else "-"

    try:
        # Find the index of the timezone sign
        gmt_index = datetime.rindex(gmt_sign)
        gmt_tail = datetime[gmt_index:]

        # Find the next set of digits after the timezone sign
        next_utc_digits = search(r"\d{1,2}.?(\d{1,2})?", gmt_tail).group()
    except (ValueError, AttributeError):  # If no timezone is found
        return datetime, ""
    else:
        # Check if there is a separator between the hour and minute of the timezone
        has_separator = not next_utc_digits.isdigit()
        # Determine the length of the timezone hours string
        # 5 stands for kind of 06:00
        gmt_hours_length = (
            2 if len(next_utc_digits) == 5 or not has_separator and len(next_utc_digits) in {2, 4} else 1
        )

        last_utc_digit_index = gmt_index + len(next_utc_digits)

        # Add missing minutes to the timezone if necessary
        tz_minute_zeros = ":00"
        # Extract the timezone string with mb missing minutes
        gmt_string = f"{gmt_sign}{next_utc_digits[:gmt_hours_length]}{tz_minute_zeros}"
        # If timezone hours is of one digit, add a leading zero before it
        gmt_string = gmt_string if gmt_hours_length == 2 else f"{gmt_sign}0{gmt_string[1:]}"
        # Rebuild datetime as datetime_no_gmt - datetime with timezone extracted
        datetime_no_gmt = f"{datetime[:gmt_index]}{datetime[last_utc_digit_index + 1:]}"

        return datetime_no_gmt, gmt_string


def _prepare_dt_for_dateparser(timestamp_series: Series, utc: bool) -> tuple[Series[str], Series[str]]:
    """
    Processes a timestamp series by converting all values to lowercase, formatting timezone if
    utc_value is True, replacing month names with formatted date, and replacing remaining 'non-
    timezone' symbols with regex.

    Args:
        timestamp_series (Series): A series of timestamp strings.
        utc_value (bool): A boolean indicating whether to format timezone.

    Returns:
        Series: formatted series of string timestamps.
    """
    # lowercase all strings before replacements
    timestamp_series = timestamp_series.astype("string").str.lower()
    # ensure strings with astype
    # nan or else - argument of type 'float' is not iterable

    timezones = Series(index=timestamp_series.index)  # conform index of datetime and timezone values
    if utc:
        # Format timezone like +03:00
        timestamp_series, timezones = DataFrame.from_records(
            zip(
                *timestamp_series.map(
                    _cutout_timezone_digit,
                )
            ),
            columns=timestamp_series.index,
        ).iloc

    # Replace whole month names (август) with formatted date
    for month, formatted_date in MonthOrdinals.items():
        timestamp_series = timestamp_series.str.replace(month, formatted_date, case=False)

    # Replace remaining symbols with regex
    for pattern, formatted_pattern in REGEX_STEPS.items():
        timestamp_series = timestamp_series.str.replace(pattern, formatted_pattern, regex=True)

    return timestamp_series, timezones
