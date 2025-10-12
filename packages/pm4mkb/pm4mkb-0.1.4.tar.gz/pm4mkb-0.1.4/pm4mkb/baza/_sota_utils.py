from __future__ import annotations
from enum import Enum
from itertools import repeat
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generator, Iterable, NamedTuple, Type

from loguru import logger

from numpy import linspace, searchsorted, unique
from pandas import DataFrame, read_csv, read_excel, read_table


if TYPE_CHECKING:
    from pm4mkb.baza.managers.duration import DurationManager


def get_raw_data(data_or_path: str | Path | DataFrame, **reader_arguments: int | str | None) -> DataFrame | None:
    logger.info("Чтение данных...")

    if isinstance(data_or_path, DataFrame):
        return data_or_path
    if isinstance(data_or_path, (str, Path)):
        return _read_from_file(Path(data_or_path), **reader_arguments)

    # TODO custom exception, message
    raise ValueError(f"pandas.DataFrame or str types are expected, but got {type(data_or_path)}")


def notify_absent_attribute(name: str) -> None:
    """
    Log an info message indicating the absence of `col_duration` attribute or `col_case_success`.
    And more, in the future.

    Parameters
    ----------
    name : str
        The name of the attribute (col_...).
    """
    reason, message = "", f"Функционал для '{name}' недоступен, так как\nранее произошла ошибка при"

    if name == "col_duration":
        reason = "расчете длительности операций"
    elif name == "col_case_success":
        reason = "определении успешных процессов"

    logger.info(f"{message} {reason}")


# TODO comments
def verify_in_enum(value: Any, enum: Type[Enum]):
    # Ensure ..._enum is valid
    enum_values = tuple(member.value for member in enum)

    if value not in enum_values:
        # TODO specific custom exception
        raise ValueError(f"time_errors must be in {enum_values}, got '{value}' instead")


def _read_from_file(path: Path, **reader_arguments: int | str | None) -> DataFrame:
    # Check if the path exists
    try:
        assert path.exists()
    except AssertionError as err:
        raise FileNotFoundError() from err  # TODO message

    suffix_key = path.suffix[1:].upper()

    try:
        reader, *arg_names = FileReaders.__members__[suffix_key].value
    except KeyError as err:  # TODO custom exception, message
        raise ValueError(
            f"Only 'csv', 'xls(x)' and 'txt' file formats are supported, "
            f"but given file path ends with '{path.suffix}'"
        ) from err

    return reader(path, **{name: reader_arguments[name] for name in arg_names})


class SyntheticColumns(str, Enum):
    # ! just names, won't necessarily be present in data
    START_TIME = "start_time (synthetic)"
    END_TIME = "end_time (synthetic)"
    DURATION = "duration (synthetic)"
    CASE_SUCCESS = "case_success (synthetic)"

    def __str__(self) -> str:
        return self.value


class TimeErrors(Enum):
    RAISE = "raise"
    COERCE = "coerce"
    AUTO_CONVERT = "auto_convert"

    def __get__(self, instance: None | DurationManager, owner: TimeErrors | Type[DurationManager]) -> str:
        return self.value

    @classmethod
    def values(cls) -> tuple[str, str, str]:
        return tuple(member.value for member in cls)  # type: ignore[return-value]


class DurationUnits(int, Enum):
    SECOND = 1
    MINUTE = 60
    HOUR = 3600
    DAY = 86400


class FileReaders(Enum):
    XLS = (read_excel, "nrows")
    XLSX = (read_excel, "nrows")
    CSV = (read_csv, "sep", "encoding", "nrows")
    TXT = (read_table, "sep", "encoding", "nrows")


class HolderColumns(Iterable):  # a NamedTuple class
    # * these annotations are not final, and describe the most complete DataHolder use case
    # * just a few of them are expected in a new class instance
    case: str
    stage: str
    start_time: str
    end_time: str
    user: str
    text: str
    duration: str
    case_success: str

    # TODO doc
    def __new__(cls, **all_holder_columns: str) -> NamedTuple:  # type: ignore[misc]
        actual_columns = {
            holder_name[4:]: column  # * skip `col_` in column names
            for holder_name, column in all_holder_columns.items()
            if column is not None
        }

        column_annotations = dict(zip(actual_columns.keys(), repeat(str)))

        return NamedTuple(cls.__name__, **column_annotations)(**actual_columns)  # type: ignore[call-overload]


# ? TODO drop MandatoryColumns from whole lib
class MandatoryColumns(NamedTuple):
    col_case: str | None
    col_stage: str | None
    col_start_time: str | None
    col_end_time: str | None


class SuccessInputs(NamedTuple):
    entries: Iterable[str] = set()
    column: str | None = None


# ? TODO rm
def generate_data_partitions(data: DataFrame, col_case: str, batch_num: int) -> Generator[DataFrame, None, None]:
    """
    Return a generator of data frames representing partitions of the original data frame.

    Args:
        data (DataFrame): The DataFrame to partition.
        col_case (str): The name of the column containing the ID used to group rows.
        batch_num (int): The number of partitions to create.

    Yields:
        DataFrame: Each partition of the original data frame.
    """
    # Calculate the possible start indices for each partition
    possible_start_indices = linspace(0, data.shape[0], num=batch_num + 1, dtype=int)[:-1]
    # Find the indices where the ID column changes (i.e., where a new group starts)
    where_id_changes = data.index[data[col_case] != data[col_case].shift(1)]
    # Pick indices from possible_start_indices but closest to the beginnings of the event traces
    correct_start_indices = where_id_changes[searchsorted(where_id_changes, possible_start_indices, side="left")]
    # Prevent duplicate indices (possible with two possible_start_indices in a single trace)
    correct_start_indices = unique(correct_start_indices)

    # Select data slice based on start indices and yield each partition
    for num in range(len(correct_start_indices) - 1):
        yield data.iloc[correct_start_indices[num] : correct_start_indices[num + 1]]

    # Yield the final partition, which goes from the last correct_start_index to the end of the data
    yield data.iloc[correct_start_indices[-1] :]
