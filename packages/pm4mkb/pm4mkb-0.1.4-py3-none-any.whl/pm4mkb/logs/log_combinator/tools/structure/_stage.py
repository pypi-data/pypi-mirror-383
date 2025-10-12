from __future__ import annotations
from typing import TYPE_CHECKING, Tuple

from dataclasses import dataclass, field
from pandas import Timestamp

from pm4mkb.logs.log_combinator.tools.structure._meta import Meta

if TYPE_CHECKING:
    from typing import Any, List, NoReturn


class STAGE_ERRORS(Tuple):
    """Ошибки для класса stage"""

    NAME_TYPE: str = "Название этапа не может быть не строкой"
    TIME_TYPE: str = (
        "Время передано в недопустимом формате, используйте функцию to_datetime или"
        + "измените формат времени, а затем попробуйте снова"
    )
    INIT_VALUES: str = "Требуется указать хотя бы одну из трех временных переменных"
    TIME_COMPARE: str = "Время начала этапа не может быть больше времени конца"


@dataclass
class Stage:
    """Класс этапа, базовые характеристики для dh и meta. Этапы называются так же, как
    их можно вызвать из датахолдера. Для этого класса используется проверка только
    на то чтобы все 3 поля связанные с времененм не были пустыми

    Parameters
    ----------
    stage : str
        название этапа
    start_time : Timestamp
        время начала этапа, by default None
    end_time : Timestamp
        время конца этапа, by default None
    duration : int
        время в секундах, длительности этапа, by default None
    meta : Meta
        метаинформация (по сути словарь), из этого параметра берется информация для
        небазовых колонок, by default Meta
    Returns
    -------
    _type_
        _description_
    """

    stage: str
    start_time: Timestamp = None
    end_time: Timestamp = None
    duration: int = None
    meta: Meta = field(default_factory=Meta)

    def _chek(
        self,
    ) -> NoReturn:
        """Некоторые проверки для каждого этапа, должен вызываться после инициализации, по хорошему,
        не должно использоваться юзером"""
        # некоторые функции для проверки значений, вынесены для удобства + непонятно как нормально
        # сделать перенос условий в assert
        time_type = (
            True if self.start_time is None else isinstance(self.start_time, Timestamp),
            True if self.end_time is None else isinstance(self.end_time, Timestamp),
        )
        is_times = (self.start_time is None, self.end_time is None, self.duration is None)

        assert isinstance(self.stage, str), TypeError(STAGE_ERRORS.NAME_TYPE)
        assert not all(is_times), ValueError(STAGE_ERRORS.INIT_VALUES)
        assert all(time_type), TypeError(STAGE_ERRORS.TIME_TYPE)
        if self.start_time is not None and self.end_time is not None:
            assert self.start_time <= self.end_time, ValueError(STAGE_ERRORS.TIME_COMPARE)

    def _to_list(
        self,
    ) -> List[Any]:
        """Список элементов класса"""
        return list(self.__dict__.values())[:-1] + self.meta._to_list()
