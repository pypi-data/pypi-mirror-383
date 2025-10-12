from __future__ import annotations
from copy import deepcopy
from typing import Any, Iterable

from dataclassy import asdict, dataclass, factory
from loguru import logger

from numpy import float64, int64, nan, where
from numpy.typing import NDArray
from pandas import DataFrame, Series, unique
from pandas.arrays import ArrowStringArray
from pandas.core.groupby.generic import DataFrameGroupBy

from pm4mkb.baza import (
    Case,
    CaseSuccess,
    DataEditor,
    DateTime,
    Duration,
    DurationUnits,
    HolderColumns,
    MandatoryColumns,
    Stage,
    SuccessInputs,
    SyntheticColumns,
    Text,
    TimeErrors,
    User,
    get_raw_data,
    notify_absent_attribute,
)


@dataclass(eq=False, slots=True, frozen=True)
class DataHolder:
    """
    Loads a data suitable for Process Mining and associates the names of its columns.

    In a nutshell, `DataHolder` is a flexible container class for:
        1. Preparing raw Process Mining log data into a structured dataset
            ready for analyzing with most of pm4mkb's Data Science algorithms.
        2. Holding the structured data
        3. Extracting certain properties of the data, related to Process Mining tasks,
            and manipulating the data to some extent.

    Description And Purpose
    -----------------------
    `DataHolder` is designed to manage and interact with data, usually derived from event logs.
    It serves for ongoing storage of the sorted and processed event data
    and provides methods for data manipulation and analysis.
    Such as grouping and filtering events based on various parameters, getting special attributes.
    Data processing involves different steps:
        dealing with empty values, cleaning and formatting timestamps,
        skipping weekends and holidays, sorting events and more.

    Value
    -----
    The `DataHolder` delivers a streamline of data preprocessing,
        setting a stage for further data analysis.
    It ensures the data is clean and arranged in a way
        that highlights the sequence of operations, which lays the foundation
        to facilitate further application of process mining analysis algorithms.
    `DataHolder` transforms raw business process data into a coherent format
        that is ready for detecting important business process markers.
    Like process success, bottlenecks and other issues or insights.

    Inputs
    -------
    Requires event data — a Pandas DataFrame or a path to the file,
        column names for typical Process Mining attributes,
        and various parameters such as datetime formats or case success criteria.
    Outputs
    -------
    It will save and be ready to output an organized Pandas DataFrame with additional columns
        indicating process success, calculated or adjusted event durations.
    If the input is a Pandas DataFrame, it will be modified in-place (overwritten by `DataHolder`).

    Limitations
    -----------
    Apart of its primary purpose, `DataHolder` is capable of handling a variety of datasets.
    Initialization parameters of the class are highly adaptive, what gives an opportunity
    for multiple configuration choices of relevant columns and other settings.
    This flexibility allows users to fine-tune how `DataHolder` interprets and processes the data,
        making it suitable for a wide range of data shapes and analysis needs.
    This means that the data doesn't have to support all the columns required for Process Mining.
    Sometimes, defining only one column may be sufficient for the analysis.

    Main Components And Their Interaction
    -------------------------------------
    `DataHolder` serves as a central class and the primary entry point for data-related operations,
        employing `DataEditor` as a another layer toolkit class for various data manipulation tasks.
    `DataHolder` is also complemented by a number of auxiliary classes
        that enhance its functionality and user convenience.
    Here is an overview of these classes and their roles:

    ### Helper Classes for Parameter Initialization
    - `TimeErrors`: Enum used to specify how to handle errors during date-time conversions.
    - `DurationUnits`: Enum to set the resulting time unit of calculated or received duration data.
    - `SuccessInputs`: A data structure to encapsulate inputs necessary
        to determine success of process cases.

    ### Attribute Classes for `DataHolder`
    You may encounter these classes when getting respective `DataHolder` attributes
    - `HolderColumns`: Named tuple used to store references to the columns of the data
        that has parameter names in `DataHolder`.
    - `SyntheticColumns`: Named tuple used to manage synthetic columns, the ones which
        are additional to the original data and may be created during the data processing.
    - `MandatoryColumns`: Named tuple that defines a list of required columns in the data
        purposed for most of Process Mining tasks.

    Parameters
    ----------
    data : DataFrame
        A Pandas DataFrame containing the event data of a process,
        a set of events that have taken place within a particular process or system.
        It contains necessary information to reconstruct episodes
            that define the execution of the process.
        This data is fundamental for Process Mining techniques which are used to
            discover, monitor, and improve real processes by extracting knowledge from event logs.

        Can be either
            - a pandas.DataFrame object
            - a path to file — common string or pathlib.Path instance.
        If 'path to file' is given, it is considered to be a full path to the data.
        Supported file formats are: 'csv', 'xls'/'xlsx', 'txt'.

        Typically, an event data must contain at least three key columns:
            case ID, activity (event name), timestamp.
        Additional columns can provide more context and can often be found in data.
    col_case : str, optional
        The name of column in data that contains instances of the process identifier,
            often referred to as a 'case' or 'case ID'. Each stage (event) is tied to its case.
        Is usually being used to group events into cases.
    col_stage : str, optional
        The name of column in data that contains names of the process events.
        It represents the actual steps or actions that took place within the process.
    col_start_time : str, optional
        The name of column in data that has records of date and time for every event start.
        Timestamps are essential for understanding the order of events and their duration.
        ~~~
        This column can be set as parameter or computed from end timestamp and duration columns.
    col_end_time : str, optional
        The name of column in data that has records of date and time for every event end.
        Timestamps are essential for understanding the order of events and their duration.
        ~~~
        This column can be set as parameter or computed from start timestamp and duration columns.
    col_user : str, optional
        The name of column in data that contains identifiers of users or resources
            (e.g., person, machine, system) that executed or initiated the event.
        Who or what can make the referred action.
        It might be a user's name, ID or even session or any other identifier.
    col_text : str, optional
        The name of column in data that has text comments related to each event.
            These comments are often describe the action names itself,
            but they can also include details about any other aspects of the process.
            For a particular action name, text comments may not necessarily be unique.
    col_duration : str, optional
        The name of column in data that has duration records for every event.
        Every duration represent a period of time that is needed to fulfill the particular action.
        In other words, how long the action took.
        Resulting duration values will be of numeric type,
            converted into seconds or other time unit set with `DurationUnits`.
        ~~~
        This column can be set as parameter or computed from timestamp columns.
    col_case_success : str, optional
        The name of column in data that has success indicators for each case ID.
        Shows whether a case was completed successfully, according to case success criteria.
        Column consists of 'True' or 'False' values, which can't alter in particular case ID.
        ~~~
        This column can be set as parameter or computed with help of `SuccessInputs`.
    sep : str, default ','
        File reading parameter.
        The separator character used in the origin files like 'csv' to distinguish between columns.
        If a file uses separator different from ',', you have to set the parameter.
    encoding : str, optional
        File reading parameter.
        The character encoding format used in the origin file string.
        You have to set the right value to avoid error and read the data,
            if data encoding is different from unicode (UTF-8).
    nrows : int, optional
        File reading parameter.
        Limits the number of rows in data to read. When None, all rows are read.
        May be useful for large files, to glance over first N rows.
    preprocess : bool, default True
        Determines whether the data should undergo preprocessing steps.
        Preprocessing might include
            data normalization, handling missing values, optimizing data types and more.
    time_format : str, optional
        Data processing parameter.
        The format string for parsing and converting datetime columns in the raw data.
        The datetime columns are the ones under the `col_start_time` and `col_end_time` names.
        Specifying this is likely to prevent errors due to ambiguous date formats.

        Examples:
            '13-05-2020 15:30:05' -> '%d-%m-%Y %H:%M:%S'
            '05/13/2020, 15:30' -> '%m/%d/%Y, %H:%M'
            Consult this for the time format syntax:
            https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes

        Set the parameter if either:
            - You have encountered errors when `time_format=None`, need to parse the time column
                So you need to set the exact format for datetime records.
            - You want the resulting datetime values to be set in specific time format
                For instance, '05/13/2020, 15:30' with `time_format='%m/%Y'`
                will be pruned to Timestamp('2020-05-01 00:00:00').
    time_errors : TimeErrors or str, default TimeErrors.RAISE
        Data processing parameter.
        Defines the behavior when time parsing error occurs.
        Errors can arise when:
            1. At least one datetime string format is different from the `time_format` specified.
            2. Failed to detect a valid format to parse datetime values, when `time_format=None`.
                With any combination of `dayfirst` and `yearfirst` parameters.

        The parameter accepts the following `TimeErrors` Enum values:
            * 'raise'
            Just raise an exception if an error is encountered while converting strings to datetime.
            * 'coerce'
            Conversion to datetime is done anyway, without an interruption.
            Any found errors are replaced with 'NaT'. This approach may lead to complete data loss.
            * 'auto_convert'
            Disclaimer:
                - the `time_format` parameter is required to be set
                - results may not be reliable
            Attempts to parse the timestamps with `time_format` by all means.
            Applies sophisticated conversion steps — additional logic and heuristics to guess
            the format for every datetime string, when it can't be parsed with Pandas `to_datetime`.
            For values, which format is figured out, strings are converted to the `time_format`.
            And for which ones auto-conversion is unsuccessful, 'NaT' are set ('coerce' fallback)
            This mode uses https://pypi.org/project/dateparser library to actually guess formats.
    dayfirst : bool, default True
        Data processing parameter.
        Whether to interpret the first value in an ambiguous 3-integer date,
            (e.g. 01/05/09) as the day (True) or month (False).
        Pandas `to_datetime` will parse '01/05/09' in 'DMY' format as Timestamp('2009-05-01')
            and in 'YDM' format if `yearfirst` is also set to 'True' — as Timestamp('2001-09-05').

        The 'day before month' date representation is common in European formats.
        This setting is not strict, but will prefer to parse datetime values with day first.
    yearfirst : bool, default False
        Data processing parameter.
        Whether to interpret the first value in an ambiguous 3-integer date,
            (e.g. 01/05/09) as the year (True) or month (False).
        Pandas `to_datetime` will parse '01/05/09' in 'YMD' format as Timestamp('2001-05-09')
            and in 'YDM' format if `dayfirst` is also set to 'True' — as Timestamp('2001-09-05').

        Usually, the last number in date representations is understood as the year.
        With this parameter, the year is interpreted as the one before month and day.
    utc : bool, default False
        Data processing parameter.
        Controls localization for timezone-related datetime parsing.
        All timezone-aware timestamps are converted to UTC when `utc=True`.

        This is must-have for timestamp consistency in datasets that span two or more time zones.
    duration_unit : DurationUnits, default DurationUnits.SECOND
        Data processing parameter.
        The time unit of event duration values. Changing this affects scale of duration metrics.
        Accepts `DurationUnits` Enum values. Can set one of {'second', 'minute', 'hour', 'day'}.

        For instance, with `duration_unit` being 'hour',
            initial duration values of [3600, 1800] will be scaled and stored as [1, 0.5].
    skip_weekends : bool, default False
        Data filtering parameter.
        Whether to keep or omit records on weekends (Sat and Sun).
        Timestamps occurred on weekends will be excluded from data when `skip_weekends=True`.

        Can help with business analysis of process, which doesn't take weekends into account.
        It makes sense to use computed durations if records are skipped. Affects computation result.
    skip_holidays_list : Iterable[str], default ()
        Data filtering parameter.
        A list of arbitrary dates in a year like ('01 Jun', '1 Jan-4 Jan', '8 март-10 март' '9 Мая')
            which represent holidays to be excluded from data, similar to the `weekends` parameter.
        The dates must be added manually to the list (empty by default).
        Once they are added, these days will be thrown away. To not to skew the event durations.

        Can help with business analysis, in the same way as `skip_weekends` parameter.
    success_inputs : SuccessInputs, default SuccessInputs
        Data processing parameter.
        A named tuple class instance with a column in data and the column entries
            that defines success criteria for a process case IDs.
        This has to be used when you need to mark the case IDs as successful or unsuccessful,
            based on the inclusion of certain column entries.
        Every event name 'entry' from `SuccessInputs.entries`
            implies the success of a case ID that contains any of these entries.

    Attributes
    ----------
    data : pandas.DataFrame
        The internal DataFrame where the structured log is stored.
        This is the data that Process Mining algorithms will work with.
    col_case : str, optional
        Column name referring to case IDs.
    col_stage : str, optional
        Column name referring to events.
    col_start_time : str, default=SyntheticColumns.START_TIME
        Column name referring to start times of events.
    col_end_time : str, default=SyntheticColumns.END_TIME
        Column name referring to end times of events.
    col_user : str, optional
        Column name referring to resources, set as 'user' identifiers.
    col_text : str, optional
        Column name referring to text details extending process events description.
    col_duration : str, default=SyntheticColumns.DURATION
        Column name referring to event durations.
    col_case_success : str, default=SyntheticColumns.CASE_SUCCESS
        Column name referring to success (or not) of process case IDs.

    Methods
    -------
    copy(**new_holder_args)
        Create a deep copy of the current instance with optional attribute overrides.
    calculate_duration()
        Calculate the durations of process events, if not calculated.
    group_as_traces(*columns)
        Group the event data with the `columns` by case ID into process instances, known as traces.
    sort_event_data()
        Sort the events in the data. Chronologically and consistently for every unique case.
    top_traces_holder(n)
        Returns a `DataHolder` containing the data of the `n` most frequent traces (event chains).

    Raises
    ------
    AttributeError
        When attempting to directly change the data attribute.
    AssertionError
        If any of the arguments passed to `copy` do not exist as attributes within the object.
    LogWithout<COLUMN_NAME>Error
        If no <COLUMN_NAME> present in the `data` of particular `DataHolder` instance.
        When trying to access a property that should return or work with <COLUMN_NAME>.
    FileNotFoundError
        If the file path provided as an argument for the `data` parameter does not exist.
    ValueError
        If the format of the input data is not supported
        or there are inconsistencies in the data that prevent proper loading and processing.

    Warnings
    --------
    - If certain columns are missing during the initialization, mandatory for Process Mining log.
    - Various warnings may appear during data preprocessing, when values are validated.

    Notes
    -----
    - Event logs can come from various sources:
        - IT systems like Customer Relationship Management (CRM)
        - Workflow management systems
        - Ticketing systems
        - Website clickstreams
    - Although a single column parameter from (`col_case`, `col_start_time`, `col_end_time`)
        may be sufficient for class initialization,
        the absence of certain columns will trigger warnings or errors,
        informing about the inability to use certain methods.
    - Direct modification of attributes, including `data`, is restricted;
        However, a new `DataHolder` instance can be created from existing
        by copying with minimal changes. You should be aware of what you're doing.
        This design choice ensures that data integrity is maintained
        throughout its lifecycle in data science pipeline.
        And helps to prevent unintended side-effects.
    - Some operations may result in an ArrowInvalid overflow error (https://github.com/apache/arrow/issues/33049),
        which has been resolved in newer versions of pandas (>=2.2), available for Python 3.9+.

    Examples
    --------
    To initialize a `DataHolder` with minimal information:
    >>> from pandas import DataFrame
    >>> from pm4mkb.baza import DataHolder
    >>>
    >>> event_log_data = DataFrame(...)
    >>> data_holder = DataHolder(event_log_data, col_case="case_id")

    For a more common setup, one can specify conventional Process Mining columns:
    >>> df = DataFrame({
    ... "case_column": [1, 1, 2],
    ... "stage_column":["st1", "st2", "st1"],
    ... "dt_column":["12.12.2022", "12.12.2022, "13.12.2022"]})
    >>> data_holder = DataHolder(df, "col_case", "col_stage", "dt_column")
    Or this way:
    >>> data_holder = DataHolder("path/to/file.csv", "case_column", "stage_column", "dt_column")

    And for a comprehensive setup, one can specify additional columns and settings:
    >>> data_holder = DataHolder(
    ...     "path/to/event_log_data.csv",
    ...     col_case="case_id",
    ...     col_stage="activity",
    ...     col_start_time="start_time",  # Can be a column in data or just a name for computed
    ...     col_end_time="end_time",  # Can be a column in data or just a name for computed
    ...     col_user="user_name",
    ...     col_text="text_info",
    ...     col_duration="activity_duration",  # Can be a column in data or just a name for computed
    ...     col_case_success="case_success",  # Can be a column in data or just a name for computed
    ...     encoding="windows-1251",
    ...     sep=";",
    ...     time_format="%Y-%m-%d %H:%M:%S",
    ...     time_errors=TimeErrors.AUTO_CONVERT,
    ...     skip_weekends=True,
    ...     skip_holidays_list=("01 июня", " 1 Jan -10Jan", "23 Dec  "),
    ...     duration_unit=DurationUnits.HOUR,
    ...     success_inputs=SuccessInputs(
    ...         column="activity",
    ...         entries={"Подписание документов ", "Принято"}
    ...     ),
    >>> )
    """

    UNSTEADY_COLUMNS = ("col_duration", "col_case_success")

    data: DataFrame

    col_case: str | None = None
    col_stage: str | None = None
    col_start_time: str | None = SyntheticColumns.START_TIME
    col_end_time: str | None = SyntheticColumns.END_TIME
    col_user: str | None = None
    col_text: str | None = None
    col_duration: str | None = SyntheticColumns.DURATION
    col_case_success: str | None = SyntheticColumns.CASE_SUCCESS

    _data_editor: DataEditor = factory(DataEditor)

    def __post_init__(
        self,
        sep: str = ",",
        encoding: str | None = None,
        nrows: int | None = None,
        preprocess: bool = True,
        time_format: str | None = None,
        time_errors: TimeErrors | str = TimeErrors.RAISE,
        dayfirst: bool = True,
        yearfirst: bool = False,
        utc: bool = False,
        duration_unit: DurationUnits = DurationUnits.SECOND,
        skip_weekends: bool = False,
        skip_holidays_list: Iterable[str] = (),
        success_inputs: SuccessInputs = SuccessInputs(),
    ) -> None:
        """
        Initializes the DataHolder instance and optionally, performs processing steps for the
        data.
        """
        processed_data = (
            self._preprocess_data(
                get_raw_data(self.data, nrows=nrows, sep=sep, encoding=encoding),
                time_format=time_format,
                time_errors=time_errors,
                dayfirst=dayfirst,
                yearfirst=yearfirst,
                utc=utc,
                skip_weekends=skip_weekends,
                skip_holidays_list=skip_holidays_list,
                duration_unit=duration_unit,
                success_inputs=success_inputs,
            )
            if preprocess
            else get_raw_data(self.data, nrows=nrows, sep=sep, encoding=encoding)
        )
        object.__setattr__(self, "data", processed_data)  # frozen trick
        # unify synthetic and common columns
        # required by imbalanced-learn and scikit-learn validation
        self.data.columns = self.data.columns.astype("string[pyarrow]")

    def __getattr__(self, deleted_synth_name: str) -> None:
        if deleted_synth_name in self.UNSTEADY_COLUMNS:
            notify_absent_attribute(deleted_synth_name)
            return None
        if deleted_synth_name in {"col_start_time", "col_end_time"}:
            return None

        raise AttributeError(f"У объекта '{self.__class__.__name__}' нет атрибута '{deleted_synth_name}'")

    def __deepcopy__(self, memo: dict[str | int, Any]) -> DataHolder:
        """
        Return a deep copy of the DataHolder instance, with optional attribute modifications.

        Parameters
        ----------
        memo : dict[str, Any]
            A dictionary of new DataHolder arguments to be set instead of the self copies,
                also serves to reconstruct object relations.

        Returns
        -------
        new_self : DataHolder
            A new deep copied instance of the class.
        """
        # extract arguments to be modified in the copy, clear memo
        new_holder_args, memo = memo, {}
        # create a new instance of the class
        new_self = self.__class__.__new__(self.__class__)
        # self reference for new instance
        memo[id(self)] = new_self

        # set new attributes from self and new_holder_args
        # deepcopy self attributes, even though it may be just a string
        for attribute in self.__slots__:  # type: ignore[attr-defined]
            # set attribute object in a way it's possible
            object.__setattr__(
                new_self,
                attribute,
                new_holder_args.get(
                    attribute,  # set from new_holder_args
                    # or set a copy if the attribute wasn't passed
                    deepcopy(getattr(self, attribute), memo),  # type: ignore[arg-type]
                ),
            )

        return new_self

    @property
    def case(self) -> Series[Case]:
        try:
            return self.data[self.col_case]
        except KeyError as err:
            raise LogWithoutCaseError("The event log does not have 'case' column") from err

    @property
    def stage(self) -> Series[Stage]:
        try:
            return self.data[self.col_stage]
        except KeyError as err:
            raise LogWithoutStageError("The event log does not have 'stage' column") from err

    @property
    def start_time(self) -> Series[DateTime]:
        try:
            return self.data[self.col_start_time]
        except KeyError as err:
            raise LogWithoutStartTimeError("The event log does not have 'start time' column") from err

    @property
    def start_timestamp(self) -> NDArray[float64]:
        time_series = self.start_time

        return where(time_series.isna(), nan, time_series.view(int64) // 1e9)

    @property
    def end_time(self) -> Series[DateTime]:
        try:
            return self.data[self.col_end_time]
        except KeyError as err:
            raise LogWithoutEndTimeError("The event log does not have 'end time' column") from err

    @property
    def end_timestamp(self) -> NDArray[float64]:
        time_series = self.end_time

        return where(time_series.isna(), nan, time_series.view(int64) // 1e9)

    @property
    def text(self) -> Series[Text]:
        try:
            return self.data[self.col_text]
        except KeyError as err:
            raise LogWithoutTextError("The event log does not have 'text' column") from err

    @property
    def user(self) -> Series[User]:
        try:
            return self.data[self.col_user]
        except KeyError as err:
            raise LogWithoutUserError("The event log does not have 'user' column") from err

    @property
    def duration(self) -> Series[Duration]:
        try:
            return self.data[self.col_duration]
        except KeyError as err:
            raise LogWithoutDurationError("The event log does not have 'duration' data") from err

    @property
    def case_success(self) -> Series[CaseSuccess]:
        try:
            return self.data[self.col_case_success]
        except KeyError as err:
            raise LogWithoutCaseSuccessError("The event log does not have 'case success' data") from err

    @property
    def known_columns(self) -> HolderColumns:
        """
        Get the present DataHolder columns, passed by a user at the initialization.

        Returns
        -------
        HolderColumns
            A HolderColumns named tuple containing the known columns of the data.
        """
        # disable logger for this module - ignore __getattr__ info
        logger.disable(__name__)
        holder_columns = HolderColumns(  # type: ignore[abstract]
            **{attribute: value for attribute, value in asdict(self).items() if attribute.startswith("col_")},
        )
        # enable __getattr__ messages
        logger.enable(__name__)

        return holder_columns

    @property
    def timestamp_columns(self) -> Iterable[str]:
        return [*filter(None, [self.col_start_time, self.col_end_time])]

    @property
    def any_timestamp_column(self) -> str | None:
        """Returns the name of any timestamp column for the data, if any exists."""
        # Check if either col_start_time or col_end_time is set
        return self.col_start_time or self.col_end_time

    @property
    def mandatory_columns(self) -> MandatoryColumns:
        return MandatoryColumns(
            self.col_case,
            self.col_stage,
            self.col_start_time,
            self.col_end_time,
        )

    @property
    def mandatory_frame(self) -> DataFrame:
        return self.data[
            filter(lambda column: isinstance(column, str), self.mandatory_columns)
        ]  # filter timestamp columns and None

    @property
    def unique_cases(self) -> NDArray[Case]:  # NDArray[str_] is ArrowStringArray
        """Return unique case ID in the event log"""
        return unique(self.case)

    @property
    def unique_stages(self) -> NDArray[Stage]:  # NDArray[str_] is ArrowStringArray
        """Return unique stages in the event log"""
        return unique(self.stage)

    @property
    def unique_users(self) -> NDArray[User]:  # NDArray[str_] is ArrowStringArray
        """Return unique users in the event log"""
        return unique(self.user)

    @property
    def unique_texts(self) -> ArrowStringArray:
        """Return unique texts in the event log"""
        return unique(self.text)

    @property
    def case_groupby(self) -> DataFrameGroupBy:
        return self.data.groupby(self.case.name)

    @property
    def stage_groupby(self) -> DataFrameGroupBy:
        return self.data.groupby(self.stage.name)

    @property
    def user_groupby(self) -> DataFrameGroupBy:
        return self.data.groupby(self.user.name)

    @property
    def text_groupby(self) -> DataFrameGroupBy:
        return self.data.groupby(self.text.name)

    @property
    def case_success_groupby(self) -> DataFrameGroupBy:
        return self.data.groupby(self.case_success.name)

    @property
    def has_both_times(self) -> bool:
        """
        Checks if both col_start_time and col_end_time are not None. Whether the log has
        timestamp
        intervals with both end and start for stages.

        Returns:
            bool: True if both col_start_time and col_end_time are not None.
                False otherwise.
        """
        return self._has_start_time and self._has_end_time

    @property
    def has_users(self) -> bool:
        """Checks if the holder user column has been passed."""
        return self.col_user in self.data

    @property
    def has_texts(self) -> bool:
        """Checks if the holder text column has been passed."""
        return self.col_text in self.data

    @property
    def has_duration(self) -> bool:
        """Checks if the holder duration has been passed or calculated."""
        return self.col_duration in self.data

    @property
    def has_case_success(self) -> bool:
        """Checks if the holder case success has been passed or calculated."""
        return self.col_case_success in self.data

    def copy(self, **new_holder_args: Any) -> DataHolder:
        """
        Create a deep copy of the current object with optional overrides.

        Parameters
        ----------
        new_holder_args : dict[str, Any]
            Optional arguments to override the values of the copied object.

        Returns
        -------
        DataHolder
            A new instance of the DataHolder, with the specified overrides.

        Raises
        ------
        AssertionError
            If any of the arguments in new_holder_args do not exist as slots in the object.
        """

        def all_arguments_exist() -> bool:
            """
            Check if all keys from `new_holder_args` exist as attributes in the current
            object.
            """
            return not set(new_holder_args).difference(self.__slots__)  # type: ignore[arg-type]

        assert all_arguments_exist(), "Trying to set DataHolder attributes that do not exist"

        return deepcopy(self, new_holder_args)  # type: ignore[arg-type]

    def group_as_traces(self, *columns: str | None) -> DataFrame | None:
        """
        Build the event log data grouped by case ID,
            with given columns aggregated to tuples (traces).
        Default column to aggregate is set to `col_stage`.

        Parameters
        ----------
        columns : Iterable of str
            Columns to aggregate.

        Returns
        -------
        pd.DataFrame
            Grouped data, with columns consisting of case ID and traces of `columns` argument.
        """
        # use stage column by default if no arguments passed
        columns = columns or [self.col_stage]

        # ensure columns exist in the data, col_stage still can be None
        try:
            self.data[[*columns]]
        except (TypeError, KeyError) as err:  # empty or non-existing columns
            raise InvalidColumnsToGroup(f"Не все колонки из '{columns}' найдены в данных") from err

        # return the data grouped as traces
        return self.case_groupby.agg(dict.fromkeys(columns, tuple)).reset_index()

    def calculate_duration(self) -> None:
        """
        Calculates stages duration in the event log, for different scenarios.

        If possible. If the duration has already been calculated, the function does nothing.
        """
        # If duration has already been calculated, do nothing
        if self.has_duration:
            return

        self._data_editor.calculate_duration(self)

    def indicate_case_success(self, success_inputs: SuccessInputs) -> None:
        """
        Indicate case ID success for the event log. Write computed success data to the
        `col_case_success` column. By default, entries column of the `success_inputs` is
        `col_stage`, so `success_inputs` `column` can be omitted.

        Parameters
        ----------
        success_inputs : SuccessInputs
            The successful entry inputs (entries and corresponding column)
            for the holder case ID success.
        """
        # recompute each time with another 'success_inputs'
        # do not prevent computation if already have case success column
        self._data_editor.indicate_case_success(self, success_inputs)

    def sort_event_data(self) -> None:
        """
        Sort the event data by a preset of 1-4 known holder columns that are significant for
        process
        mining analysis. DataHolder-specific columns that are not known (not passed) are ignored.

        Raises:
            # TODO change LogWithoutTimestampError
            LogWithoutTimestampError: If no case id and datetime columns are given.
        """
        self._data_editor.sort_event_data()

    # ? TODO return data frame instead of full holder
    def top_traces_holder(self, n: int) -> DataHolder:
        """
        Return DataHolder with the data of n most frequent traces.

        Parameters
        ----------
        n : int
            Number of top frequent traces.

        Returns
        -------
        DataHolder
            A new DataHolder object containing the data of the n most frequent traces.
        """
        # get the grouped data of the stages (chains of activities)
        stage_groups: DataFrame = self.group_as_traces()

        # get the ids of the n most frequent traces
        id_series = (
            stage_groups.groupby(self.col_stage)
            .agg({self.col_case: (tuple, len)})[self.col_case]
            .sort_values("len", ascending=False)["tuple"]
            .head(n)
        )
        # get the set of ids for the top traces
        top_ids = {id_ for id_tuples in id_series for id_ in id_tuples}

        # new holder instance's data will include only the data with top ids
        return self.copy(data=self.data[self.case.isin(top_ids)])

    @property
    def _has_start_time(self) -> bool:
        """Checks if the holder has start time data."""
        return self.col_start_time in self.data

    @property
    def _has_end_time(self) -> bool:
        """Checks if the holder has end time data."""
        return self.col_end_time in self.data

    def _preprocess_data(self, data: DataFrame, **kwargs: Any) -> DataFrame:
        """
        Preprocesses the event log DataFrame by performing a chain of `_data_editor` instance
        manipulations:

        - replaces a bunch of missing value representations with numpy `nan`
        - removes records with null values among col_case or col_stage
        - asserts the most suitable data type for each column in the data frame,
            forbids categories for known holder columns
        - converts timestamps from the given datetime columns to the time format
        - adjusts the duration values to the time unit, if duration column is given,
            calculates independently and inserts duration column, otherwise
        - removes records that occurred on weekend or holiday,
            based on `skip_weekends` and `skip_holidays_list` parameters
        - sorts the event log by subset of 1-4 known holder columns.

        Parameters
        ----------
        data : pandas.DataFrame
            The event log to preprocess.
        time_format : str or None
            The time format string to use when parsing datetime columns..
            Examples:
            '%d-%m-%Y %H:%M:%S' -> '13-05-2020 15:30:05'
            '%d/%m/%Y, %H:%M' -> '05/13/2020, 15:30'
            Consult this for time_format syntax:
            https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
        time_errors : TimeErrors ('raise', 'coerce', 'auto_convert')
            Specifies the way to handle errors when adjusting datetime columns.
                Is used if only time_format is not None.
            if ‘raise’, then invalid parsing will raise an exception;
            if ‘coerce’, then invalid parsing will be set as NaT;
            if 'auto_convert', then auto conversion attempt will be made;
        dayfirst : bool
            Whether to interpret dates in the European date format (dd-mm-yyyy).
                (e.g. 01/05/09) first value may be parsed as the day (True) or month (False).
                If yearfirst is set to True, then distinguishes between YDM and YMD.
        yearfirst : bool
            Whether to interpret the first value in a date as the year.
                (e.g. 01/05/09) first (True) or last (False) value may be parsed as the year.
        utc : bool, optional
            Whether to assume datetime values are in UTC, by default False.
        duration_unit : DurationUnits
            The duration unit to use when adjusting stages with duration.
        skip_weekends : bool, optional
            Whether to exclude weekends when adjusting stages with duration, by default False.
        skip_holidays_list : Iterable[str], optional
            A list of holidays to exclude when adjusting stages with duration, by default ().
        TODO success_inputs

        Returns
        -------
        pandas.DataFrame
            The preprocessed event data.
        """
        logger.info("Обработка данных ивент лога...")
        self._data_editor.setup(
            data,
            self.known_columns,
        )

        self._data_editor.adjust_datetime(
            **dict(
                datetime_columns=self.timestamp_columns,
                **{key: kwargs[key] for key in ("time_format", "time_errors", "dayfirst", "yearfirst", "utc")},
            )
        )
        self._data_editor.skip_calendar_days(
            kwargs["skip_weekends"],
            kwargs["skip_holidays_list"],
            [*filter(lambda column: not isinstance(column, SyntheticColumns), self.timestamp_columns)],
        )
        # * sort the times before working with durations
        self._data_editor.sort_event_data()

        if self.col_duration in data:
            self._data_editor.adjust_stages_duration(
                self, kwargs["duration_unit"], duration_errors=kwargs["time_errors"]
            )
        else:
            self._data_editor.calculate_duration(self)

        self._data_editor.adjust_data_types()

        # * run after adjust_data_types - no need to adjust bool dtype
        if self.col_case_success in data:
            self._data_editor.adjust_case_success()
        else:
            self._data_editor.indicate_case_success(self, kwargs["success_inputs"])

        logger.info("Обработка данных завершена")

        return data


# TODO init exception messages
class LogWithoutCaseError(KeyError):
    pass


class LogWithoutStageError(KeyError):
    pass


class LogWithoutStartTimeError(KeyError):
    pass


class LogWithoutEndTimeError(KeyError):
    pass


class LogWithoutTextError(KeyError):
    pass


class LogWithoutUserError(KeyError):
    pass


class LogWithoutDurationError(KeyError):
    pass


class LogWithoutCaseSuccessError(KeyError):
    pass


class LogWithoutTimestampError(AttributeError):
    pass


class InvalidColumnsToGroup(TypeError, KeyError):
    pass
