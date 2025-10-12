from __future__ import annotations
from typing import TYPE_CHECKING

from numpy import sum as np_sum
from pandas import Series

from ._annotations import COLUMNS
from ._base import LoopMetric


if TYPE_CHECKING:
    from numpy import float64
    from pandas import DataFrame
    from pm4mkb.baza import DataHolder


class ArbitraryLoop(LoopMetric):
    """
    Метрика, показывающая есть ли какая-либо зацикленность в процессе.

    bool_insights
    -------------
    Если этап процесса встречается 2 и более раз в одном экземпляре процесса, то
    этап считается зацикленным.

    float_insights
    --------------
    По каждому этапу считается количество зацикленностей по экземплярам процесса
    и делится на количество экземпляров процесса, в которых встречается этот
    этап.

    fin_effects
    -----------
    Среднее время зацикленных этапов, умноженное на их количество.

    Parameters
    ----------
    Metric : class
        Абстрактный класс метрики с методами _bool_insights, _float_insights,
        _fin_effects и свойством column.
    intersections : bool
        Будут ли учитываться пересечения метрик зацикленности или нет.
    """

    holder: DataHolder
    loop_metrics_data: DataFrame
    intersections: bool
    float_insights: Series[float64]

    _mask: Series[bool]

    @property
    def column(self) -> tuple[str, str]:
        return COLUMNS.loop_arbitrary

    def _float_insights(self) -> Series:
        latest_duplicated_stages = self.holder.data.duplicated(
            subset=[self.holder.col_case, self.holder.col_stage], keep="last"
        )
        no_duplicated_stages = self.holder.data.duplicated(
            subset=[self.holder.col_case, self.holder.col_stage], keep=False
        )

        self.loop_metrics_data[self.metric_name] = (latest_duplicated_stages == no_duplicated_stages).rename(
            self.metric_name
        )

        return self.loop_metrics_data.groupby(self.holder.col_stage)[self.metric_name].apply(
            lambda loop: loop.sum() / loop.count()
        )

    def _bool_insights(self) -> Series:
        return self.float_insights > 0

    def _fin_effects(self) -> Series:
        fin_effect = (
            self.loop_metrics_data.groupby(self.holder.col_stage)
            .apply(lambda df: np_sum(df.loc[df[self.metric_name], self.holder.col_duration]))
            .fillna(0)
            .astype(float)
        )
        loop_mask = self.loop_metrics_data[self.metric_name].fillna(False)
        if not self.intersections:
            self.loop_metrics_data.loc[loop_mask, self.holder.col_stage] = [
                f"{self.insight_name}_{self.metric_name}_{num}" for num in range(loop_mask.sum())
            ]
        else:
            self._mask = loop_mask
        return fin_effect
