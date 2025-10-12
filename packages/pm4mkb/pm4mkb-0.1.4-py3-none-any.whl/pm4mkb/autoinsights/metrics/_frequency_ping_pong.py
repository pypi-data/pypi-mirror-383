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


class PingPong(LoopMetric):
    """
    Метрика, показывающая есть ли какая-либо зацикленность формата «Пинг-Понг», ... А Б А Б ... .

    bool_insights
    -------------
    Если есть хотя бы одна зацикленность типа Пинг-Понг, то этап считается зацикленным.

    float_insights
    --------------
    Количество раз, когда этап встречается в зацикленности типа Пинг-Понг,
    деленное на общее количество этапов в логе.

    fin_effects
    -----------
    Считаем сумму времени по зацикленным цепочкам без учета последней пары.

    Parameters
    ----------
    Metric : class
        Абстрактный класс метрики с методами _bool_insights, _float_insights,
        _fin_effects и свойством column.
    """

    holder: DataHolder
    loop_metrics_data: DataFrame
    intersections: bool
    float_insights: Series[float64]

    _mask: Series[bool]

    @property
    def column(self) -> tuple[str, str]:
        return COLUMNS.loop_ping_pong

    @staticmethod
    def ping_pong(stages: Series) -> Series:
        """
        Determines if a ping pong looping is going among the stages.

        Parameters:
            stages (pandas.Series): The stages of the game.

        Returns:
            pandas.Series: A boolean series indicating if a ping pong game is happening.
        """
        if stages.size <= 2:
            # Return fully False mask when there are two or less stages
            return Series([False] * stages.size, index=stages.index)

        ping_pong_times = 3
        # Find where the current stage equals to the stage after 2 next
        where_stages_loop = stages == stages.shift(-ping_pong_times)

        # Shift mask for 2-loop and fill na values with `False` - the first and two last are na
        return where_stages_loop.shift(1).fillna(False)

    def _float_insights(self) -> Series:
        self.loop_metrics_data[self.metric_name] = (
            self.holder.case_groupby[self.holder.col_stage].apply(self.ping_pong).reset_index(drop=True)
        ).values
        ping_pong_stages = self.holder.data[self.holder.col_stage][self.loop_metrics_data[self.metric_name]]

        return (
            (ping_pong_stages.value_counts() / self.holder.data[self.holder.col_stage].value_counts())
            .fillna(0.0)
            .astype(float)
        )

    def _bool_insights(self) -> Series:
        return (self.float_insights > 0).astype(bool)

    def _fin_effects(self) -> Series:
        self.loop_metrics_data[self.metric_name].fillna(False, inplace=True)
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
