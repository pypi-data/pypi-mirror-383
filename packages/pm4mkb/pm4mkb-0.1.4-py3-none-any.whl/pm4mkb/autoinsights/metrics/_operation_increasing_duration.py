from __future__ import annotations
from typing import TYPE_CHECKING, Any

from numpy import arctan, pi
from pandas import DataFrame, Series, Timedelta

from sklearn.linear_model import RANSACRegressor

from ._annotations import COLUMNS
from ._base import Metric


if TYPE_CHECKING:
    from pm4mkb.baza import DataHolder


class IncreasingDuration(Metric):
    """
    Метрика, показывающая растет ли длительность этапа со временем.

    bool_insights
    -------------
    Для каждого этапа строится зависимость длительности этапа от времени его
    начала по всем экземплярам с помощью RANSACRegressor. Если угловой
    коэффициент больше 0.01, то считается, что длительность растет со временем.

    float_insights
    --------------
    Угловой коэффициент преобразуется в угол наклона. Если угол = 90, то
    значение инсайта = 1. Если угол = 0, то инсайт = 0.5. Если угол = - 90, то
    значение инсайта = 0.

    fin_effects
    -----------
    Не считается для этой метрики.

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
        return COLUMNS.operation_increasing_duration

    @staticmethod
    def get_trend_coef(df: DataFrame) -> float:
        start_time = df.iloc[:, 0]
        duration = df.iloc[:, 1]

        start_time = (start_time - start_time.min()) / Timedelta(seconds=1)

        start_time.fillna(-10000, inplace=True)
        duration.fillna(-10000, inplace=True)

        feature = start_time.to_numpy().reshape(-1, 1)
        target = duration.to_numpy().reshape(-1, 1)

        if feature.shape[0] > 1 and target.shape[0] > 1:
            regressor = RANSACRegressor(random_state=0).fit(feature, target)
            return regressor.estimator_.coef_[0][0]
        else:
            return 0

    def _float_insights(self) -> Series:
        self._meta_data["coef"] = self.holder.stage_groupby[
            [self.holder.col_start_time, self.holder.col_duration]
        ].apply(self.get_trend_coef)
        return (arctan(self._meta_data["coef"]) + pi / 2) / pi

    def _bool_insights(self) -> Series:
        bool_insights = self._meta_data["coef"] > 0
        self._mask = self.holder.stage.isin(bool_insights[bool_insights].index)
        return bool_insights

    def _fin_effects(self) -> Series:
        return Series(data=self.SPACE_VALUE, index=self.holder.unique_stages)
