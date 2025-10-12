from __future__ import annotations
from typing import TYPE_CHECKING, Any

from loguru import logger

from pandas import Series

from sklearn.preprocessing import MinMaxScaler

from ._annotations import COLUMNS
from ._base import Metric


if TYPE_CHECKING:
    from numpy import float64
    from pm4mkb.baza import DataHolder


class OperationBottleneck(Metric):
    """
    Метрики Bottleneck с высокой вариативностью и с низкой вариативностью. Если среднее значение
    длительности по этапу больше, чем медиана, то этап считается bottleneck.

    float_insights
    --------------
    Для каждого этапа значения длительность нормализуются c помощью `MinMaxScaler`.
    Считается стандартное отклонение для этапа. Умножаем на 2, чтобы значения были от 0 до 1.
    Если считаем метрику с низкой вариативностью, то из 1 вычитаем стандартное отклонение, чтобы
    самая низкая вариативность соответствовала float_insights=1.

    bool_insights
    -------------
    Если float_insights > 0.5, тогда считаем, что bottleneck есть.

    fin_effects
    -----------
    Сумма времени этапов выше среднего.

    Parameters
    ----------
    Metric : class
        Абстрактный класс метрики с методами _bool_insights, _float_insights,
        _fin_effects и свойством column.
    high_variance: bool
        Бинарное значение, которое определяет метрику Bottleneck с высокой и низкой вариативностью.
    """

    holder: DataHolder
    high_variance: bool
    float_insights: Series[float64]
    bool_insights: Series[bool]

    _mask: Series[bool]
    _meta_data: dict[str, Any]

    def __post_init__(self):
        if not isinstance(self.high_variance, bool):
            raise ValueError(
                logger.error(f"Неправильное значение high_variance = {self.high_variance}, оно должно быть `bool`")
            )

    @property
    def column(self) -> tuple[str, str]:
        if self.high_variance is True:
            return COLUMNS.operation_variable_bottleneck
        else:
            return COLUMNS.operation_stable_bottleneck

    @staticmethod
    def _deviation(duration: Series, high_variance) -> float:
        """
        Calculate the deviation of the given duration data.

        Parameters:
            duration (pd.Series): A series of duration values.
            high_variance (bool): A flag indicating whether the duration data has high variance.

        Returns:
            float: The deviation of the duration data. If `high_variance` is True,
                it returns the standard deviation of the scaled duration.
            Otherwise, it returns the complement of the standard deviation of the scaled duration.
        """
        duration = duration.to_numpy().reshape(-1, 1)
        scaled_duration = MinMaxScaler().fit_transform(duration)
        scaled_duration *= 2

        return scaled_duration.std() if high_variance else 1 - scaled_duration.std()

    def _float_insights(self) -> Series:
        bottleneck = self.holder.stage_groupby[self.holder.col_duration].apply(
            lambda duration: duration.mean() > duration.median()
        )
        deviation = self.holder.stage_groupby[self.holder.col_duration].apply(
            lambda duration: self._deviation(duration, high_variance=self.high_variance)
        )
        return bottleneck * deviation

    def _bool_insights(self) -> Series:
        self._meta_data["prolonged"] = self._meta_data.get(
            "prolonged", Series(data=False, index=self.holder.unique_stages, dtype=bool)
        )
        bool_insights = (self.float_insights > 0.5) & self._meta_data["prolonged"]
        self._mask = self.holder.stage.isin(bool_insights[bool_insights].index)
        return bool_insights

    def _fin_effects(self) -> Series:
        fin_effect = self.holder.stage_groupby[self.holder.col_duration].apply(
            lambda duration: (duration - duration.mean())[duration - duration.mean() > 0].sum()
        )
        return fin_effect * self.bool_insights
