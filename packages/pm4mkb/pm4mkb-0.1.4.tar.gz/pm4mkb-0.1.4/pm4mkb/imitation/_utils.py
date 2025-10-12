from __future__ import annotations

from numpy import array, exp, float64, log, nan_to_num, sum as np_sum, unique
from numpy.random import normal
from numpy.typing import NDArray
from pandas import Series

from sklearn.mixture import GaussianMixture


def smooth_duration_by_activity(duration_by_activity: Series, zeroing_additive: float = 1e-05) -> NDArray[float64]:
    def non_null_smoothed_time(duration_by_activity: Series) -> NDArray[float64]:
        """"""
        return array(log(duration_by_activity[duration_by_activity != 0] + zeroing_additive).dropna())

    def all_null_smoothed_time(duration_by_activity: Series) -> NDArray[float64]:
        """"""
        return array(
            log(
                duration_by_activity + zeroing_additive,  # log(zeroing_additive) of activity_duration size
            ).dropna()
        )

    if len(duration_by_activity.value_counts(dropna=True)) > 1:
        return (
            non_null_smoothed_time(duration_by_activity)
            if np_sum(duration_by_activity) != 0
            else all_null_smoothed_time(duration_by_activity)
        )
    else:
        return unique(nan_to_num(duration_by_activity, copy=False, nan=0))


# TODO rename
def apply_gaussian_mixture(smoothed_time: NDArray[float64], zeroing_additive: float = 1e-05) -> NDArray[float64]:
    if smoothed_time.size <= 1:
        the_only_time = smoothed_time[0]

        return normal(the_only_time, the_only_time * zeroing_additive, max(smoothed_time.size, 10))

    mixture = GaussianMixture(n_components=min(8, smoothed_time.size)).fit(smoothed_time.reshape(-1, 1))
    generated_samples, _ = mixture.sample(n_samples=smoothed_time.size)

    return exp(generated_samples).flatten()
