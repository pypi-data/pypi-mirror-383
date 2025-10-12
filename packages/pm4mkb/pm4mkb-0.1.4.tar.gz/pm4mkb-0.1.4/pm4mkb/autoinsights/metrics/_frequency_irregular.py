from __future__ import annotations
from typing import TYPE_CHECKING, Any

from pandas import Series

from sklearn.svm import OneClassSVM

from ._annotations import COLUMNS
from ._base import Metric


if TYPE_CHECKING:
    from pm4mkb.baza import Stage, DataHolder


class Irregular(Metric):
    """
    Метрика "Нерегулярная операция" из категории "Длительность процесса".

    float_insights
    --------------
    Для каждого этапа считаем количество уникальных этапов процесса, делим на
    общее количество уникальных этапов. Вычитаем получившееся число из единицы,
    чтобы 1 соответствовало самому редкому этапу.

    bool_insights
    -------------
    Для каждого этапа считаем количество уникальных этапов процесса, делим на
    общее количество уникальных этапов. Смотрим выбросы с помощью OneClassSVM,
    с самыми маленькими значениями.

    fin_effects
    -----------
    Считаем сумму длительностей для нерегулярных этапов, которые не являются
    успешными.

    Parameters
    ----------
    Metric : class
        Абстрактный класс метрики с методами bool_insights, float_insights, fin_effects
    """

    holder: DataHolder
    successful_stage: Stage
    bool_insights: Series[bool]

    _mask: Series[bool]
    _meta_data: dict[str, Any]

    @property
    def column(self) -> str:
        return COLUMNS.process_irregular_frequency

    def _float_insights(self) -> Series:
        id_count = self.holder.case.nunique()
        process_frequency = self.holder.data.groupby(self.holder.col_stage)[self.holder.col_case].apply(
            lambda id: id.nunique() / id_count
        )
        process_frequency = process_frequency.reindex(self.holder.unique_stages)
        self._meta_data["process_frequency"] = process_frequency
        return 1 - process_frequency

    def _bool_insights(self) -> Series:
        process_frequency = self._meta_data["process_frequency"]
        process_frequency = process_frequency.to_numpy().reshape(-1, 1)
        svm = OneClassSVM().fit(process_frequency)
        labels = svm.predict(process_frequency)

        outliers = process_frequency[labels == 1]
        lower_outlier_bound = outliers.min() if outliers.size > 0 else 0.0
        return Series((process_frequency < lower_outlier_bound)[:, 0], index=self.holder.unique_stages)

    def _fin_effects(self) -> Series:
        self._mask = (self.holder.stage != self.successful_stage) & (
            self.holder.stage.isin(self.bool_insights[self.bool_insights].index)
        )
        return (
            self.holder.data[self._mask]
            .groupby(self.holder.col_stage)[self.holder.col_duration]
            .sum()
            .astype(float)
        )
