from __future__ import annotations
from typing import TYPE_CHECKING

from numpy import float64, log, sum as np_sum
from pandas import DataFrame, concat, pivot_table


if TYPE_CHECKING:
    from pm4mkb.baza import DataHolder


class InfluencingActivities:
    __slots__ = ("holder",)

    def __init__(self, data_holder: DataHolder) -> None:
        self.holder = data_holder

    def _features_selection(self, data):
        return {
            "good_features": None,
            "index": None,
            "selected_features": (
                [[column for column in data.columns if column != column_itself] for column_itself in data.columns]
            ),
        }

    def _extract_data(self) -> DataFrame:
        data_f = pivot_table(
            self.holder.data,
            values=self.holder.col_start_time or self.holder.col_end_time,
            index=self.holder.col_case,
            columns=self.holder.col_stage,
            aggfunc="count",
        ).fillna(0)

        self.holder.data[self.holder.col_duration] = self.holder.duration.fillna(0)
        idt = self.holder.case[self.holder.duration < 0]

        data_r = pivot_table(
            self.holder.data[~self.holder.case.isin(idt)],
            values=self.holder.col_duration,
            index=self.holder.col_case,
            columns=self.holder.col_stage,
            aggfunc=np_sum,
        ).fillna(0)

        data_log = data_r.applymap(lambda x: log(x + 1))
        data_t = concat([data_log, data_r])

        return concat([data_t, data_f])

    def activities_impact(self, feature_counts=True):
        extracted_data = self._extract_data()
        features = list(extracted_data.columns)

        result = self._features_selection(extracted_data.astype(float64))

        if feature_counts:
            features_appearance = sum(result["selected_features"], [])
            return {feature: features_appearance.count(feature) for feature in features}

        return dict(zip(features, result["selected_features"]))
