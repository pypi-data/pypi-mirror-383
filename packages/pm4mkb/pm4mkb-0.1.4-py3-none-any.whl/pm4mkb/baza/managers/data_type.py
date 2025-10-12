from __future__ import annotations
from typing import TYPE_CHECKING, Iterable

from pandas import to_numeric
from pdcast import downcast


if TYPE_CHECKING:
    from pandas import DataFrame, Index, Series, StringDtype


class DTypeManager:
    data: DataFrame

    __slots__ = __annotations__

    def __init__(self, data) -> None:
        """

        Parameters
        ----------
        data : pandas.DataFrame
            The data obtained through DataHolder initialization.
        """
        self.data = data

    def adjust_data_types(self) -> None:
        """
        Adjusts the data types of the given data frame to reduce memory consumption.

        Following data types are possible after all:
        - string
        - number
        - datetime
        - bool
        - category
        """
        # Adjust remaining numeric data
        # use columns of the object dtype - presume some of raw <the-dtype> data columns
        # were misinterpreted by the reader as an object
        self._cast_to_numeric(self._object_columns)

        # downcast numeric dtypes, bool cast possible
        # but keep objects
        for column in self.data:
            self.data[column] = downcast(self.data[column], numpy_dtypes_only=True)

        # Adjust remaining string data
        # use columns of the object dtype that are not numeric or categorical
        self._cast_to_string(self._object_columns)

    @property
    def _object_columns(self) -> Index[str]:
        """
        Get all columns in the data that have the object dtype, except for datetime dtype columns.

        Returns
        -------
            An Index of `object` column names
        """
        # ! note that DataHolder datetime columns are excluded -
        # - already converted with `adjust_datetime`
        return self.data.select_dtypes("object").columns

    def _cast_to_numeric(self, columns: Iterable[str]) -> None:
        """
        Cast certain columns in the data to numeric dtype.

        Parameters
        ----------
        columns : Iterable[str]
            Column names to cast to the numeric dtype
        """
        # seems OK, if auxillary datetime columns are converted to timestamp
        self.data[columns] = self.data[columns].transform(to_numeric, errors="ignore")

    def _cast_to_string(self, columns: Iterable[str]) -> None:
        """
        Cast certain columns in the data to string[pyarrow] dtype.

        Parameters
        ----------
        data : DataFrame
            The data to cast columns in
        columns : Iterable[str]
            Column names to cast to the string dtype
        """

        def to_pyarrow_string(series: Series) -> Series[StringDtype(storage="pyarrow")]:  # noqa: F821
            return series.astype("string[pyarrow]")

        # seems OK, if actual object columns (tuple, array, e.t.c.) are converted to string
        self.data[columns] = self.data[columns].transform(to_pyarrow_string)
