from __future__ import annotations

from pandas import Series, DataFrame, merge
from loguru import logger

from pm4mkb.baza import DataHolder
from pm4mkb.miners._abstract_miner import AbstractMiner
from pm4mkb.visual._graph import create_dfg
from pm4mkb.metrics import TransitionMetric, ActivityMetric


class ClusterMiner(AbstractMiner):
    """
    Майнер, группирующий этапы на основе их последовательной совместной встречаемости в логе процесса.
    Алгоритм рекурсивно отбирает активности и переходы исходя из того, что доля переходов из активности должна быть >= заданного
    порога (confidence). Если это условие выполняется, такие цепочки активностей добавляются в один кластер.
    Данный майнер целесообразно использовать для визуализации вариативных процессов, например, клиентских путей.

    Parameters
    ----------
    data_holder: DataHolder
        Класс, который хранит данные
    confidence: float, optional
        Этапы с confidence большей, чем это значение будут сгруппированы. Сonfidence - метрика,
        основанная на количестве переходов из рассматриваемой активности в последующие.
        Чем больше доля переходов относительно всех переходов, тем больше confidence, что два этих этапа принадлежат одному кластеру.
        Значение от 0 (не включая) до 1, где 0 - все возожные объединения будут найдены,
        1 - ни одного объединения не будет, by default 0.5
    transition_benchmark: float, optional
        Метрика, обозначающая долю переходов в рассматриваемый этап, которые будут отфильтрованы перед разметкой кластеров.
        Значение от 0 до 0.5. Чем выше значение, тем большая доля выфильтрованных переходов.
        Например, если значение transition_benchmark == 0.1, это значит, что все переходы,
        доля которых в общем числе переходов в эту активность < 0.1, будут удалены перед кластеризацией
    stages_to_combine: list[str], optional
        Список этапов, которые точно нужно объединить, by default None
    stages_not_to_combine: list[str], optional
        Список этапов, которые точно не нужно объединять, by default None
    """

    def __init__(
        self,
        data_holder: DataHolder,
        confidence: float = 0.5,
        transition_benchmark: float = 0.1,
    ):
        super().__init__(data_holder)

        self.confidence = confidence
        self.transition_benchmark = transition_benchmark
        self._clusters = Series()
        self._results = DataFrame()

    def get_clusters(self):
        if not self._clusters.empty:
            return self._clusters
        return self.apply()

    def get_results(self):
        if not self._results.empty:
            return self._results
        return self.apply()

    def apply(self) -> Series:
        logger.info("Рассчитываем метрики переходов")
        # activity metric preparation
        activity_metric = ActivityMetric(self._data_holder)
        activity_count = activity_metric.count()
        activity_count = activity_count.reset_index().rename(columns={self._data_holder.col_stage: "end"})

        # transition metric preparation
        transition_metric = TransitionMetric(self._data_holder)
        transition_count = transition_metric.count()
        data = DataFrame(
            transition_count.index.to_list(),
            columns=["start", "end"],
            index=transition_count.index,
        )
        data["counter"] = transition_count
        transition_count = data.sort_values(by="counter", ascending=False)

        # merge metrics
        merged_count = merge(left=transition_count, right=activity_count, on="end")
        merged_count["div"] = merged_count["counter"] / merged_count["count"]

        # leave only valuable trasitions
        merged_count = merged_count.loc[merged_count["div"] >= self.transition_benchmark]
        merged_count = merged_count[["start", "end", "counter"]]
        merged_count = merged_count[merged_count.start != merged_count.end]

        logger.info("Ищем похожие переходы")

        list_to_merge = self._find_mergeable(merged_count)

        if list_to_merge != []:
            logger.info("Создаем новый DataHolder")
            self._form_new_dh(list_to_merge)
        else:
            print("Нет возможностей для объединения")

        logger.info("Создаем граф процесса")

        graph = create_dfg()
        follows_pairs = super()._get_follows_pairs()
        super().create_act_nodes(graph, self._data_holder.unique_stages)
        super().create_start_end_events_and_edges(graph, *super()._get_first_last_activities())
        for pair in follows_pairs:
            graph.add_edge(pair[0], pair[1])
        self.graph = graph
        logger.info("Получили кластеры")
        self._results = self._data_holder.data
        return self._results

    def _form_new_dh(self, list_to_merge: list) -> None:
        """
        Form a new data holder by merging the provided list of clusters.

        Parameters
        ----------
        list_to_merge: list
            A list of clusters to merge.
        """
        df = self._data_holder.data.copy()
        to_merge_dict = dict(zip(df[self._data_holder.col_stage], df[self._data_holder.col_stage]))

        # transform list of lists to readable Series
        self._clusters = (
            Series(list_to_merge)
            .explode()
            .rename(self._data_holder.col_stage)
            .reset_index()
            .drop_duplicates(subset=[self._data_holder.col_stage])
            .set_index(self._data_holder.col_stage)["index"]
        )
        to_merge_dict.update(self._clusters.astype(str).add(" кластер").to_dict())
        df["cluster"] = df[self._data_holder.col_stage].map(to_merge_dict)
        self._data_holder = self._data_holder.copy(data=df, col_stage="cluster")

    def _find_component(
        self,
        data: DataFrame,
        component: list,
    ) -> (DataFrame, list):
        """
        Finds a component in the given DataFrame.

        Parameters
        ----------
        data: DataFrame
            The DataFrame to search in.
        component: list
            The list of nodes representing the component.

        Returns:
            Tuple[DataFrame, list]: A tuple containing the updated DataFrame and the updated component list.
        """
        last_node = component[-1]
        transitions = data[data.start == last_node]
        for node in component:
            transitions = transitions[transitions.end != node]
        transitions = transitions[transitions.counter / transitions.counter.sum() >= self.confidence]

        data = data.loc[(data.start != last_node) & (data.end != last_node)]

        if len(data) > 0:
            for node in transitions.end:
                component.append(node)
                data, _ = self._find_component(data, component)
        return data, component

    def _find_mergeable(self, transition_count: DataFrame) -> list:
        """
        Finds and returns a list of mergeable components in the given transition count DataFrame.

        Parameters:
        ----------
            transition_count: DataFrame
                The transition count DataFrame.

        Returns:
            list: A list of mergeable components.
        """
        list_to_merge = []
        trace_count_copy = transition_count.copy()
        while not trace_count_copy.empty:
            trace_count_copy, new_component = self._find_component(
                trace_count_copy,
                trace_count_copy.iloc[0][["start", "end"]].to_list(),  # 0-начало с первой строки датасета
            )
            if len(new_component) > 2:
                list_to_merge.append(new_component)
            trace_count_copy = trace_count_copy.iloc[1:]
        return list_to_merge
