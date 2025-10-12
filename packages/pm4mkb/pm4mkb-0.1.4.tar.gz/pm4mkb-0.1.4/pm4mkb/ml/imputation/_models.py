from __future__ import annotations

from sklearn.experimental import (
    enable_iterative_imputer,
)  # I'ts need from IterativeImputer import
from sklearn.impute import KNNImputer, SimpleImputer, IterativeImputer
from sklearn.preprocessing import OrdinalEncoder
from warnings import filterwarnings
from typing import List
from dataclassy import dataclass
from pandas import DataFrame, Series, qcut, crosstab
from typing import Optional, List
from numpy import sqrt, ones, diag, ndarray, nan
from scipy.stats import chi2_contingency
from itertools import combinations


filterwarnings("ignore")
#! All imputers are not inplace


def _categorize_data_with_nulls(data: DataFrame, categorical_columns: list[str]) -> None:
    data[categorical_columns] = data[categorical_columns].astype(object).astype("category")


@dataclass
class BaseImputer:
    data: DataFrame
    threshold: float = 0.8
    columns_to_fill: Optional[List[str]] = None
    categorical_col: Optional[List[str]] = []
    numeric_col: Optional[List[str]] = []
    _results = None
    _num_imputer = None
    _cat_imputer = None

    @property
    def get_results(self) -> DataFrame:
        """
        Returns the results of the fit_transform method.

        Parameters:
        - None

        Returns:
        - The results of the fit_transform method.
        """
        if self._results is None:
            self._results = self.fit_transform()
        return self._results

    def fit_transform(self, numeric: bool = True) -> DataFrame:
        """
        Fit and transform the DataFrame by filling missing values.

        Parameters:
            numeric (bool): Flag indicating whether to use the numeric imputer or the categorical imputer. Default is True.

        Returns:
            DataFrame: The filled DataFrame.
        """

        df_filled = self.data.copy()
        if numeric:
            imputer = self._num_imputer
            df_filled = imputer.fit_transform(df_filled[self.numeric_col])
            df_filled = DataFrame(df_filled, columns=self.numeric_col, index=self.data.index)

        else:
            # Categorize the data with pandas missing values
            # Otherwise, scikit-learn encoder will throw a TypeError about non-uniform strings
            _categorize_data_with_nulls(df_filled, self.categorical_col)

            # we first should encode the data
            encoder = OrdinalEncoder()
            df_filled = encoder.fit_transform(df_filled[self.categorical_col])
            df_filled = DataFrame(df_filled, columns=self.categorical_col, index=self.data.index)
            df_filled[self.numeric_col] = self.data[self.numeric_col]
            columns = df_filled.columns

            # imputation
            imputer = self._cat_imputer
            df_filled = imputer.fit_transform(df_filled)
            df_filled = DataFrame(df_filled, columns=columns, index=self.data.index)

            # we inverse the encoding
            df_filled = encoder.inverse_transform(df_filled[self.categorical_col])
            df_filled = DataFrame(df_filled, columns=self.categorical_col, index=self.data.index)

        return df_filled


class CorrelatedImputer(BaseImputer):
    """
    This class fills the missing values in the DataFrame by finding correlated columns
    and replaces them with the corresponding values.

    Parameters:
        data (DataFrame): The dataframe to be used.
        threshold (float, optional): The threshold value. Defaults to 0.8.
        columns_to_fill (list[str], optional): The list of columns to fill. Defaults to all columns.

    """

    def __post_init__(self):
        if self.columns_to_fill is None:
            self.columns_to_fill = self.data.columns
        self._results = None
        self._correlated_features = {}

    @property
    def correlated_features(self) -> dict:
        if self._correlated_features:
            return self._correlated_features
        print("No correlated features found")

    def fit_transform(self, numeric=True) -> DataFrame:
        """
        Performs a fit-transform operation on the data.

        This method fills the missing values in the DataFrame by finding correlated columns
        and replaces them with the corresponding values.
        The filled DataFrame is then assigned to the `_results` attribute.

        Returns:
            df_filled (DataFrame): The DataFrame with filled missing values.
            self._correlated_features (dict): A dictionary containing the correlated features.
        """

        df_filled, self._correlated_features = self.find_corr_columns()
        self._results = self.data.copy()
        self._results[df_filled.columns] = df_filled
        return self._results

    def cramers_v(self, confusion_matrix: ndarray, fill_value=0) -> float:
        """
        Calculate Cramers V statistic for categorial-categorial association.
        uses correction from Bergsma and Wicher according to
        Journal of the Korean Statistical Society 42 (2013): 323-328

        Parameters:
            confusion_matrix (numpy.ndarray): A 2-dimensional array representing the confusion matrix.
            fill_value (float): The value to return in case of a FloatingPointError.

        Returns:
            float: The calculated Cramer's V coefficient.

        """

        chi2 = chi2_contingency(confusion_matrix)[0]
        n = confusion_matrix.sum().sum()
        phi2 = chi2 / n
        r, k = confusion_matrix.shape
        phi2corr = max(0, phi2 - ((k - 1) * (r - 1)) / (n - 1))
        rcorr = r - ((r - 1) ** 2) / (n - 1)
        kcorr = k - ((k - 1) ** 2) / (n - 1)
        try:
            return sqrt(phi2corr / min((kcorr - 1), (rcorr - 1)))
        except FloatingPointError:
            return fill_value

    def correlation_ratio(self, data, categorical, numeric) -> DataFrame:
        """
        Calculates the correlation ratio between categorical and numeric variables in a dataframe.

        Parameters:
        - data (DataFrame): The input dataframe.
        - categorical (list): List of column names representing categorical variables.
        - numeric (list): List of column names representing numeric variables.

        Returns:
        - corr_matrix (DataFrame): The correlation matrix, where the rows and columns represent the variables in the dataframe.
        """
        corr_matrix = DataFrame(diag(ones(data.shape[1])), columns=data.columns, index=data.columns)
        num_bins = data[categorical].nunique().max()
        new_numeric = DataFrame()
        for column in numeric:
            new_numeric[column] = qcut(
                data[column],
                q=num_bins,
                labels=False,
                duplicates="drop",
            )
        new_numeric.index = data.index
        cat_df = data[categorical].join(new_numeric, how="left")
        for col1, col2 in list(combinations(cat_df.columns, 2)):
            corr_matrix.loc[col1, col2] = self.cramers_v(crosstab(cat_df[col1], cat_df[col2]).values)
            corr_matrix.loc[col2, col1] = corr_matrix.loc[col1, col2]
        num_corr = data[numeric].corr()
        corr_matrix.loc[num_corr.index, num_corr.columns] = num_corr
        return corr_matrix

    def find_corr_columns(self) -> DataFrame:
        """
        Finds columns in the dataframe that have a correlation coefficient above the given threshold.
        Then fills one column with the most frequent value in the other column.

        Parameters:
        threshold (float): The threshold value for the correlation coefficient. Defaults to 0.8.

        Returns:
        df_filled (DataFrame): partially filled dataframe.
        """
        correlated_features_dict = {}
        df_filled = DataFrame()
        for col in self.columns_to_fill:
            df_corr = self.correlation_ratio(self.data, self.categorical_col, self.numeric_col).abs()
            correlated_features = list(df_corr.loc[df_corr[col] > self.threshold, col].drop(col).index)
            if len(correlated_features):
                df_filled[col] = self.data[col]
                for feature in correlated_features:
                    df_filled[col], _ = self.fill_from_other_column(df_filled[col], self.data[feature])
                correlated_features_dict[col] = correlated_features

        return df_filled, correlated_features_dict

    def fill_from_other_column(
        self,
        target: Series,
        source: Series,
    ) -> Series:
        """
        Fill the target column empty values with values from the source column * mean of their .

        Args:
            target (Series): Target column.
            source (Series): Source column.

        Returns:
            Series: The modified column after filling it with values from the source column.
        """

        # counting unique pairs occurrences
        matching = DataFrame([target, source, ones(len(target))]).T
        matching = matching.groupby([target.name, source.name]).count().max(axis=1).reset_index()

        # dict of most frequent pairs for target and source cols
        matching = matching.loc[matching.groupby(source.name)[0].idxmax(), :][[target.name, source.name]]
        matching = matching.set_index(source.name).to_dict()[target.name]

        return target.fillna(source.map(matching)), matching


class SimpleMissingValuesImputer(BaseImputer):
    def __post_init__(self, num_strategy="mean", cat_fill_value=None):
        """
        Параметры:
        - num_strategy (str): Стратегия обработки пропусков для числовых признаков.
                          Значения: 'mean', 'median', 'most_frequent'.
                          По умолчанию 'mean'.
        - fill_value (str): Константное значение, которым заполняются пропуски в категориальных признаках.
                      По умолчанию заполнение самым частым значением.
        """
        self.num_strategy = num_strategy
        self.cat_fill_value = cat_fill_value
        self._num_imputer = SimpleImputer(strategy=self.num_strategy)
        self._cat_imputer = SimpleImputer(strategy="most_frequent", fill_value=self.cat_fill_value)


# Только для числовых
class IterativeMissingValuesImputer(BaseImputer):
    def __post_init__(self, max_iter=10):
        self.max_iter = max_iter
        self._num_imputer = IterativeImputer(max_iter=self.max_iter, missing_values=nan, skip_complete=True)


class KNNMissingValuesImputer(BaseImputer):
    def __post_init__(self, n_neighbors=5, weights="uniform"):
        """
        Параметры:
        - n_neighbors (int): Количество ближайших соседей KNN. По умолчанию: 5
        - weights (str): {'uniform', 'distance'}
          'uniform' - одинаковые веса у соседей, 'distance' - веса зависят от расстояния.
        """
        self.n_neighbors = n_neighbors
        self.weights = weights
        self._num_imputer = KNNImputer(n_neighbors=self.n_neighbors, weights=self.weights)
        self._cat_imputer = KNNImputer(n_neighbors=self.n_neighbors, weights=self.weights)
