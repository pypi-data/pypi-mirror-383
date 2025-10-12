from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, NamedTuple

from tqdm import tqdm
from pandas import DataFrame
# from pandas.tseries.holiday import USFederalHolidayCalendar

from pm4mkb.logs.log_combinator.tools.structure._chain import Chain
from pm4mkb.logs.log_combinator.tools.structure._stage import Stage

if TYPE_CHECKING:
    from typing import List, NoReturn


class LOG_ERRORS(Tuple):
    """Ошибки для класса Log"""

    COUNT: str = "Количество заданных и сгенерированных колонок не совпадает"


class Log(NamedTuple):
    """Хранит цепочки и превращает их в DataFrame, может автоматически выставлять названия
    колонкам таблицы. Основная функция для получения лога get_df, при наличии пропусков во
    временных данных (длительность, начало\конец этапа) можно использовать функцию run, которая
    автоматически заполнит пропуски (если достаточно данных).
    
    #! Функция run никогда не сгенерирует длительности переходов между этапами, если они нужны
    #! их требуется указывать явно при создании цепочек этапов

    Parameters
    ----------
    chains : List[Chain]
        набор листов из Chain
    columns : List[str]
        набор названий колонок для будущего dataframe, если оставить поле пустым, то колонки
        будут названы как поля в dataholder, by default None
    """

    chains: List[Chain]
    columns: List[str] = None

    def run(self) -> NoReturn:
        self._chek()
        self._init()

    def _chek(self) -> NoReturn:
        """Проверка каждой цепочки и этапа"""
        print("Проверка всех цепочек этапов")
        for chain in tqdm(self.chains):
            chain._chek()

    def _init(self) -> NoReturn:
        """Догенерация пустых полей времени и длительности"""
        print("Инициализация недостающего времени")
        # holy_cal = set(USFederalHolidayCalendar().holidays())
        holy_cal = set()
        for chain in tqdm(self.chains):
            chain._init(holy_cal)

    def get_df(self) -> DataFrame:
        """Получение результата"""
        return DataFrame(
            data=self._to_list(),
            columns=self._get_columns(),
        )

    def _to_list(self) -> List[List]:
        """В список списков превращает все данные"""
        return [[chain.case] + stage._to_list() for chain in self.chains for stage in chain.stages]

    def _get_columns(self) -> List[str]:
        """Берет указанные колонки в качестве названий для колонок в dataframe или
        берет названия из классов"""
        if self.columns is None:
            return (
                Chain._fields[:1]
                + tuple(Stage.__dataclass_fields__.keys())[:-1]
                + tuple(self.chains[0].stages[0].meta.keys())
            )
        else:
            assert len(self.columns) == len(self.chains[0]._to_list()), ValueError(LOG_ERRORS.COUNT)
            return self.columns
