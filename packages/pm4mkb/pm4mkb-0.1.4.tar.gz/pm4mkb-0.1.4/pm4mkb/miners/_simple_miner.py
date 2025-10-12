from __future__ import annotations

from pm4mkb.baza import DataHolder
from pm4mkb.miners._abstract_miner import AbstractMiner
from pm4mkb.visual._graph import Graph, create_dfg


class SimpleMiner(AbstractMiner):
    """
    Realization of a simple miner algorithm that creates all edges that exist
    according to the event log (no filtration is performed).

    Parameters
    ----------
    data_holder : DataHolder
        Object that contains the event log and the names of its necessary columns.

    Examples
    --------
    >>> import pandas as pd
    >>> from pm4mkb.baza import DataHolder
    >>> from pm4mkb.miners import SimpleMiner
    >>>
    >>> # Create data_holder
    >>> df = pd.DataFrame({
    ...     'col_case': [1, 1, 2],
    ...     'col_stage':['st1', 'st2', 'st1'],
    ...     'dt_column':[123456, 123457, 123458]})
    >>> data_holder = DataHolder(df, 'col_case', 'col_stage', 'dt_column')
    >>>
    >>> miner = SimpleMiner(data_holder)
    >>> miner.apply()
    """

    def __init__(self, data_holder: DataHolder):
        super().__init__(data_holder)

    def apply(self):
        """
        Starts the calculation of the graph using the miner.
        """
        unique_activities = self._data_holder.unique_stages
        follows_pairs = super()._get_follows_pairs()

        graph = create_dfg()
        super().create_act_nodes(graph, unique_activities)
        super().create_start_end_events_and_edges(graph, *super()._get_first_last_activities())
        self.create_edges(graph, follows_pairs)
        self.graph = graph

    @staticmethod
    def create_edges(graph, pairs):
        """
        Adds edges between transitions to the graph.

        Parameters
        ----------
        graph: Graph
            Graph.

        pairs: list of tuple(str, create_start_end_events_and_edgesstr)
            Pairs of activities that have causal relation.
        """
        for pair in pairs:
            graph.add_edge(pair[0], pair[1])


def simple_miner(data_holder: DataHolder) -> Graph:
    """
    Realization of a simple miner algorithm that creates all edges that exist
    according to the event log (no filtration is performed).

    Parameters
    ----------
    data_holder : DataHolder
        Object that contains the event log and the names of its necessary columns.

    Returns
    -------
    graph : Graph

    """
    miner = SimpleMiner(data_holder)
    miner.apply()
    return miner.graph
