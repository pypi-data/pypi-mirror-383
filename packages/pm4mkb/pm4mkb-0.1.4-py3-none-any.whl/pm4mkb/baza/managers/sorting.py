from __future__ import annotations
from typing import TYPE_CHECKING, Iterable, TypedDict

from loguru import logger

from pandas import Series

from pm4mkb.baza import SyntheticColumns


if TYPE_CHECKING:
    from pandas import DataFrame
    from pm4mkb.baza import HolderColumns


class SortingColumns(TypedDict):  # ? TODO move utils / annotations
    case: str
    start_time: str
    end_time: str
    stage: str


class SortingManager:
    SORTING_NAMES = ("case", "start_time", "end_time", "stage")

    columns_to_sort: Iterable[str]
    sorting_columns: SortingColumns

    __slots__ = __annotations__

    # TODO HolderColumns annotation
    def __init__(self, holder_columns: HolderColumns, data: DataFrame) -> None:
        """
        Sort the DataHolder event data in order of `SORTING_NAMES` (by case ID, timestamp start to
        end, stage).

        Some columns may be missing in the data, they will be filtered down to `columns_to_sort`.
        """
        self.sorting_columns = SortingColumns()
        self.__select_columns_to_sort(holder_columns, data)
        self.__verify_has_enough_columns(holder_columns)

    def sort_event_data(self, data: DataFrame) -> None:
        """
        Sorts the given event data based on the `columns_to_sort` attribute columns of the instance,
        resets the index of the sorted DataFrame to restore the range index.

        Parameters
        ----------
        data : pandas.DataFrame
            The event data to sort
        """
        # sort data based on the given sorting columns
        data.sort_values(self.columns_to_sort, inplace=True)
        # reset index of the sorted data (restore range index)
        data.reset_index(drop=True, inplace=True)

    # TODO HolderColumns annotation
    def __select_columns_to_sort(self, holder_columns: Iterable[str], data: DataFrame) -> None:
        """
        Select all the available DataHolder columns for event data to be sorted by. Sorting columns
        comply the order of `SORTING_NAMES` class attribute.

        Parameters
        ----------
        holder_columns : Iterable[str]
            A named tuple containing the names of PM-specific columns
            passed by the user in `DataHolder` initialization.
        data : pandas.DataFrame
            The event data to sort
        """
        # first of all, get columns the user passed in the DataHolder, as they are
        for name in self.SORTING_NAMES:
            self.sorting_columns[name] = getattr(holder_columns, name, None)
        # Time ones of the `holder_columns` may be None or wrong synthetic
        # `calculate_duration` method call could have created / deleted them
        for synthetic_column in (SyntheticColumns.START_TIME, SyntheticColumns.END_TIME):
            name = synthetic_column.name.lower()
            # do nothing if the column is not synthetic or None, even if there were duration errors
            if self.sorting_columns[name] == synthetic_column or self.sorting_columns[name] is None:
                # otherwise, set synthetic_column or None,
                # depending on presence in the data (duration errors)
                self.sorting_columns[name] = data.get(synthetic_column, default=Series()).name

        # pick actual columns to sort data in the order of `SORTING_NAMES`
        self.columns_to_sort = [*filter(None, self.sorting_columns.values())]  # type: ignore[list-item]

    def __verify_has_enough_columns(self, holder_columns: HolderColumns) -> None:
        """
        Ensure that the selected sorting columns are enough for the DataHolder.
        """
        # * no need for all, actually, if any is None - all is None (synthetic one otherwise)
        if all(self.sorting_columns[name] is None for name in ("start_time", "end_time")):
            logger.info(
                "Не предоставлены данные ни для одной из временных колонок: "
                "начала и конца этапов лога `col_start_time`, `col_end_time`.\n"
                "Сортировка этапов по времени производиться не будет."
            )

            # check the case id column is available
            try:
                holder_columns.case
                # datetime columns are checked already
                # and stage column may be away without causing any harm
            except AttributeError as err:
                # no case id, no timestamp columns - no option to sort records
                # TODO custom exception message
                # FIXME LogWithoutTimestampError
                raise AttributeError(
                    "Невозможно отсортировать ивент лог. "
                    "Отсутствуют временные колонки и колонка экземпляров процесса."
                ) from err
