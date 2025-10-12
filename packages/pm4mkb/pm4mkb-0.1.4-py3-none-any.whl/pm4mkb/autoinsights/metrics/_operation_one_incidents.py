from __future__ import annotations
from typing import TYPE_CHECKING, Any

from loguru import logger

from numpy import isnan
from pandas import Series

from sklearn.cluster import k_means
from sklearn.preprocessing import MinMaxScaler

from ._annotations import COLUMNS
from ._base import Metric


if TYPE_CHECKING:
    from pm4mkb.baza import DataHolder


class OperationOneIncidents(Metric):
    """
    Метрика "Разовые инциденты" из категории "Операции". Считается, что если распределение
    центрированное и есть выбросы по времени сверху.

    float_insights
    --------------
    Преобразование среднего времени этапа с помощью ``MinMaxScaler``.

    bool_insights
    -------------
    Разделение средней длительности с помощью кластеризации ``KMeans`` на 2
    класса. Кластер с большим центроидом будет считаться выбросным. Фильтруются
    этапы, у которых распределение не центрировано.

    fin_effects
    -----------
    Сумма длительности этапов, у которых bool_insights == True

    Parameters
    ----------
    Metric : class
        Абстрактный класс метрики с методами _bool_insights, _float_insights,
        _fin_effects и свойством column.
    """

    holder: DataHolder

    _mask: Series[bool]
    _meta_data: dict[str, Any]

    @property
    def column(self) -> tuple[str, str]:
        return COLUMNS.operation_one_incidents

    def _float_insights(self) -> Series:
        scaler = MinMaxScaler()
        mean_duration = self.holder.stage_groupby[[self.holder.col_duration]].mean()
        return scaler.fit_transform(mean_duration)

    def _bool_insights(self) -> Series:
        data = (
            self.holder.data[
                ~isnan(
                    self.holder.duration
                )  # drop records for col_case transitions - no option to estimate duration with a single timestamp
            ]
            .groupby(by=self.holder.col_stage)[self.holder.col_duration]
            .mean()
        ).dropna()  # drop grouped activities which are the only in process

        try:
            centroids, labels, _ = k_means(data.to_numpy().reshape(-1, 1), n_clusters=2)
        except ValueError as err:
            raise ValueError(
                "Ошибка при расчете метрики 'Разовые инциденты': "
                "полностью отсутствуют (не удалось рассчитать) данные для продолжительностей операций"
            ) from err

        if centroids[0] > centroids[1]:
            # bool([0, 0, 1] - 1) = [True, True, False]
            insight = Series(data=map(abs, labels - 1), index=data.index)
        elif centroids[0] < centroids[1]:
            insight = Series(data=labels, index=data.index)
        else:
            insight = Series(data=len(labels) * [False], index=data.index)

        centered_distribution_mask = self.holder.stage_groupby[self.holder.col_duration].apply(
            self.__centered_distribution
        )
        bool_insights = insight & centered_distribution_mask

        self._meta_data["prolonged"] = Series(data=False, index=self.holder.unique_stages, dtype=bool)
        self._meta_data["prolonged"].update(insight.astype(bool))
        self._mask = self.holder.stage.isin(bool_insights[bool_insights].index)

        return bool_insights

    @staticmethod
    def __centered_distribution(duration):
        if duration.median() != 0:
            return (duration.mean() / duration.median() >= 0.9) and (duration.mean() / duration.median() <= 1.1)
        logger.warning(f"Недостаточно данных для расчета времени для {duration.name} = 0")
        return False

    def _fin_effects(self) -> Series:
        return (
            self.holder.data.groupby(self.holder.col_stage)[self.holder.col_duration]
            .sum()[self._bool_insights()]
            .astype(float)
        )
