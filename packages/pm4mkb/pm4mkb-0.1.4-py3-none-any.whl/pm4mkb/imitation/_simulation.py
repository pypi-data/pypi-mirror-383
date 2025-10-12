from __future__ import annotations
from functools import partialmethod
from random import choices
from typing import TYPE_CHECKING

from dataclassy import dataclass

from numpy import array, exp, float64, log, mean, nan_to_num, ravel, sum as np_sum, unique, zeros_like
from numpy.random import normal, seed as set_random_state
from pandas import DataFrame, Series, crosstab, to_timedelta
from scipy.stats import gaussian_kde

from tqdm.notebook import tqdm

from pm4mkb.baza import DataHolder
from pm4mkb.imitation._utils import apply_gaussian_mixture, smooth_duration_by_activity
from pm4mkb.metrics import ActivityMetric, TraceMetric, TransitionMetric


if TYPE_CHECKING:
    from numpy import int64
    from numpy.typing import NDArray
    from pandas import Timestamp

set_random_state(42)  # random state for sklearn
tqdm.__init__ = partialmethod(tqdm.__init__, disable=False)  # able to hide tqdm progress


@dataclass(slots=True)
class Simulation:
    # TODO docstring
    data_holder: DataHolder

    _activity_mutation_data: DataFrame = None
    _action_duration: dict[str, NDArray[float64]] = None
    _transition_duration: dict[tuple[str], NDArray[float64]] = None
    _union_duration: dict[str | tuple[str], NDArray[float64]] = None
    _cross_tab: DataFrame = None

    _result: DataFrame = None
    _mean_action_duration: float64 = None
    _mean_transition_duration: float64 = None
    _start_timestamp_traces: list[dict[str, int | float | str | list[str] | Timestamp]] = []
    _col_trans_duration: str = "transition"

    __inter_start: NDArray = array([])  # TODO subtype, replace array
    __node_dict: dict = {}  # TODO type, defaultdict
    __time_like_nodes: dict = {}  # TODO type, defaultdict

    def __post_init__(self):
        self._activity_mutation_data = self._assign_end_activity_by_process()
        self._action_duration = self._sample_approx_activities_duration()

        self._check_for_transitions()

        if self._col_trans_duration is not None:
            self._transition_duration = self._sample_approx_transition_duration()
            self._union_duration = {**self._action_duration, **self._transition_duration}
        else:
            self._union_duration = {**self._action_duration}

        self._cross_tab = self._get_cross_tab()

        self._recalculate_cross_tab_probabilities()

    # TODO refactor
    def generate(self, iterations=100, start_time=None):
        """
        Generate and save process traces, start_time and duration for every action,

        Parameters
        ----------
        iterations : int
            number of traces
        """
        self.__node_dict = self._cross_tab_to_dict()
        self.__inter_start = self._calc_inter_start_rate(iterations - 1)

        initial_start_time = start_time if start_time is not None else min(self.data_holder.start_time)
        if self._col_trans_duration is None:
            trace_choicer = self._without_transition_choice
        else:
            trace_choicer = self._with_transition_choice

        # ? TODO tuple
        self._start_timestamp_traces = [
            dict(
                col_case=0,
                trace=trace_choicer("start", []),
                col_start_time=initial_start_time,
                col_duration=None,
            ),
            *[
                dict(
                    col_case=iteration,
                    trace=trace_choicer("start", []),
                    col_start_time=initial_start_time
                    + to_timedelta(
                        self.__inter_start[iteration - 1],
                        unit="s",
                        errors="coerce",
                    ),
                    col_duration=None,  # ? TODO move None duration closer to use
                )
                for iteration in tqdm(range(1, iterations))
            ],
        ]

        self._result = DataFrame()  # reset _result every generate run

    def get_result(self):
        """
        Convert result to dataframe (in early not converted) and return result

        Returns
        -------
            results : DataFrame, column as in init data_holder
        """
        if self._result.empty:
            self._convert_result_to_df()

        return self._result

    def swap_nodes(self, node_first, node_second, save_probabilities=True):
        """
        Swap nodes in process graph, swap nodes names, action duration and edge probabilities
        (optional)

        Parameters
        ----------
            node_first : str
            node_second : str
            save_probabilities : bool
                if False swap nodes and probabilities of pre-edges
        """
        if node_first in ["start", "end"] or node_second in ["start", "end"]:
            return

        if (
            node_first in self._cross_tab.index
            and node_second in self._cross_tab.columns
            and not save_probabilities
        ):
            node_first_probs = self._to_prob(self._cross_tab[node_first].values)
            node_second_probs = self._to_prob(self._cross_tab[node_second].values)
            mean_first = mean(node_first_probs)
            mean_second = mean(node_second_probs)

            for prob_idx, node in enumerate(self._cross_tab.index):
                self._add_edge(node, node_first, node_second_probs[prob_idx] * mean_first)
                self._add_edge(node, node_second, node_first_probs[prob_idx] * mean_second)

        self._cross_tab.rename({node_first: node_second, node_second: node_first}, axis=0, inplace=True)
        self._cross_tab.rename({node_second: node_first, node_first: node_second}, axis=1, inplace=True)
        self._recalculate_cross_tab_probabilities()

    def add_node(self, new_node, nodes, probabilities, mean_time=None, time_like=None, side="both"):
        """
        Add node and connect it with other nodes to process graph

        Parameters
        ----------
            new_node : str
            nodes : list of str
            probabilities : list of float
                Probability of transition from new_node to target node
            mean_time: TODO
            time_like: TODO
            side : str
                'right', 'left' or 'both'
        """
        if time_like in self._cross_tab.columns:
            self.__time_like_nodes[new_node] = time_like

        self._add_node_to_cross_tab(new_node, mean_time)

        for probability, node in zip(probabilities, nodes):
            self.add_edge(new_node, node, probability, side)

        self._recalculate_cross_tab_probabilities()

    def delete_node(self, node, save_con=True):
        """
        Delete node from graph

        Parameters
        ----------
            node : str
            save_con : bool
                If True, all edges in node, reconnect to all out edges from node
        """
        if save_con:
            self._del_node_create_connections(node)

        self._del_node_from_cross_tab(node)
        self._recalculate_cross_tab_probabilities()

    def add_edge(self, node_first, node_second, prob=0.5, side="right") -> None:
        """
        Add edge, set probability and recompute all probabilities

        Parameters
        ----------
            node_first : str
            node_second : str
            prob : float
                Probability to transition from node to node
            one_side : str
                determines the direction of connection
        """
        # TODO function for each_case
        if side == "right":
            self._add_edge(node_first=node_first, node_second=node_second, prob=prob)
        elif side == "left":
            self._add_edge(node_first=node_second, node_second=node_first, prob=prob)
        else:
            self._add_edge(node_first=node_second, node_second=node_first, prob=prob)
            self._add_edge(node_first=node_first, node_second=node_second, prob=prob)

        self._recalculate_cross_tab_probabilities()

    def delete_edge(self, node_first, node_second, side="right"):
        """
        Delete edge

        Parameters
        ----------
            node_first : str
            node_second : str
            one_side : str
                determines the direction of connection
        """
        self._del_edge(node_first, node_second)

        # TODO function for each_case
        if side == "right":
            self._del_edge(node_first, node_second)
        elif side == "left":
            self._del_edge(node_first=node_second, node_second=node_first)
        else:
            self._del_edge(node_first=node_first, node_second=node_second)
            self._del_edge(node_first=node_second, node_second=node_first)

        self._recalculate_cross_tab_probabilities()

    def delete_loop(self, node):
        """
        Easy delete self cycle edge from process graph

        Parameters
        ----------
            node : str
                node with self cycle
        """
        self.delete_edge(node, node)
        self._recalculate_cross_tab_probabilities()

    def add_loop(self, node, prob=0.5):
        """
        Easy add self cycle edge to process graph

        Parameters
        ----------
            node : str
            prob : float
        """
        self.add_edge(node, node, prob)
        self._recalculate_cross_tab_probabilities()

    def delete_all_loops(self):
        """Delete all loops (self cycles) from process graph"""
        for node in set(self._cross_tab.columns) - {"start", "end"}:
            self._del_edge(node, node)

        self._recalculate_cross_tab_probabilities()

    def change_edge_probability(self, node_first, node_second, new_prob=0):
        """
        Change prob for edge in process graph

        Parameters
        ----------
            node_first : str
                node from edge
            node_second : str
                node to edge
            new_prob : float
                new probability for edge
        """
        self._add_edge(node_first, node_second, new_prob)
        self._recalculate_cross_tab_probabilities()

    def scale_time_node(self, node, scale=1) -> None:
        """
        Change time for activity

        Parameters
        ----------
            node : str
            scale : float
                number
        """
        if node not in self._union_duration.keys():
            return

        self._union_duration[node] = self._union_duration[node] * scale

    def scale_time_edge(self, node_first, node_second, scale=1) -> None:
        """
        Change time for activity

        Parameters
        ----------
            node_first : str
            node_second : str
            scale : float
                number
        """
        edge = f"{node_first} -> {node_second}"

        if edge not in self._union_duration.keys():
            return

        self._union_duration[edge] = self._union_duration[edge] * scale

    def get_probabilities_tab(self):  # TODO rename tab
        """Return cross tab"""
        return self._cross_tab

    def _check_for_transitions(self) -> None:
        """"""
        if not self.data_holder.has_both_times:
            self._col_trans_duration = None

    # TODO speed up, no recursion - too many calls plus appending
    # ~10 times number of iterations * 10 - 100 microseconds
    def _without_transition_choice(self, start_node, trace):
        """
        Recursively constructs a chain of activities.

        Parameters
        ----------
            start_node: str
                Node from which the transition will take place.
            trace: list of str
                Part of the process path to which node are added

        Returns
        -------
            trace: list of str
                Simulated event trace.
        """
        next_node = choices(
            list(self.__node_dict[start_node].keys()), weights=list(self.__node_dict[start_node].values())
        )[0]

        if next_node == "end":
            return trace

        trace.append(next_node)

        return self._without_transition_choice(next_node, trace)

    def _with_transition_choice(self, start_node: str, trace):
        """"""
        next_node = choices(
            list(self.__node_dict[start_node].keys()), weights=list(self.__node_dict[start_node].values())
        )[0]

        if next_node == "end":
            return trace

        trace.extend([f"{start_node} -> {next_node}", next_node])

        return self._with_transition_choice(next_node, trace)

    def _add_edge(self, node_first, node_second, prob):
        # TODO function for duplication
        if (node_first in self._cross_tab.index and node_second in self._cross_tab.columns) or (
            node_first in self._cross_tab.columns and node_second in self._cross_tab.index
        ):
            self._cross_tab.at[node_first, node_second] = prob

    def _del_edge(self, node_first, node_second):  # ? TODO rename different of delete_edge
        # TODO function for duplication
        if (node_first in self._cross_tab.index and node_second in self._cross_tab.columns) or (
            node_first in self._cross_tab.columns and node_second in self._cross_tab.index
        ):
            self._cross_tab.at[node_first, node_second] = 0

    def _del_node_create_connections(self, node):
        # TODO function for duplication
        if (node in self._cross_tab.columns) and (node not in ["start", "end"]):
            del_node_col = self._cross_tab.loc[node]
            value_node_row = self._cross_tab[node]

            for node_value, tab_index in zip(value_node_row, self._cross_tab.index):
                self._cross_tab.loc[tab_index] = (
                    del_node_col * node_value + self._cross_tab.loc[tab_index]
                ).values

    def _del_node_from_cross_tab(self, node):
        # TODO function for duplication
        if (node in self._cross_tab.columns) and (node not in ["start", "end"]):
            self._cross_tab.drop(node, inplace=True)
            self._cross_tab.drop(columns=[node], inplace=True)

    def _add_node_to_cross_tab(self, node, mean_time):
        if (node not in self._cross_tab.columns) and (node not in ["start", "end"]):
            self._cross_tab.loc[node] = 0
            self._cross_tab[node] = 0

            if mean_time:
                self._union_duration[node] = array([mean_time])

    def _cross_tab_to_dict(self) -> dict:
        """
        Converts crosstab to dict, for use when generating a process

        Returns
        -------
            nodes_to_probs : dict(str : np.array(str, float))
                Dictionary of transitions from node to other nodes with probabilities
        """
        return self._cross_tab.T.to_dict()

    def _get_cross_tab(self) -> DataFrame:
        """
        Generate adjacency matrix

        Returns
        -------
            cross_tab : DataFrame
                Adjacency matrix
        """
        unique_actions = list(unique(self.data_holder.stage)) + [
            "start",
            "end",
        ]

        cross_tab = crosstab(unique_actions, unique_actions) * 0
        mask = self._activity_mutation_data.groupby(
            by=[self.data_holder.col_stage, self.data_holder.col_stage + "_next"]
        )[self.data_holder.col_duration].count()

        for index in mask.index:
            cross_tab.at[index] = mask[index]

        cross_tab.drop(columns="start", inplace=True)
        cross_tab.drop("end", inplace=True)

        return cross_tab

    def _convert_result_to_df(self):
        """
        Add duration and start_timestamp to generated data, calculates the time for
        each stage of the process and records its date, converts the date format

        Returns
        -------
            result : DataFrame, columns as in init data_holder
        """
        if not self._start_timestamp_traces:
            return ValueError('To start, use the "generate" function.')

        self._result = DataFrame(self._start_timestamp_traces).explode("trace")

        self._result["col_duration"] = (
            self._result.groupby(self._result.trace)
            .col_duration.transform(
                lambda trace_by_action: self._get_duration_array(trace_by_action.name, len(trace_by_action))
            )
            .values
        )  # TODO check if done

        # TODO speed up
        self._result["tmp"] = self._result.groupby("col_case").col_duration.cumsum().shift(1)

        start_act_mask = self._result.col_case == self._result.col_case.shift(1)
        self._result.loc[start_act_mask, "col_start_time"] = self._result[start_act_mask][
            "col_start_time"
        ] + to_timedelta(self._result[start_act_mask].tmp, unit="s", errors="coerce")

        self._result["col_end_time"] = self._result.col_start_time.shift(-1)
        end_act_mask = self._result.col_case != self._result.col_case.shift(-1)
        self._result.loc[end_act_mask, "col_end_time"] = self._result[end_act_mask][
            "col_start_time"
        ] + to_timedelta(self._result[end_act_mask].col_duration, unit="s", errors="coerce")

        try:
            self._result["col_start_time"] = self._result.col_start_time.dt.strftime(self.data_holder.time_format)
            self._result["col_end_time"] = self._result.col_end_time.dt.strftime(self.data_holder.time_format)
        except AttributeError:  # FIXME suspicious hardcode
            self._result["col_start_time"] = self._result.col_start_time.dt.strftime("%Y-%m-%d %H:%M:%S")
            self._result["col_end_time"] = self._result.col_end_time.dt.strftime("%Y-%m-%d %H:%M:%S")

        self._result.rename(
            columns=dict(
                col_case=self.data_holder.col_case,
                trace=self.data_holder.col_stage,
                col_start_time=self.data_holder.col_start_time,
                col_end_time=self.data_holder.col_end_time,
                col_duration=self.data_holder.col_duration,
            ),
            inplace=True,
        )

        # this allows you to generate similar breaks in duration (strongly affects the
        # time series prediction, because in gsp module Nan convert to 0)
        if self.data_holder.col_start_time is not None and self.data_holder.col_end_time is not None:
            self._result.drop(columns=["tmp"], inplace=True)  # TODO refactor
        else:
            self._result.drop(columns=["tmp", "col_duration"], inplace=True)  # TODO refactor

        self._result = self._result[~self._result[self.data_holder.col_stage].str.contains("->")]

        self._result.reset_index(drop=True, inplace=True)

    # TODO refactor
    def change_edges_probabilities(self, probabilities_dict: dict, edges=False):
        """Only for timed what-if, non stable"""
        if not edges:
            cross_tab_nodes = [
                *filter(
                    lambda node: node in self._cross_tab,
                    probabilities_dict,
                )
            ]

            self._cross_tab[cross_tab_nodes] *= tuple(map(abs, probabilities_dict))
        else:
            for first_node in probabilities_dict:
                bound_second_nodes = [
                    *filter(
                        lambda second_node: second_node in self._cross_tab,
                        probabilities_dict[first_node],
                    )
                ]

                self._cross_tab.loc[
                    first_node,
                    bound_second_nodes,
                ] *= tuple(map(abs, probabilities_dict[first_node].values()))

        self._recalculate_cross_tab_probabilities()

    def _recalculate_cross_tab_probabilities(self):
        """Recalculates the transition probabilities when the process structure changes."""
        if len(self._cross_tab) >= 2:
            self._cross_tab.at["start", "end"] = 0

        for col in self._cross_tab.index:
            self._cross_tab.loc[col] = self._to_prob(self._cross_tab.loc[col].values)

    def _to_prob(self, cross_tabulation_array: NDArray[int64]) -> NDArray[int64]:
        to_prob = np_sum(cross_tabulation_array)

        return cross_tabulation_array / to_prob if to_prob else zeros_like(cross_tabulation_array)

    def _assign_end_activity_by_process(self) -> DataFrame:
        """
        Adds 'end_event' (and its zero time duration) to the traces in the event log.

        Returns
        -------
            supp_data : pandas.DataFrame
                Modified log data with 'end_event', columns: [activity column (str),
                time duration column (float (minutes)]
        """
        transition_durations_data = self.data_holder.data[
            [self.data_holder.col_case, self.data_holder.col_stage, self.data_holder.col_duration]
        ]
        # Use assign operation to avoid SettingWithCopyWarning
        transition_durations_data = transition_durations_data.assign(
            **{
                self._col_trans_duration: (
                    self.data_holder.start_time.shift(-1) - self.data_holder.end_time
                ).dt.total_seconds()
            }
        )
        transition_mask = self.data_holder.case != self.data_holder.case.shift(-1)
        transition_durations_data.loc[transition_mask, self._col_trans_duration] = 0

        supp_data = (
            transition_durations_data.groupby(self.data_holder.col_case)
            .agg(
                {
                    self.data_holder.col_stage: tuple,
                    self.data_holder.col_duration: tuple,
                    self._col_trans_duration: tuple,
                }
            )
            .reset_index()
        )
        supp_data_length = len(supp_data)

        supp_data["act_end"] = [("end",)] * supp_data_length
        supp_data["act_start"] = [("start",)] * supp_data_length
        supp_data["time_end"] = [(0,)] * supp_data_length
        supp_data["time_start"] = [(0,)] * supp_data_length

        supp_data[self.data_holder.col_stage] = (
            supp_data["act_start"] + supp_data[self.data_holder.col_stage] + supp_data["act_end"]
        )
        supp_data[self.data_holder.col_duration] = (
            supp_data["time_start"] + supp_data[self.data_holder.col_duration] + supp_data["time_end"]
        )
        supp_data[self._col_trans_duration] = (
            supp_data["time_start"] + supp_data[self._col_trans_duration] + supp_data["time_end"]
        )

        supp_data = (
            supp_data[
                [
                    self.data_holder.col_case,
                    self.data_holder.col_stage,
                    self.data_holder.col_duration,
                    self._col_trans_duration,
                ]
            ]
            .apply(Series.explode)
            .reset_index(drop=True)
        )
        supp_data[self.data_holder.col_duration] = supp_data[self.data_holder.col_duration].fillna(0)
        supp_data[self._col_trans_duration] = supp_data[self._col_trans_duration].fillna(0)
        supp_data[self.data_holder.col_stage + "_next"] = supp_data[self.data_holder.col_stage].shift(-1)

        return supp_data

    def _sample_approx_activities_duration(self) -> dict[str, NDArray[float64]]:
        """
        Calculate the approximate and mean_time duration of activities.
        GaussianMixture - function consisting of gaussian functions, the generated distribution +-
        adjusts to the combination of gaussian functions

        Returns
        -------
            acts_duration : dict of {str : numpy.array of float}
                Key: node, value: array of probable time durations.
        """
        duration_activity_grouped = self._activity_mutation_data.groupby(self.data_holder.col_stage)[
            self.data_holder.col_duration
        ]
        smoothed_time_series = duration_activity_grouped.apply(smooth_duration_by_activity)

        unique_amount = duration_activity_grouped.nunique(dropna=True)  # at least two unique non-na durations
        duration_by_activity_series, single_duration_by_activity_series = (
            smoothed_time_series[unique_amount > 1].apply(apply_gaussian_mixture),
            smoothed_time_series[unique_amount <= 1],
        )

        self._mean_action_duration = mean(duration_by_activity_series.map(mean))

        return {**dict(single_duration_by_activity_series), **dict(duration_by_activity_series)}

    def _sample_approx_transition_duration(self) -> dict[str, NDArray[float64]]:
        """"""
        duration_transition_grouped = self._activity_mutation_data.groupby(
            [self.data_holder.col_stage, self.data_holder.col_stage + "_next"]
        )[self._col_trans_duration]

        smoothed_time_series = duration_transition_grouped.apply(smooth_duration_by_activity)

        unique_amount = duration_transition_grouped.nunique(dropna=True)
        duration_by_transition_series, single_duration_by_transition_series = (
            smoothed_time_series[unique_amount > 1].apply(apply_gaussian_mixture),
            smoothed_time_series[unique_amount <= 1],
        )

        self._mean_transition_duration = mean(duration_by_transition_series.map(mean))
        multi_keyed_dict = {**dict(single_duration_by_transition_series), **dict(duration_by_transition_series)}

        return {f"{key[0]} -> {key[1]}": item for key, item in multi_keyed_dict.items()}

    def _get_duration_array(self, node, size, zeroing_additive: float = 1e-05) -> array:
        """
        Generate numpy array duration of action used origin data (if new node +
        like_node='node' -> use duration data from origin data for generate new scaling duration

        Parameters
        ----------
            node : str
                node for which the time is generated
            size : int
                shape for compresses or generate gaussian data time

        Returns
        -------
            duration : np.array
        """
        if node not in self._union_duration:
            if isinstance(node, tuple):
                return normal(
                    loc=self._mean_transition_duration, scale=self._mean_transition_duration**0.5, size=size
                )
            return normal(loc=self._mean_action_duration, scale=self._mean_action_duration**0.5, size=size)

        if len(self._union_duration[node]) == 1:
            if node not in self.__time_like_nodes:
                self._union_duration[node] = normal(1, 0.1, size + 1) * self._union_duration[node]
            else:
                mean_time_scale = (
                    mean(self._union_duration[self.__time_like_nodes[node]]) / self._union_duration[node]
                )
                self._union_duration[node] = self._union_duration[self.__time_like_nodes[node]] * mean_time_scale

        smoothed_dur = log(self._union_duration[node] + zeroing_additive)
        nan_to_num(smoothed_dur, copy=False, nan=0)

        if all(smoothed_dur[0] == smoothed_dur):
            smoothed_dur = normal(smoothed_dur[0], zeroing_additive, smoothed_dur.size)

        kde = gaussian_kde(dataset=smoothed_dur, bw_method="scott")

        return exp(kde.resample(size)[0])

    def _calc_inter_start_rate(self, size: int, zeroing_additive: float = 1e-05) -> NDArray[float64]:
        """
        Generates intervals similar to the original between the start of processes,
        compresses the sample to the number of generations (size)

        Parameters
        ----------
            size : int
                shape for compresses data

        Returns
        -------
            start_timestamps: numpy.array of float, shape=[iterations from generate func].
                Time duration in seconds.
        """
        start_timestamp_mask = self.data_holder.case != self.data_holder.case.shift(1)
        start_timestamps_s_numpy = self.data_holder.start_time[start_timestamp_mask].dropna().values
        start_timestamps_s = Series(start_timestamps_s_numpy)
        time_periods_s = max(start_timestamps_s) - start_timestamps_s
        time_periods_s.dropna(inplace=True)
        time_periods_s = time_periods_s.apply(lambda x: x.total_seconds())
        kde = gaussian_kde(dataset=log(time_periods_s + zeroing_additive), bw_method="scott")

        return ravel(exp(kde.resample(size)[0]))

    def compute_metric(self, target="activity"):
        """
        Calculates metric (transition, activity or trace), used pm4mkb functional

        Parameters
        ----------
            target: {'transitions', 'activities', 'trace'}, default='activity'

        Returns
        -------
            transition_metric : TransitionMetric
                OR
            activity_metric : ActivityMetric
                OR
            trace_metric : TraceMetric
        """
        selected_metric = None
        if target == "activity":
            selected_metric = ActivityMetric(self.get_data_holder_result())
        elif target == "transition":
            selected_metric = TransitionMetric(self.get_data_holder_result())
        elif target == "trace":
            selected_metric = TraceMetric(self.get_data_holder_result())

        if selected_metric is not None:
            selected_metric.apply()
            return selected_metric

        return ValueError(f'Expected "activity", "transition" or "trace", but got "{target}" instead.')

    def get_data_holder_result(self) -> DataHolder:  # ? TODO better name
        return self._create_holder_like(self.get_result(), self.data_holder)

    def _create_holder_like(self, data: DataFrame, holder_like: DataHolder):
        return DataHolder(
            data=data,
            col_case=holder_like.col_case,
            col_stage=holder_like.col_stage,
            col_start_time=holder_like.col_start_time,
            col_end_time=holder_like.col_end_time,
        )
