from __future__ import annotations
from typing import TYPE_CHECKING, Any

from ._annotations import COLUMNS
from ._base import Metric


if TYPE_CHECKING:
    from pathlib import Path
    from numpy import float64
    from pandas import Series
    from pm4mkb.baza import Stage, DataHolder


class FailureStructure(Metric):
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
    float_insights: Series[float64]
    mistakes_words: list[str] = None

    _mistake_words_path: Path
    _mask: Series[bool]
    _meta_data: dict[str, Any]

    def __post_init__(self):
        with open(self._mistake_words_path, encoding="utf-8") as file:
            self.mistakes_words = file.read().splitlines()

    @property
    def column(self) -> tuple[str, str]:
        return COLUMNS.failure_structure

    def _float_insights(self) -> Series:
        activity_mistake_mask = (
            self.holder.stage.astype(str).str.lower().str.contains("|".join(self.mistakes_words)).fillna(False)
        )
        if self.holder.col_text:
            activity_mistake_mask |= (
                self.holder.text.astype(str).str.lower().str.contains("|".join(self.mistakes_words)).fillna(False)
            )
        success_process = (
            self.holder.data[[self.holder.col_case, self.holder.col_stage]]
            .groupby(self.holder.col_case)[self.holder.col_stage]
            .apply(lambda activity: (self.successful_stage == activity).any())
        )
        self._meta_data["success_process"] = success_process
        mask = ~self.holder.case.isin(success_process.index)
        mask &= ~activity_mistake_mask
        self.holder.data["mask_no_success_no_mistake"] = mask

        return self.holder.data.groupby(self.holder.col_stage)["mask_no_success_no_mistake"].apply(
            lambda mask: mask.sum() / mask.count()
        )

    def _bool_insights(self) -> Series:
        return self.float_insights > 0

    def _fin_effects(self) -> Series:
        success_process = self._meta_data["success_process"]
        self._mask = (~self.holder.case.isin(success_process.index)) & (~self.holder.data["activity_mistake_mask"])
        return (
            self.holder.data[
                (~self.holder.case.isin(success_process.index)) & (~self.holder.data["activity_mistake_mask"])
            ]
            .groupby(self.holder.col_stage)[self.holder.col_duration]
            .sum()
        ).astype(float)
