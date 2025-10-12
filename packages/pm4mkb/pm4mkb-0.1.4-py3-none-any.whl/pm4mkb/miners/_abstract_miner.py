from __future__ import annotations

from typing_extensions import Protocol

from pandas import DataFrame, unique

from pm4mkb.visual._types import NodeType  # FIXME partially initialized import


class MiningDataHolder(Protocol):
    @property
    def col_case(self) -> str:
        ...

    @property
    def col_stage(self) -> str:
        ...

    @property
    def data(self) -> DataFrame:
        ...


class AbstractMiner:
    """
    Abstract class for miners.
    Contains fields and methods used by all miners.

    Parameters
    ----------
    data_holder : pm4mkb.baza.DataHolder
        Object that contains the event log and the names of its necessary columns.

    Attributes
    ----------
    data_holder : pm4mkb.baza.DataHolder
        Object that contains the event log and the names of its necessary columns.

    graph: pm4mkb.visual._graph.Graph
        Mined graph of the process.
    """

    def __init__(self, data_holder: MiningDataHolder):
        self._data_holder = data_holder.copy()  # TODO WRONG COPY!!!!!
        self.graph = None

    def _get_first_last_activities(self):
        """
        Returns activities that event traces start and end with.

        Returns
        -------
        first_activities : list of str
            Names of the activities that event traces start with.

        last_activities : list of str
            Names of the activities that event traces end with.
        """
        grouped_frame = self._data_holder.case_groupby[self._data_holder.col_stage]
        first_stages = grouped_frame.head(1)
        last_stages = grouped_frame.tail(1)

        return unique(first_stages), unique(last_stages)

    @staticmethod
    def _get_causal_parallel_pairs(follows_pairs):
        """
        Returns two list of pairs of activities that have causal and parallel relation.

        "activity_1" and "activity_2" have causal relation ("activity_1 -> activity_2") if
            "activity_1 > activity_2" and not "activity_2 > activity_1"
        "activity_1" and "activity_2" have parallel relation ("activity_1 || activity_2") if
            "activity_1 > activity_2" and "activity_2 > activity_1"
        "activity_1 > activity_2" means that "activity_1" is directly followed by "activity_2" in at least
            one event trace in the event log.

        Returns
        -------
        causal_pairs : set of tuples (str, str)
            Pairs (activity_1, activity_2) that have causal relation: "activity_1 -> activity_2"

        parallel_pairs : set of tuples (str, str)
            Pairs (activity_1, activity_2) that have parallel relation: "activity_1 || activity_2"
        """
        causal_pairs = set()
        parallel_pairs = set()
        for pair in follows_pairs:
            if pair[::-1] not in follows_pairs:
                causal_pairs.add(pair)
            elif pair[::-1] in follows_pairs:
                parallel_pairs.add(pair)
        return causal_pairs, parallel_pairs

    def _get_follows_pairs(self):
        """
        Returns set of unique pairs (activity_1, activity_2), where "activity_1" is directly followed
        by "activity_2" in the event log.

        Returns
        -------
        follows_pairs : set of tuples (str, str)
            Unique pairs of activities that present in the event log.
        """
        stages = self._data_holder.stage
        mask = self._data_holder.case == self._data_holder.case.shift(-1)

        return set(zip(stages[mask], stages.shift(-1)[mask]))

    @staticmethod
    def _label_encode_activities(unique_activities):
        """
        Label-encodes the names of the activities.

        Numbers corresponding to the activities will be used as rows/columns
        in a matrix of edges between the activities.

        Returns
        -------
        label_to_name_dict : dict of {int: str}
            Key: numeric label of an activity. Value: name of the activity.

        name_to_label_dict : dict of {str: int}
            Key: name of an activity. Value: numeric label of the activity.
        """
        name_to_label_dict = {}
        label_to_name_dict = {}
        for i, activity_name in enumerate(unique_activities):
            name_to_label_dict[activity_name] = i
            label_to_name_dict[i] = activity_name
        return label_to_name_dict, name_to_label_dict

        # ----------------------------------------------------------------------------------
        # -----------------------------   Graph methods   ----------------------------------
        # ----------------------------------------------------------------------------------

    @staticmethod
    def create_act_nodes(graph, activities):
        """
        Creates nodes for given activities.

        Parameters
        ----------
        graph: pm4mkb.visual._graph.Graph
            Graph.

        activities: list of str
            List of the activities.
        """
        for activity_name in activities:
            graph.add_node(node_id=activity_name, label=activity_name)

    @staticmethod
    def create_start_end_events_and_edges(graph, first_activities, last_activities):
        """
        Creates nodes for activities and two artificial nodes: "start" node and "end" node.
        Creates edges between artificial nodes and first/last transitions (nodes that represent activities).

        Parameters
        ----------
        graph: pm4mkb.visual._graph.Graph
            Graph.

        first_activities: list of str
            The starting activities in one or more event traces.

        last_activities: list of str
            The last activities in one or more event traces.
        """
        graph.add_node(node_id=NodeType.START_EVENT, label="", node_type=NodeType.START_EVENT)
        for first_activity in first_activities:
            graph.add_edge(NodeType.START_EVENT, first_activity)

        graph.add_node(node_id=NodeType.END_EVENT, label="", node_type=NodeType.END_EVENT)
        for last_activity in last_activities:
            graph.add_edge(last_activity, NodeType.END_EVENT)
