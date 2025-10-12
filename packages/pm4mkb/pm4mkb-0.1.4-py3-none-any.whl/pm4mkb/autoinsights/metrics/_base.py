from __future__ import annotations
from typing import TYPE_CHECKING, Any

from dataclassy import dataclass

from pandas import Series


if TYPE_CHECKING:
    from numpy import float64, str_
    from pandas import DataFrame
    from pm4mkb.baza import DataHolder, Stage


@dataclass(slots=True)
class Metric:
    SPACE_VALUE = "---"

    holder: DataHolder
    float_insights: Series[float64] = None
    fin_effects: Series[float64] | Series[str_] = None  # `SPACE_VALUE` string for rare outputs
    bool_insights: Series[bool] | Series[str_] = None  # `SPACE_VALUE` string for rare outputs

    _mask: Series[bool] = None
    _meta_data: dict[str, Any] = {}

    def __post_init__(self):
        unique_stages = self.holder.unique_stages

        self.float_insights = Series(data=None, index=unique_stages)
        self.bool_insights = Series(data=None, index=unique_stages)
        self.fin_effects = Series(data=None, index=unique_stages)

    @property
    def column(self) -> tuple[str, str]:
        raise NotImplementedError("Реализуй свойство column у метрики")

    @property
    def mask(self) -> str:
        return self._mask.rename(self.column)

    def apply(self):
        self.float_insights = self._float_insights()
        self.bool_insights = self._bool_insights()
        self.fin_effects = self._fin_effects()

    def _float_insights(self) -> Series[float64]:
        raise NotImplementedError(f"Реализуй метод _float_insights у метрики {self.column}")

    def _bool_insights(self) -> Series[bool] | Series[str_]:
        raise NotImplementedError(f"Реализуй метод _bool_insights у метрики {self.column}")

    def _fin_effects(self) -> Series[float64] | Series[str_]:
        raise NotImplementedError(f"Реализуй метод _fin_effects у метрики {self.column}")


class LoopMetric(Metric):
    holder: DataHolder
    intersections: bool = False
    loop_length: int = 1
    starting_stage: Stage = None  # FIXME unused
    loop_metrics_data: DataFrame = None

    def __post_init__(self):
        self.loop_metrics_data = self.holder.data.loc[
            :, [self.holder.col_case, self.holder.col_stage, self.holder.col_duration]
        ]

    @property
    def column(self) -> tuple[str, str]:
        raise NotImplementedError("Реализуй свойство column у метрики")

    @property
    def insight_name(self) -> str:
        return self.column[0]

    @property
    def metric_name(self) -> str:
        return self.column[1]
