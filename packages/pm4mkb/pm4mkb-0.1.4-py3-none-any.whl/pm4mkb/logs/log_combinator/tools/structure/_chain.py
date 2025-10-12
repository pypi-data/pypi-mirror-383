from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, NamedTuple

from datetime import time
from pandas import to_timedelta
from pandas import Timedelta

from pm4mkb.logs.log_combinator.tools._utils import is_holy

if TYPE_CHECKING:
    from typing import List, Union, Set, Any, NoReturn
    from pandas._libs.tslibs.timestamps import Timestamp

    from pm4mkb.logs.log_combinator.tools.structure._stage import Stage


class CHAIN_ERRORS(Tuple):
    """Ошибки для класса chain"""

    CASE_TYPE: str = "Id (case) должен быть строкой или числом"
    START_TIME: str = "Start time первого этапа в процессе не может быть неопределено"
    AVAILABLE_FIELDS: str = (
        "Нельзя задавать не одинаковые поля для Stages, при условии что оно является единственным"
    )


class Chain(NamedTuple):
    """Цепочка из Stage элементов, порядок важен, так как это и является процессом.
    После вызова инициализации (класс не подразумевает вызов метода _init, полагается, что
    будет использован класс Log и вызвана функция get_df)

    Parameters
    ----------
    case : Union[int, str]
        case_id
    stages : List[Stage]
        лист из элементов класса Stage
    non_skiped_stages : Set[str]
        список из непропускаемых этапов, на них не будут работать различные условия пропуска
        времени
    work_day_start : time
        время начала рабочего дня, by default time(9)
    work_day_end : time
        время конца рабочего дня, by default time(18)

    off_days : Set[int]
        выходные дни для конкретной цепочки, by default set()
    """

    case: Union[int, str]
    stages: List[Stage]

    non_skiped_stages: Set[str]

    work_day_start: time = time(9)
    work_day_end: time = time(18)

    off_days: Set[int] = set()

    def _chek(
        self,
    ) -> NoReturn:
        """Некоторые проверки для каждой цепочки этапов, должен вызываться после инициализации, по
        хорошему не предназначен для пользователя"""
        assert isinstance(self.case, str) or isinstance(self.case, int), TypeError(CHAIN_ERRORS.CASE_TYPE)
        for stage in self.stages:
            stage._chek()

        for i in range(2, len(self.stages) - 1):
            if (
                sum(
                    [
                        isinstance(self.stages[i].start_time, type(self.stages[i - 1].start_time)),
                        isinstance(self.stages[i].end_time, type(self.stages[i - 1].end_time)),
                        isinstance(self.stages[i].duration, type(self.stages[i - 1].duration)),
                    ]
                )
                == 1
            ):
                print("Очень не рекомендуется указывать разные временные поля для Stages")
                break

    def _init(self, holy_cal: Set[Timestamp]) -> NoReturn:
        """Инициализация времени для этапов, если время не задано. Выставленные флаги важны"""
        self._by_start_fill()
        self._by_duration_fill(holy_cal)
        self._by_borders_fill()
        self._by_iteration_fill(holy_cal)

    def _by_start_fill(
        self,
    ) -> NoReturn:
        """Заполнение end_time полей из доступных start_time"""
        for i in range(1, len(self.stages)):
            # логика такая, если у этапа нет времени конца и нет duration значит пусть
            # у него время перехода 0 и время конца, это время начала следующего
            if self.stages[i - 1].duration is None and self.stages[i - 1].end_time is None:
                self.stages[i - 1].end_time = self.stages[i].start_time
        for i in range(len(self.stages) - 2, 0, -1):
            if self.stages[i + 1].duration is None and self.stages[i + 1].start_time is None:
                self.stages[i + 1].start_time = self.stages[i].end_time

    def _by_duration_fill(self, holy_cal) -> NoReturn:
        """Заполнение end_time полей из достпных duration"""
        skip_time: Timedelta = Timedelta(days=1)

        for i, stage in enumerate(self.stages):
            if stage.end_time is None:
                if stage.start_time is not None and stage.duration is not None:
                    datetime = stage.start_time + to_timedelta(stage.duration, unit="s")
                    if self.stages[i].stage in self.non_skiped_stages:
                        self.stages[i].end_time = datetime
                    else:
                        self.stages[i].start_time = is_holy(
                            datetime=datetime,
                            holidays=holy_cal,
                            is_up_skip=True,
                            work_periods=(self.work_day_start, self.work_day_end),
                            off_days=self.off_days,
                            skip_time=skip_time,
                        )
                        self.stages[i].end_time = (
                            self.stages[i].start_time + to_timedelta(stage.duration, unit='s')
                        )
            if stage.start_time is None:
                if stage.end_time is not None and stage.duration is not None:
                    datetime = stage.end_time - to_timedelta(stage.duration, unit="s")
                    if self.stages[i].stage in self.non_skiped_stages:
                        self.stages[i].start_time = datetime
                    else:
                        self.stages[i].start_time = is_holy(
                            datetime=datetime,
                            holidays=holy_cal,
                            is_up_skip=False,
                            work_periods=(self.work_day_start, self.work_day_end),
                            off_days=self.off_days,
                            skip_time=skip_time,
                        )

    def _by_borders_fill(
        self,
    ) -> NoReturn:
        """Заполнение duration из доступных start_time и end_time"""
        for i, stage in enumerate(self.stages):
            if stage.duration is None:
                if stage.start_time is not None and stage.end_time is not None:
                    self.stages[i].duration = (stage.end_time - stage.start_time).total_seconds()

    def _by_iteration_fill(self, holy_cal) -> NoReturn:
        """Итеративное заполнение"""
        assert self.stages[0].start_time is not None, ValueError(CHAIN_ERRORS.START_TIME)

        skip_time: Timedelta = Timedelta(days=1)

        for i in range(1, len(self.stages)):
            if self.stages[i].start_time is None:
                self.stages[i].start_time = self.stages[i - 1].end_time
            if self.stages[i].end_time is None:
                if self.stages[i].duration is not None:
                    datetime = self.stages[i].start_time + to_timedelta(self.stages[i].duration, unit="s")
                    if self.stages[i].stage in self.non_skiped_stages:
                        self.stages[i].end_time = datetime
                    else:
                        self.stages[i].start_time = is_holy(
                            datetime=datetime,
                            holidays=holy_cal,
                            is_up_skip=True,
                            work_periods=(self.work_day_start, self.work_day_end),
                            off_days=self.off_days,
                            skip_time=skip_time,
                        )
                        self.stages[i].end_time = (
                            self.stages[i].start_time + to_timedelta(self.stages[i].duration, unit='s')
                        )

        for i in range(len(self.stages) - 2, 0, -1):
            if self.stages[i].end_time is None:
                self.stages[i].end_time = self.stages[i + 1].start_time
            if self.stages[i].start_time is None:
                if self.stages[i].duration is not None:
                    datetime = self.stages[i].end_time - to_timedelta(self.stages[i].duration, unit="s")
                    if self.stages[i].stage in self.non_skiped_stages:
                        self.stages[i].start_time = datetime
                    else:
                        self.stages[i].start_time = is_holy(
                            datetime=datetime,
                            holidays=holy_cal,
                            is_up_skip=False,
                            work_periods=(self.work_day_start, self.work_day_end),
                            off_days=self.off_days,
                            skip_time=skip_time,
                        )

    def _to_list(
        self,
    ) -> List[Any]:
        """Список элементов класса"""
        return [[self.case] + stage._to_list() for stage in self.stages]
