from __future__ import annotations
from typing import TYPE_CHECKING

from numpy import sum as np_sum
from pandas import Series

from ._annotations import COLUMNS
from ._base import LoopMetric


if TYPE_CHECKING:
    from numpy import float64
    from pandas import DataFrame
    from pm4mkb.baza import DataHolder, Stage


class StartLoop(LoopMetric):
    """
    Метрика, показывающая есть ли зацикленность, при которой в экземпляре процесса встречается
    первый этап экземпляра.

    float_insights
    --------------
    Количество раз, когда этап процесса встречается в экземпляре процесса не только в начале
    экземплярах, но и в оставшейся части, деленное на количество этапа во всех экземплярах.

    bool_insights
    -------------
    Если встречается ситуация, когда экземпляр начинается на один этап, и в этом
    экземпляре присутствует еще этот этап то метрика ``True``.
    (float_insights > 0)

    fin_effects
    -----------
    Время этапов, которые встречаются до последнего этапа, который был первым в экземпляре.
    В фин эффект заносится длительность всех этих
    этапов.

    Parameters
    ----------
    Metric : class
        Абстрактный класс метрики с методами _bool_insights, _float_insights,
        _fin_effects и свойством column.q
    starting_stage : str
        Стартовый этап, при повторении которого в экземпляре считается, что
        возникла зацикленность.
    intersections : bool
        Будут ли учитываться пересечения метрик зацикленности или нет.
    """

    holder: DataHolder
    starting_stage: Stage  # FIXME unused
    loop_metrics_data: DataFrame
    intersections: bool
    float_insights: Series[float64]

    _mask: Series[bool]

    @property
    def column(self) -> tuple[str, str]:
        return COLUMNS.loop_start

    def extract_loop_mask(self, case_data: DataFrame, starting_stages: Series[Stage]):
        start_stage_mask = case_data[self.holder.col_stage] == starting_stages[case_data.name]

        # Ignore first match for starting stage itself
        if np_sum(start_stage_mask) > 1:
            # Take index of the first `True` value in start_stage_mask - last for source stages
            last_start_stage_index = start_stage_mask[::-1].idxmax()

            # Set `True` up to last found stage, omit first value - starting stage
            case_data[self.metric_name][1:last_start_stage_index] = True

        return case_data

    def _float_insights(self) -> Series:
        self.loop_metrics_data[self.metric_name] = False

        starting_stages = self.holder.case_groupby[self.holder.col_stage].first()

        self.loop_metrics_data[self.metric_name] = (
            self.loop_metrics_data.groupby(self.holder.col_case)
            .apply(
                self.extract_loop_mask,
                starting_stages,
            )[self.metric_name]
            .reset_index(drop=True)
        )

        return self.loop_metrics_data.groupby(self.holder.col_stage)[self.metric_name].apply(
            lambda mask: mask.sum() / mask.count()
        )

    def _bool_insights(self) -> Series:
        return (self.float_insights > 0).astype(bool)

    def _fin_effects(self) -> Series:
        fin_effects = Series(0, index=self.holder.unique_stages, dtype=float)

        loop_mask = self.loop_metrics_data[self.metric_name].fillna(False)
        if not self.intersections:
            self.loop_metrics_data.loc[loop_mask, self.holder.col_stage] = [
                f"{self.insight_name}_{self.metric_name}_{num}" for num in range(loop_mask.sum())
            ]
        else:
            self._mask = loop_mask

        return (
            fin_effects
            + self.loop_metrics_data[loop_mask].groupby(self.holder.col_stage)[self.holder.col_duration].sum()
        )
