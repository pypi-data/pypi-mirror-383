from __future__ import annotations

from typing import TYPE_CHECKING

from dataclassy import dataclass
from loguru import logger
from numpy import mean
from numpy import sum as np_sum
from pandas import DataFrame, MultiIndex, Series, concat
from pandas.api.types import is_float_dtype
from sklearn.preprocessing import minmax_scale

from pm4mkb.baza import Stage

from ._initialized_metrics import initialize_metrics
from .metrics import dh2cycle_metric
from .metrics._annotations import COLUMNS
from .text_data import get_mistake_lemmas_path, get_reversal_lemmas_path

if TYPE_CHECKING:
    from pm4mkb.baza import DataHolder

    from .metrics._base import Metric


@dataclass(slots=True, unsafe_hash=True)
class AutoInsights:
    """
    Autoinsights show problems in the data log.

    Parameters:
        holder(DataHolder): Object that loads, preprocesses
            and contains the event log and names of its columns.
        successful_stage(Optional[str]): activity that represents successful process.
            Defaults to None.
        min_cost(Union[dict, float, int, None]): Minute cost of human work. Defaults to 1.0.
            Allowed formats:
            {stage1: cost_stage1, cost_stage2: cost_stage2, ...}
            {stage1: cost_stage1}
            181.1841
            181
            None
        graph_embedding(bool): whether to use graph embeddings to calculate looping metrics

    Args:
        _bool_insights(DatFrame): True/False for metrics
        _float_insights(DataFrame): [0, 1] for metrics
        _fin_effects(DatFrame): fin effect for metrics


    Examples:
    >>> from pm4mkb.autoinsights import AutoInsights
    >>>
    >>> auto_i = AutoInsights(holder, successful_stage='Stage_8', min_cost=1.0)
    >>> auto_i.apply()
    >>>
    >>> auto_i.bool_insights()
    >>> auto_i.float_insights()
    >>> auto_i.fin_effects()
    >>> auto_i.intersected_loops_wasted_time
    >>> auto_i_for_transitions = auto_i.autoinsights_for_transitions()
    >>> auto_i_for_transitions.apply()
    >>> print(auto_i.fin_effects_summary())
    """

    MISTAKE_LEMMAS_PATH = get_mistake_lemmas_path()
    REVERSAL_LEMMAS_PATH = get_reversal_lemmas_path()
    LOOP_METRIC_NAMES = ("START", "SELF", "ROUNDTRIP", "PING_PONG", "ARBITRARY")

    holder: DataHolder

    min_cost: dict | float | int | None = None
    successful_stage: Stage | None = None
    starting_stage: Stage | None = None  # FIXME unused
    graph_embedding: bool = False

    _unique_stages: list[Stage] = None
    _metrics: dict[str, Metric] = None
    _intersected_loops_metrics: DataFrame = DataFrame()

    _bool_insights: DataFrame = DataFrame()
    _float_insights: DataFrame = DataFrame()
    _fin_effects: DataFrame = DataFrame()

    def __post_init__(self) -> None:
        self.holder = self.holder.copy()

        self._unique_stages = self.holder.unique_stages
        self.min_cost = self.__guarantee_min_cost(unique_act=self._unique_stages, min_cost=self.min_cost)
        self.successful_stage = self.__guarantee_success_activity(self.successful_stage, self.holder)
        self.starting_stage = self.__guarantee_start_activity(self.starting_stage, self.holder)

        self._metrics = initialize_metrics(self)

    def apply(self) -> None:
        self._bool_insights = DataFrame(
            data=False, index=self._unique_stages, dtype=bool, columns=COLUMNS.as_header()
        )
        self._float_insights = DataFrame(
            data=0, index=self._unique_stages, dtype=float, columns=COLUMNS.as_header()
        )
        self._fin_effects = DataFrame(data=0, index=self._unique_stages, dtype=float, columns=COLUMNS.as_header())

        loop_metrics = (self._metrics[metric_name] for metric_name in self.LOOP_METRIC_NAMES)
        for metric in loop_metrics:
            metric.intersections = True
            metric.apply()
            self._intersected_loops_metrics[metric.column[1]] = metric._fin_effects()
            metric.intersections = False

        for metric in self._metrics.values():
            metric.apply()
            self._float_insights[metric.column] = metric.float_insights
            self._bool_insights[metric.column] = metric.bool_insights
            self._fin_effects[metric.column] = metric.fin_effects

        if self.graph_embedding:
            self._bool_insights.update(dh2cycle_metric(self.holder) > 0)
        self._float_insights = self._float_insights.fillna(0.0)

        self._float_insights = DataFrame(
            minmax_scale(self._float_insights.values),
            columns=self._float_insights.columns,
            index=self._float_insights.index,
        )
        anomaly_level = self._float_insights.mean(axis=1)
        anomaly_level = DataFrame(
            minmax_scale(anomaly_level.values),
            index=self._float_insights.index,
            columns=MultiIndex.from_tuples(
                [("", "Уровень аномальности")], names=self._float_insights.columns.names
            ),
        )

        self._float_insights = concat(
            [self._float_insights, anomaly_level],
            axis=1,
        )

        if self.graph_embedding:
            self._fin_effects.update(dh2cycle_metric(self.holder))
        self._fin_effects.update(
            self._fin_effects[self._fin_effects.select_dtypes(include=["number"]).columns]
            .multiply(Series(self.min_cost) / 60, axis=0)
            .fillna(0.0)
        )

        self._fin_effects.update(
            self._fin_effects[self._fin_effects.select_dtypes(include=["number"]).columns]
            * self._bool_insights[self._fin_effects.select_dtypes(include=["number"]).columns].fillna(False)
        )
        # jira 181 cycle metric fin effect is duplicated
        self._fin_effects[COLUMNS.loop_arbitrary] -= np_sum(
            [
                self._fin_effects[COLUMNS.loop_self],
                self._fin_effects[COLUMNS.loop_roundtrip],
                self._fin_effects[COLUMNS.loop_start],
            ],
            axis=0,
        )
        self._fin_effects[COLUMNS.loop_arbitrary] = self._fin_effects[COLUMNS.loop_arbitrary].apply(
            lambda x: max(0.0, x)
        )

        financial_effect = DataFrame(
            self._fin_effects.sum(axis=1, numeric_only=True),
            index=self._fin_effects.index,
            columns=MultiIndex.from_tuples(
                [("", "Суммарный финансовый эффект")], names=self._fin_effects.columns.names
            ),
        )
        self._fin_effects = concat(
            [self._fin_effects, financial_effect],
            axis=1,
        )

    def bool_insights(self) -> DataFrame:
        """
        True/False per stage.
        """
        self.__guarantee_apply_method_called(condition_for_failure=self._bool_insights.empty)
        return self._bool_insights.fillna(False)

    def float_insights(self) -> DataFrame:
        """
        [0, 1] per stage.
        """
        self.__guarantee_apply_method_called(condition_for_failure=self._float_insights.empty)
        return self._float_insights.fillna(0.0)

    def fin_effects(self) -> DataFrame:
        """
        [0, +inf)$ per stage.
        """
        self.__guarantee_apply_method_called(condition_for_failure=self._fin_effects.empty)
        return self._fin_effects.fillna(0.0)

    @property
    def intersected_loops_wasted_time(self) -> DataFrame:
        """
        Количество времени, потраченное на зацикленности, если не учитывать, что зацикленности могут
        пересекаться. То есть это те же метрики зацикленности, но с пересечениями.

        Returns
        -------
        pd.DataFrame
            5 колонок зацикленности.
        """
        return self._intersected_loops_metrics.fillna(0)

    @property
    def metrics_mask(self) -> DataFrame:
        """
        Разметка лога данных по разным видам неэффективности.

        Returns
        -------
        pd.DataFrame
            Размера data_holder data.
        """
        self.__guarantee_apply_method_called(condition_for_failure=self._fin_effects.empty)
        metrics_mask = DataFrame(data=False, index=self.holder.data.index, dtype=bool, columns=COLUMNS.as_header())
        for metric in self._metrics.values():
            metrics_mask[metric.column] = metric.mask
        return metrics_mask

    def autoinsights_for_transitions(self) -> AutoInsights:
        """
        Autoinsights for transactions log stage1_stage2.
        """
        self.__guarantee_apply_method_called(condition_for_failure=self._fin_effects.empty)
        if self.holder.col_start_time is not None and self.holder.col_end_time is not None:
            act1 = self.holder.stage
            act2 = self.holder.stage.shift(-1)
            id1 = self.holder.case
            id2 = self.holder.case.shift(-1)
            tr_data = self.holder.data
            group_column = "transition"
            tr_data[group_column] = list(zip(act1, act2))
            # tr_data[group_column] = [str(i) + "➡️" + str(j) for i, j in zip(act1, act2)]

            tr_holder = self.holder.copy(
                data=tr_data[id1 == id2],
                col_stage=group_column,
            )

            return AutoInsights(tr_holder)

    def fin_effects_summary(self) -> str:
        """
        Description ex get_description()
        """
        self.__guarantee_apply_method_called(condition_for_failure=self._fin_effects.empty)
        metric2text = {
            COLUMNS.operation_increasing_duration: [
                "Длительность следующих этапов увеличивается со временем, "
                "что может привести в дальнейшем к проблемам в процессе: ",
                "",
            ],
            COLUMNS.operation_stable_bottleneck: [
                "В следующих этапах обнаружен Bottle neck, стабильно тормозящий процесс: ",
                ". Максимальный потенциальный финансовый эффект от его устранения ",
            ],
            COLUMNS.operation_variable_bottleneck: [
                "Следующие этапы являются нестандартизированными или ручными, "
                "и тормозят процесс из-за высокой вариативности времени этапа в разных экземплярах: ",
                ". Максимальный потенциальный финансовый эффект от его устранения ",
            ],
            COLUMNS.operation_one_incidents: [
                "В следующих этапах наблюдаются разовые инциденты, приводящие к замедлению процесса: ",
                ". Максимальный потенциальный финансовый эффект от их устранения ",
            ],
            COLUMNS.operation_multi_incidents: [
                "В следующих этапах обнаружен Bottle neck, возникающий из-за многократных инцидентов: ",
                ". Максимальный потенциальный финансовый эффект от его устранения ",
            ],
            COLUMNS.process_mistake: [
                "На данных этапах процесса возникают ошибки системы, приводящие к замедлению процесса: ",
                ". Максимальный потенциальный финансовый эффект от их устранения ",
            ],
            COLUMNS.process_return: [
                "На данных этапах процесса возникают сторнирования, приводящее к замедлению процесса: ",
                ". Максимальный потенциальный финансовый эффект от его устранения ",
            ],
            COLUMNS.failure_mistake: [
                "На данных этапах процесса возникают критические ошибки системы, приводящие к неуспеху процесса: ",
                ". Максимальный потенциальный финансовый эффект от их устранения ",
            ],
            COLUMNS.failure_structure: [
                "На данных этапах процесса возникают структурные ошибки, приводящие к неуспеху процесса: ",
                ". Максимальный потенциальный финансовый эффект от их устранения ",
            ],
            COLUMNS.failure_return: [
                "На данных этапах процесса возникают cторнирование, приводящее к неуспеху процесса: ",
                ". Максимальный потенциальный финансовый эффект от его устранения ",
            ],
            COLUMNS.process_irregular_frequency: [
                "Следующие этапы являются нерегулярными (редкими) "
                "и не требуются для успешной реализации процесса: ",
                ". Максимальный потенциальный финансовый эффект при отказе от данных этапов ",
            ],
            COLUMNS.loop_arbitrary: [
                "На следующих этапах наблюдается зацикленность процесса: ",
                ". Максимальный потенциальный финансовый эффект от устранения зацикленности ",
            ],
            COLUMNS.loop_self: [
                "На следующих этапах наблюдается зацикленность этапа самого в себя: ",
                ". Максимальный потенциальный финансовый эффект ",
            ],
            COLUMNS.loop_roundtrip: [
                "На следующих этапах наблюдается зацикленность типа «Возврат»: ",
                ". Максимальный потенциальный финансовый эффект ",
            ],
            COLUMNS.loop_ping_pong: [
                "На следующих этапах наблюдается зацикленность типа «Пинг-Понг»: ",
                ". Максимальный потенциальный финансовый эффект ",
            ],
            COLUMNS.loop_start: [
                "На следующих этапах наблюдается зацикленность, "
                "при которой экземпляр процесса начинается и заканчивается на один и тот же этап: ",
                ". Максимальный потенциальный финансовый эффект ",
            ],
        }
        text = """"""
        for metric in COLUMNS:
            series = self._bool_insights[metric]
            stages = list(series[series].index) if series.dtype == bool else []
            financial_effect = (
                str(self._fin_effects[metric].sum().round(2)).replace(".", ",") + " рублей"
                if is_float_dtype(self._fin_effects[metric])
                else ""
            )

            if stages:
                stages_text = ", ".join(["«{}»".format(stage) for stage in stages])
                text += f"""
                    {metric2text[metric][0]}{stages_text}{metric2text[metric][1]}{financial_effect}.\n
                """

        text += (
            "Суммарный финансовый эффект от устранения обнаруженных кейсов неэффективности: "
            f"{str(self._fin_effects.sum(numeric_only=True).sum().round(2)).replace('.', ',')} рублей."
        )

        return text

    def __guarantee_min_cost(
        self,
        unique_act: list[Stage],
        min_cost: dict[str, int | float] | float | int | None,
    ) -> dict[Stage, int | float]:
        """
        Converts Minute cost to the format {stage1: cost_stage1, cost_stage2: cost_stage2, ...} for
        all stages.

        Parameters
        ----------
        unique_act : List[str]
            List of uniques activities
        min_cost : Union[Dict[str, Union[int, float]], float, int, None]
            Information about the cost of a Minute.
            Allowed formats:
            {stage1: cost_stage1, cost_stage2: cost_stage2, ...}
            {stage1: cost_stage1}
            181.1841
            181
            None

        Returns
        -------
        pd.Series[str, Union[int, float]]
            Minute cost in the format {stage1: cost_stage1, cost_stage2:
        cost_stage2, ...} for all stages.

        Raises
        ------
        ValueError
            Values of min_cost dictionary must be numeric
        ValueError
            Keys of min_cost dictionary must be in DataHolder activities
        ValueError
            min_cost must be dict, float, int or None
        """
        if isinstance(min_cost, dict):
            # keys should be in unique_activities, values should be numeric
            for act, cost in min_cost.items():
                if not isinstance(cost, (int, float)):
                    raise ValueError("Values of min_cost dictionary must be numeric.")
                if act not in unique_act:
                    raise ValueError("Keys of min_cost dictionary must be in DataHolder activities.")

            if sorted(min_cost.keys()) == sorted(unique_act):
                return min_cost
            else:
                # update the missing min_cost keys in the unique_act with mean cost
                logger.warning(
                    "Вы указали цену секунды не для всех этапов процесса. "
                    "Для этих этапов считается средняя цена секунды."
                )
                mean_cost = mean(list(min_cost.values()))
                missing_acts = list(set(unique_act) - set(min_cost.keys()))
                min_cost.update({act: mean_cost for act in missing_acts})
                return Series(min_cost)
        elif isinstance(min_cost, (int, float)):
            return {act: min_cost for act in unique_act}
        elif min_cost is None:
            return {act: 1 for act in unique_act}
        else:
            raise ValueError(f"min_cost must be dict, float, int or None, not {type(min_cost)}")

    def __guarantee_success_activity(
        self,
        success_activity: Stage,
        holder: DataHolder,
    ) -> Stage:
        """
        If success_activity is None, then identify the successful stage as the most frequent last
        stage in the col_case instances.

        Parameters
        ----------
        success_activity : Union[str, int, float]
            User input for success_activity
        dh : DataHolder
            pm4mkb DataHolder

        Returns
        -------
        str
            Successful col_stage

        Raises
        ------
        ValueError
            success_activity must be str, int or float
        """
        if success_activity is None:
            id_col = holder.col_case
            act_col = holder.col_stage
            return (holder.data.groupby(id_col)[act_col].last().mode())[0]
        elif isinstance(success_activity, (str, int, float)):
            return success_activity
        else:
            raise ValueError(f"success_activity must be str, int or float, not {type(success_activity)}")

    def __guarantee_start_activity(
        self,
        start_activity: Stage,
        holder: DataHolder,
    ) -> Stage:
        """
        If start_activity is None, then identify the start stage as the most frequent first stage in
        the col_case instances.

        Parameters
        ----------
        start_activity : Union[str, int, float]
            User input for start_activity
        dh : DataHolder
            pm4mkb DataHolder

        Returns
        -------
        str
            Successful col_stage

        Raises
        ------
        ValueError
            start_activity must be str, int or float
        """
        if start_activity is None:
            id_col = holder.col_case
            act_col = holder.col_stage
            return (holder.data.groupby(id_col)[act_col].first().mode())[0]
        elif isinstance(start_activity, (str, int, float)):
            return start_activity
        else:
            raise ValueError(f"start_activity must be str, int or float, not {type(start_activity)}")

    def __guarantee_apply_method_called(self, condition_for_failure: bool) -> None:
        if condition_for_failure:
            self.apply()
