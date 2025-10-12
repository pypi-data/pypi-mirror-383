from __future__ import annotations
from enum import Enum
from itertools import chain
from typing import Iterable, TYPE_CHECKING

from loguru import logger

from pandas import DataFrame

from pm4mkb.metrics._base_metric import BaseMetric
from pm4mkb.metrics._utils import round_decorator


if TYPE_CHECKING:
    from pm4mkb.baza import DataHolder


class AvailableMetrics(Enum):
    TRACE = {
        "count",
        "ids",
        "trace_length",
        "unique_activities_num",
        "loop_percent",
    }
    USER = {
        "unique_users",
        "unique_users_num",
    }
    DURATION = {
        "total_duration",
        "mean_duration",
        "median_duration",
        "max_duration",
        "min_duration",
        "probability",
        "variance_duration",
        "std_duration",
    }

    @classmethod
    def values(cls) -> Iterable[str]:
        return chain.from_iterable([member.value for member in cls.__members__.values()])


class TraceMetric(BaseMetric):
    """
    Class for calculating metrics for event traces.

    Parameters
    ----------
    data_holder: DataHolder
        Object that contains the event log and the names of its necessary columns.

    time_unit: {'s'/'second', 'm'/'minute', 'h'/'hour', 'd'/'day', 'w'/'week'}, default='day'
        Calculate time/duration values in given format.

    round_: int, default=None
        Round float values of the metrics to the given number of decimals.


    Attributes
    ----------
    metrics: DataFrame
        DataFrame that contains all calculated metrics.
    """

    def __init__(
        self,
        data_holder: DataHolder,
        required_metrics: Iterable[str] = None,
        time_unit: str = "hour",
        round_: int = None,
    ):
        super().__init__(data_holder, time_unit, round_)

        if required_metrics is None:
            self.required_metrics = list(AvailableMetrics.values())
        else:
            # Anyways, need "unique" index then "count" column to sort values
            self.required_metrics = set(["count", *required_metrics])

        if data_holder.col_user is None:
            self._grouped_data = data_holder.group_as_traces()
        else:
            self._grouped_data = data_holder.group_as_traces(data_holder.col_stage, data_holder.col_user)

        duration_df = data_holder.case_groupby[data_holder.col_duration].sum()
        self._grouped_data = self._grouped_data.join(duration_df, on=data_holder.col_case)

        self._group_column = data_holder.col_stage
        self._group_data = self._grouped_data.groupby(self._group_column)
        self._traces = DataFrame({self._dh.col_stage: self._grouped_data[self._dh.col_stage].unique()}).set_index(
            self._dh.col_stage, drop=False
        )[
            self._dh.col_stage
        ]  # pandas.Series

    def apply(self):
        """
        Calculate all possible metrics for this object.

        Returns
        -------
        result: pandas.DataFrame
        """
        # Initialize empty dataframe with an index
        self.metrics = self.empty_unique_traces()

        # Add required from trace metrics
        trace_metrics = AvailableMetrics.TRACE.value.intersection(self.required_metrics)
        for metric_name in trace_metrics:
            self.metrics = self.metrics.join(getattr(self, metric_name)())
        # Add required from user metrics
        user_metrics = AvailableMetrics.USER.value.intersection(self.required_metrics)
        for metric_name in user_metrics:
            if self._dh.col_user is not None:
                self.metrics = self.metrics.join(getattr(self, metric_name)())
            else:
                logger.warning(
                    f"DataHolder instance has no user column. Skipping '{metric_name}' metric calculation"
                )

        # Add required from time metrics
        # TODO implement similar 'required_metrics' in base metric
        # Ignore "probability"
        if any("duration" in name for name in self.required_metrics):
            self.metrics = self.metrics.join(self.calculate_time_metrics(True))

        return self.metrics.sort_values("count", ascending=False)

    def empty_unique_traces(self):
        return DataFrame(index=self._grouped_data[self._dh.col_stage].unique())

    def count(self):
        """
        Return number of occurrences of the trace in the event log.
        (=number of IDs that have the given trace).

        Returns
        -------
        result: pandas.Series
        """
        return self._group_data[self._dh.col_case].count().rename("count")  # or .nunique() - no difference

    def ids(self):
        """
        Return list of IDs that have the given trace (=sequence of activities).

        Returns
        -------
        result: pandas.Series
        """
        return self._group_data.agg({self._dh.col_case: set})[self._dh.col_case].rename("ids")

    def trace_length(self):
        """
        Return length of the trace.

        Returns
        -------
        result: pandas.Series
        """
        return self._traces.apply(len).rename("trace_length")

    def unique_activities(self):
        """
        Return unique activities of the trace.

        Returns
        -------
        result: pandas.Series
        """
        return self._traces.apply(set).rename("unique_activities")

    def unique_activities_num(self):
        """
        Return number of unique activities of the trace.

        Returns
        -------
        result: pandas.Series
        """
        return self._traces.apply(lambda x: len(set(x))).rename("unique_activities_num")

    @round_decorator
    def loop_percent(self):
        """
        Return the percentage of activities in the event trace that occurred
        for the 2nd, 3rd, 4th,... time (percentage of 'extra use' of the activities):

         = (1 - num_of_unique_activities / trace_length) * 100.

        Thus, this value ranges from 0 to 1 (non-including).

        Returns
        -------
        result: pandas.Series
        """
        return ((1 - self.unique_activities_num() / self.trace_length()) * 100).rename("loop_percent")

    def unique_users(self):
        """
        Return set of unique users who worked on the IDs that have given event trace
        (=sequence of activities).

        Returns
        -------
        result: pandas.Series
        """
        return self._group_data[self._dh.col_user].apply(lambda x: set().union(*x)).rename("unique_users")

    def unique_users_num(self):
        """
        Return number of unique users who worked on the IDs that have given event trace
        (=sequence of activities).

        Returns
        -------
        result: pandas.Series
        """
        return self.unique_users().apply(len).rename("unique_users_num")
