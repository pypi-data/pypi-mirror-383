from __future__ import annotations
from typing import TYPE_CHECKING, Tuple

from dataclasses import dataclass
from datetime import time
from random import randint

from pm4mkb.logs.log_combinator import Meta, Stage, Chain

if TYPE_CHECKING:
    from typing import List, Dict
    from numpy import float64
    from numpy.typing import NDArray
    from pandas.core.indexes.datetimes import DatetimeIndex


class CHARGER_ERRORS(Tuple):
    """Ошибки для класса ChainsCharger"""
    START_TIME: str = 'Время начала процесса должно быть указано'


class Multipointer:
    def __init__(self, items: Dict[str, int]) -> None:
        self.multi_state = {item: 0 for item in items.keys()}
        self.multi_max = items.copy()

    def get(self, item: str) -> int:
        value = self.multi_state[item]
        self.multi_state[item] += 1
        if value >= self.multi_max[item] - 1:
            self.multi_state[item] = 0
        return value


@dataclass
class ChainsCharger:
    """Для упрощения работы с созданием набора цепочек, следует использовать этот класс. Из
    передаваемых данных создает набор цепочек, заполняет их данными и возвращает в формате,
    подходящем для использования в классе Log

    Parameters
    ----------
    stages : List[str]
        набор из названий этапов, порядок важен
    duration : Dict[str, NDArray[float64]]
        словарь из названий этапов и наборов длительностей к ним, наборы могут быть разного
        размера, но учитывайте, что при выходе за размерность, значения длительности начнут
        повторятся
    start_time : Dict[str, DatetimeIndex]
        словраь из названий этапов и наборов из времени начала к ним, для работы требуется
        указать хотя бы время начала первого этапа, остальное будет рассчитано автоматически
        (при наличии других параметров)
    non_skiped_stages : List[str]
        набор непропускаемых этапов, на них не будут работать различные условия пропуска
    end_time : Dict[str, DatetimeIndex]
        словраь из названий этапов и наборов из времени конца к ним, by default None
    meta : Dict[str, NDArray]
        словарь из названий этапов и наборов Meta классов для них, несовпадение размерностей
        Meta информации или несовпадение количества полей в классе Meta, не влияет на работу
    work_day_start : time
        начало рабочего времени, by default time(9)
    work_day_end : time
        конец рабочего времени, by default time(18)

    off_days : List[int]
        выходные дни, by default None
    """
    stages: List[str]
    duration: Dict[str, NDArray[float64]]
    start_time: Dict[str, DatetimeIndex]

    non_skiped_stages: List[str]

    end_time: Dict[str, DatetimeIndex] = None
    meta: Dict[str, NDArray] = None  # там должен класс Meta лежать

    work_day_start: time = time(9)
    work_day_end: time = time(18)

    off_days: List[int] = None

    def __post_init__(self, ) -> None:
        """Проверка на минимальные требуемые данные для работы + заполнение пропусков"""
        assert all([time is not None for time in self.start_time[self.stages[0]]]),\
            ValueError(CHARGER_ERRORS.START_TIME)
        self.end_time = {} if self.end_time is None else self.end_time
        self.meta = {} if self.meta is None else self.meta

        for stage in self.stages:
            if stage not in self.start_time:
                self.start_time[stage] = [None] * self.duration[stage].shape[0]
            if stage not in self.end_time:
                self.end_time[stage] = [None] * self.duration[stage].shape[0]
            if stage not in self.meta:
                self.meta[stage] = [Meta()] * self.duration[stage].shape[0]
        self.multipointer = Multipointer(
            {stage: self.duration[stage].shape[0] for stage in self.stages}
        )
        self._rand_case = lambda: randint(int(1e+10), int(9e+10))
        self.off_days = (
            set()
            if self.off_days is None else
            set([day - 1 for day in self.off_days])
        )

    def get_chains(self, ) -> List[Chain]:
        """Генерит цепочки этапов, с передаными данными"""
        chains = []
        for _, start_time in enumerate(self.start_time[self.stages[0]]):
            start_stage = Stage(
                stage=self.stages[0],
                start_time=start_time,
                end_time=self.end_time[self.stages[0]][self.multipointer.get(self.stages[0])],
                duration=self.duration[self.stages[0]][self.multipointer.get(self.stages[0])],
                meta=self.meta[self.stages[0]][self.multipointer.get(self.stages[0])]
            )

            chains.append(
                Chain(
                    case=self._rand_case(),
                    stages=(
                        [start_stage] +
                        [
                            Stage(
                                stage=stage,
                                start_time=(
                                    None
                                    if stage == self.stages[0] else
                                    self.start_time[stage][self.multipointer.get(stage)]
                                ),
                                end_time=self.end_time[stage][self.multipointer.get(stage)],
                                duration=self.duration[stage][self.multipointer.get(stage)],
                                meta=self.meta[stage][self.multipointer.get(stage)],
                            ) for stage in self.stages[1:]
                        ]
                    ),
                    non_skiped_stages=self.non_skiped_stages,
                    work_day_start=self.work_day_start,
                    work_day_end=self.work_day_end,
                    off_days=self.off_days,
                )
            )
        return chains
