from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING

from numpy import sum as np_sum

from ._annotations import COLUMNS
from ._base import LoopMetric


if TYPE_CHECKING:
    from numpy import float64
    from pandas import DataFrame, Series
    from pm4mkb.baza import DataHolder


class LoopLengthNames(Enum):
    # * Members are mapped to metrics annotations
    LOOP_SELF = 1
    LOOP_ROUNDTRIP = 2


class Loop(LoopMetric):
    """
    Метрика, показывающая есть ли какая-либо зацикленность конкретной длинны.

    bool_insights
    -------------
    Если этап процесса встречается в одном экземпляре процесса с периодом
    `loop_length`, то этап считается зацикленным.

    float_insights
    --------------
    По каждому этапу считается количество зацикленностей с периодом `loop_length`
    по экземплярам процесса и делится на количество экземпляров процесса, в
    которых встречается этот этап.

    fin_effects
    -----------
    Считаем сумму времени по зацикленным цепочкам.

    Parameters
    ----------
    Metric : class
        Абстрактный класс метрики с методами _bool_insights, _float_insights,
        _fin_effects и свойством column.
    loop_length : int
        Длина цикла, при которой будет прокрашиваться метрика. Например, если
        loop_length = 2, то зацикленность вида ... А Б А ... будет детектироваться.
    intersections : bool
        Будут ли учитываться пересечения метрик зацикленности или нет.
    """

    holder: DataHolder
    loop_length: int
    loop_metrics_data: DataFrame
    intersections: bool
    float_insights: Series[float64]

    _mask: Series[bool]

    @property
    def column(self) -> tuple[str, str]:
        # Get the column name of the metric with variable loop length
        loop_name = LoopLengthNames(self.loop_length).name.lower()
        return getattr(COLUMNS, loop_name)

    def _float_insights(self) -> Series:
        process_not_changed_mask = self.holder.case == self.holder.case.shift(-self.loop_length)
        loop_mask = self.holder.stage == self.holder.stage.shift(-self.loop_length)

        self.loop_metrics_data[self.metric_name] = (loop_mask & process_not_changed_mask).rename(self.metric_name)

        return self.loop_metrics_data.groupby(self.holder.col_stage)[self.metric_name].apply(
            lambda loop: loop.sum() / loop.count()
        )

    def _bool_insights(self) -> Series:
        return self.float_insights > 0

    def _fin_effects(self) -> Series:
        fin_effects = (
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

        return fin_effects
