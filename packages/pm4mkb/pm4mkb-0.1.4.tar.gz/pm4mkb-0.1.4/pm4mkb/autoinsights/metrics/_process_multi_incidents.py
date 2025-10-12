from __future__ import annotations
from typing import TYPE_CHECKING

from loguru import logger

from ..metrics import OperationBottleneck
from ._annotations import COLUMNS
from ._base import Metric


if TYPE_CHECKING:
    from pandas import Series
    from pm4mkb.baza import DataHolder, Stage


class ProcessMultiIncidents(Metric):
    """
    Parameters
    ----------
    Metric : class
        Абстрактный класс метрики с методами _bool_insights, _float_insights,
        _fin_effects и свойством column.

    float_insights
    --------------

    bool_insights
    -------------

    fin_effects
    -----------
    """

    holder: DataHolder
    successful_stage: Stage
    tight_bottleneck: OperationBottleneck = None

    _mask: Series[bool]

    def __post_init__(self, high_variance=False):
        self.tight_bottleneck = OperationBottleneck(self.holder, high_variance)
        self.tight_bottleneck.apply()

    @property
    def column(self) -> tuple[str, str]:
        return COLUMNS.operation_multi_incidents

    def _float_insights(self) -> Series:
        return self.tight_bottleneck.float_insights

    def _bool_insights(self) -> Series:
        bool_insights = self.tight_bottleneck.bool_insights & self.holder.stage_groupby[
            self.holder.col_duration
        ].apply(self.long_tail)
        self._mask = self.holder.stage.isin(bool_insights[bool_insights].index)
        return bool_insights

    def _fin_effects(self) -> Series:
        no_success_process = (
            self.holder.data[[self.holder.col_case, self.holder.col_stage]]
            .groupby(self.holder.col_case)[self.holder.col_stage]
            .apply(lambda activity: (self.successful_stage != activity).all())
        )
        return (
            self.holder.stage_groupby[self.holder.col_duration].sum()
            - self.holder.data.loc[
                self.holder.case.isin(no_success_process.index),
                [self.holder.col_stage, self.holder.col_duration],
            ]
            .groupby(self.holder.col_stage)[self.holder.col_duration]
            .sum()
        ).astype(float)

    def long_tail(self, duration):
        if duration.median() != 0:
            return duration.mean() / duration.median() > 1.15
        logger.warning(f"Недостаточно данных для расчета времени для {duration.name} = 0")
        return False
