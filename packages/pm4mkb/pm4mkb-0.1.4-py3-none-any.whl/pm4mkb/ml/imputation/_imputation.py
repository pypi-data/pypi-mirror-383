from dataclassy import dataclass
from pandas import DataFrame
from typing import Optional, List
from pm4mkb.ml.imputation._models import (
    IterativeMissingValuesImputer,
    CorrelatedImputer,
    SimpleMissingValuesImputer,
    KNNMissingValuesImputer,
)

NUMERIC_IMPUTERS = [
    IterativeMissingValuesImputer,
    SimpleMissingValuesImputer,
    KNNMissingValuesImputer,
]
CAT_IMPUTERS = [
    IterativeMissingValuesImputer,
    KNNMissingValuesImputer,
]


@dataclass
class Imputer:
    data: DataFrame
    correlation_threshold: float = 0.8
    columns_to_fill: Optional[List[str]] = None
    categorical_col: Optional[List[str]] = []
    numeric_col: Optional[List[str]] = []

    def __post_init__(self):
        self.df_filled = self.data.dropna(axis=1, how="all")
        if self.columns_to_fill is None:
            self.columns_to_fill = self.df_filled.columns[
                self.df_filled.isna().any()
            ].tolist()

    def apply(self) -> DataFrame:
        # CorrelatedImputer first
        ci = CorrelatedImputer(
            self.df_filled,
            threshold=self.correlation_threshold,
            categorical_col=self.categorical_col,
            numeric_col=self.numeric_col,
            columns_to_fill=self.columns_to_fill,
        )
        self.df_filled = ci.fit_transform()

        # then IterativeImputer for numeric and KNNImputer for categorical

        ii = IterativeMissingValuesImputer(
            self.df_filled[self.numeric_col],
            categorical_col=self.categorical_col,
            numeric_col=self.numeric_col,
            columns_to_fill=self.columns_to_fill,
        )
        self.df_filled[self.numeric_col] = ii.fit_transform()

        ii = KNNMissingValuesImputer(
            self.df_filled,
            categorical_col=self.categorical_col,
            numeric_col=self.numeric_col,
            columns_to_fill=self.columns_to_fill,
        )
        self.df_filled[self.categorical_col] = ii.fit_transform(numeric=False)

        return self.df_filled
