from __future__ import annotations
from typing import TYPE_CHECKING, Tuple

from dataclasses import dataclass
from datetime import time

from pandas import to_timedelta, to_datetime
from pandas._libs.tslibs.timestamps import Timestamp
from numpy import concatenate, count_nonzero, round as np_round
from numpy.random import normal, choice
from scipy.stats import gaussian_kde

if TYPE_CHECKING:
    from typing import List
    from numpy.typing import NDArray
    from numpy import float64
    from pandas.core.indexes.datetimes import DatetimeIndex


class PEAKS_ERRORS(Tuple):
    """Ошибки для класса PeaksTimeGenerator"""

    DAY: str = "В дне не более 24 часов"
    WEEK: str = "В неделе не более 7 дней"
    MONTH: str = "В месяце не более 4 недель"
    YEAR: str = "В году не более 12 месяцев"
    EMPTY: str = "Требуется указать хоть что то"
    BAD_GEN: str = "Не удалось сгенерировать достаточное количество значений, попробуйте проверить значения"


@dataclass
class PeaksTimeGenerator:
    """Инструмент для генерации набора дат, использовать для получения дат начала экземпляров
    процесса.

    Parameters
    ----------
    day_peaks : List[float]
        указываются пики в рамках 1 дня, многократное повторение одного числа повышает
        вклад\важность пика, by default None
    week_peaks : List[float]
        указываются пики в рамках 1 недели, многократное повторение одного числа повышает
        вклад\важность пика, by default None
    month_peaks : List[float]
        указываются пики в рамках 1 месяца, многократное повторение одного числа повышает
        вклад\важность пика, by default None
    year_peaks : List[float]
        указываются пики в рамках 1 года, многократное повторение одного числа повышает
        вклад\важность пика, by default None
    left_bound : Timestamp
        левая граница, все полученое время будет >= этого параметру, by default
        Timestamp('2023-05-01')
    right_bound : Timestamp
        правая граница, все полученое время будет <= этого параметру, by default
        Timestamp('2023-06-01')
    work_day_start : time
        время начала рабочего дня, передается в формате time из datetime класса
        полученные значения в рамках 24 часов будут >= этого параметра, by default time(9)
    work_day_end : time
        время конца рабочего дня, передается в формате time из datetime класса
        полученные значения в рамках 24 часов будут <= этого параметра, by default time(18)
    _vals_counter : int
        количество значений при генерации на каждом этапе (чем больше значение, тем итоговое
        распределение будет похоже на действительное), by default 1000
    """
    day_peaks: List[float] = None
    week_peaks: List[float] = None
    month_peaks: List[float] = None
    year_peaks: List[float] = None

    left_bound: Timestamp = to_datetime("2023-05-01")
    right_bound: Timestamp = to_datetime("2023-06-01")

    work_day_start: time = time(9)
    work_day_end: time = time(18)

    _vals_counter: int = 1000

    def __post_init__(
        self,
    ) -> None:
        """Проверка на логические ошибки при инициализации класса"""
        assert (
            True if self.day_peaks is None else all([peak > 0 and peak <= 24 for peak in self.day_peaks])
        ), ValueError(PEAKS_ERRORS.DAY)
        assert (
            True if self.week_peaks is None else all([peak > 0 and peak <= 7 for peak in self.week_peaks])
        ), ValueError(PEAKS_ERRORS.WEEK)
        assert (
            True if self.month_peaks is None else all([peak > 0 and peak <= 4 for peak in self.month_peaks])
        ), ValueError(PEAKS_ERRORS.MONTH)
        assert (
            True if self.year_peaks is None else all([peak > 0 and peak <= 12 for peak in self.year_peaks])
        ), ValueError(PEAKS_ERRORS.YEAR)

    def _day_generate(self, left_bound: Timestamp, sample: int) -> NDArray[float64]:
        """Генерация пиков в рамках одного дня"""

        def hour2sec(hours: float) -> float:
            """only for flake 8"""
            return hours * 60**2

        # из timestamp в секунды
        start_value = left_bound.normalize().value / 1e09
        # генерится n распределений, потом сглаживается и resample до требуемого количества
        time_array = gaussian_kde(
            dataset=concatenate(
                [
                    normal(start_value + hour2sec(peak), hour2sec(24) ** (3 / 4), self._vals_counter)
                    for peak in self.day_peaks
                ]
            )
        ).resample(sample)[0]

        return time_array

    def _week_generate(self, left_bound: Timestamp, sample: int) -> NDArray[float64]:
        """Генерация пиков в рамках одной недели"""
        day_array = np_round(
            gaussian_kde(
                dataset=concatenate(
                    [normal(peak - 1, 7 ** (1 / 2), self._vals_counter) for peak in self.week_peaks]
                )
            ).resample(sample)[0]
        )

        time_array = concatenate(
            [
                self._day_generate(left_bound + to_timedelta("1 day") * day, count_nonzero(day_array == day))
                for day in range(0, 7)
            ]
        )

        return time_array

    def _month_generate(self, left_bound: Timestamp, sample: int) -> NDArray[float64]:
        """Генерация пиков в рамках одного месяца"""
        day_array = np_round(
            gaussian_kde(
                dataset=concatenate([normal(peak, 4 ** (1 / 2), self._vals_counter) for peak in self.month_peaks])
            ).resample(sample)[0]
        )

        time_array = concatenate(
            [
                self._week_generate(left_bound + to_timedelta("7 day") * week, count_nonzero(day_array == week))
                for week in range(0, 4)
            ]
        )
        return time_array

    def _year_generate(self, left_bound: Timestamp, sample: int) -> NDArray[float64]:
        """Генерация пиков в рамках одного года"""
        day_array = np_round(
            gaussian_kde(
                dataset=concatenate([normal(peak, 12 ** (1 / 2), self._vals_counter) for peak in self.year_peaks])
            ).resample(sample)[0]
        )

        time_array = concatenate(
            [
                self._month_generate(
                    left_bound + to_timedelta("30 day") * month, count_nonzero(day_array == month)
                )
                for month in range(0, 12)
            ]
        )

        return time_array

    def _get_time(self, sample: int) -> NDArray[float64]:
        """Генерит время"""
        if self.year_peaks is not None:
            return self._year_generate(self.left_bound, sample)
        elif self.month_peaks is not None:
            return self._month_generate(self.left_bound, sample)
        elif self.week_peaks is not None:
            return self._week_generate(self.left_bound, sample)
        elif self.day_peaks is not None:
            return self._day_generate(self.left_bound, sample)
        raise ValueError(PEAKS_ERRORS.EMPTY)

    def get_time(
        self, sample: int = 100, attempt2gen: int = 5, sorted: bool = False, skip_week_days: List[int] = None
    ) -> DatetimeIndex:
        """Преобразует время и оставляет только валидное, чем выше sample, тем более вероятно, что
        вы получите желаемое распределение, но работать будет очень долго"""
        local_sample = sample
        skip_week_days = (
            set()
            if skip_week_days is None
            else set([day - 1 for day in skip_week_days])  # потому что дни с 0 начинаются
        )

        while attempt2gen > 0:
            values = to_datetime(self._get_time(local_sample), unit="s").round("s")
            values = values[
                (
                    (~values.day_of_week.isin(skip_week_days))
                    & (values > self.left_bound)
                    & (values < self.right_bound)
                    & (values.time > self.work_day_start)
                    & (values.time < self.work_day_end)
                )
            ]

            if values.shape[0] >= sample:
                if sorted:
                    return to_datetime(choice(values, sample)).sort_values()
                else:
                    return to_datetime(choice(values, sample))

            local_sample = int(local_sample * 2)
            attempt2gen -= 1

        raise RuntimeError(PEAKS_ERRORS.BAD_GEN)
