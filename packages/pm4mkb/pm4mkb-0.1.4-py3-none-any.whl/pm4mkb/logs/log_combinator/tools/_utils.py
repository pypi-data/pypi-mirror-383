from __future__ import annotations
from typing import TYPE_CHECKING

from datetime import time
from seaborn import displot
from pandas import Timedelta

if TYPE_CHECKING:
    from typing import Set, Tuple, List, Dict
    from numpy import float64
    from numpy.typing import NDArray
    from pandas._libs.tslibs.timestamps import Timestamp
    from seaborn.axisgrid import FacetGrid


def total_seconds(dtime: time) -> float:
    """Количество секунд для типа datetime.time"""
    return dtime.hour * 60 * 60 + dtime.minute * 60 + dtime.second


def up_skip(
    datetime: Timestamp,
    lower_bound: time,
    higher_bound: time,
    holidays: Set[Timestamp],
    day_border: Timedelta,
    off_days: Set[int],
    skip_time: Timedelta,
) -> Timestamp:
    """К полученному времени прибавляет нужное количество для пропуска выходных\праздников

    Parameters
    ----------
    datetime : Timestamp
        время в формате Timestamp
    lower_bound : time
        нижняя граница, подразумевается время начала рабочего дня
    higher_bound : time
        верхняя граница, подразумевается время конца рабочего дня
    holidays : Set[Timestamp]
        набор из дат, которые будут пропущены, указываются в любом формате подходящим под
        логику наличия только года, месяца и дня в дате
    day_border : Timedelta
        по сути нижняя граница рабочего времени, но при желании можно указать любое значение,
        с условием попадания в границы рабочего времени (которые lower и higher bound)
    off_days : Set[int]
        дни недели (начиная с 0), которые будут пропущены, подразумевалось как указатель выходных
    skip_time : Timedelta
        время, которое прибавляется к текущему, чтобы пропустить требуемый временной интервал,
        обычно это 24 часа

    Returns
    -------
    Timestamp
        дата в неизмененной форме, если условия пропуска не были выполнены, или дата больше
        изначальной, с учетом попадания в непропускаемый промежуток
    """
    local_time = datetime.time()
    if lower_bound > local_time:
        datetime += Timedelta(seconds=total_seconds(lower_bound) - total_seconds(local_time))

    if higher_bound < local_time:
        datetime = datetime.normalize() + skip_time + day_border

    normalized_time = datetime.normalize()
    # TODO что то, чтобы задавать руками графи
    if normalized_time in holidays or normalized_time.day_of_week in off_days:
        while normalized_time in holidays or normalized_time.day_of_week in off_days:
            normalized_time += skip_time
        return normalized_time + day_border
    return datetime


def down_skip(
    datetime: Timestamp,
    lower_bound: time,
    higher_bound: time,
    holidays: Set[Timestamp],
    day_border: Timedelta,
    off_days: Set[str],
    skip_time: Timedelta,
) -> Timestamp:
    """Из полученного времени вычитает нужное количество для пропуска выходных\праздников

    Parameters
    ----------
    datetime : Timestamp
        время в формате Timestamp
    lower_bound : time
        нижняя граница, подразумевается время начала рабочего дня
    higher_bound : time
        верхняя граница, подразумевается время конца рабочего дня
    holidays : Set[Timestamp]
        набор из дат, которые будут пропущены, указываются в любом формате подходящим под
        логику наличия только года, месяца и дня в дате
    day_border : Timedelta
        по сути верхняя граница рабочего времени, но при желании можно указать любое значение,
        с условием попадания в границы рабочего времени (которые lower и higher bound)
    off_days : Set[int]
        дни недели (начиная с 0), которые будут пропущены, подразумевалось как указатель выходных
    skip_time : Timedelta
        время, которое прибавляется к текущему, чтобы пропустить требуемый временной интервал,
        обычно это 24 часа

    Returns
    -------
    Timestamp
        дата в неизмененной форме, если условия пропуска не были выполнены, или дата больше
        изначальной, с учетом попадания в непропускаемый промежуток"""
    local_time = datetime.time()
    if lower_bound > local_time:
        datetime = datetime.normalize() - skip_time + day_border

    if higher_bound < local_time:
        datetime -= Timedelta(seconds=total_seconds(local_time) - total_seconds(higher_bound))

    normalized_time = datetime.normalize()
    if normalized_time in holidays or normalized_time.day_of_week in off_days:
        while normalized_time in holidays or normalized_time.day_of_week in off_days:
            normalized_time -= skip_time
        return normalized_time + day_border
    return datetime


def is_holy(
    datetime: Timestamp,
    holidays: Set[Timestamp],
    is_up_skip: bool,
    work_periods: Tuple[time, time],
    off_days: Set[int],
    skip_time: Timedelta,
) -> Tuple[bool, Timestamp]:
    """Комбинация из двух функций down_skip и up_skip, имеет те же параметры, за исключением флага
    is_up_skip, который указывает в какую сторону будет пропуск"""
    get_skip = up_skip if is_up_skip else down_skip
    lower_bound, higher_bound = work_periods
    if (
        datetime.normalize() in holidays
        or datetime.time() < lower_bound
        or datetime.time() > higher_bound
        or datetime.day_of_week in off_days
    ):
        return get_skip(
            datetime=datetime,
            lower_bound=lower_bound,
            higher_bound=higher_bound,
            holidays=holidays,
            day_border=Timedelta(seconds=total_seconds(work_periods[0] if is_up_skip else work_periods[1])),
            off_days=off_days,
            skip_time=skip_time,
        )
    return datetime


def plot_dist(
    values: NDArray[float64],
    bins: int = 15,
    density: bool = False,
    size: Tuple[float, float] = (7, 2),
) -> FacetGrid:
    """Рисует распределение переданных значений
    #TODO одна из тех функций, которую стоит вынести и переиспользовать в разных местах

    Parameters
    ----------
    values : NDArray[float64]
        набор значений
    bins : int, optional
        количество бинов, by default 15
    density : bool, optional
        density, by default False
    size : Tuple[float, float], optional
        размер plota, by default (7, 2)

    Returns
    -------
    FacetGrid
        класс графика
    """
    return displot(values, bins=bins, kde=density, height=size[0], aspect=size[1])


def recursive_chainer(
    trace: List[str],
    prob: float,
    transitions: Dict[str, Dict[str, float]],
    chains: List[List],
    dependent_stages: List[Tuple[str]] = None,
    independent_stages: List[Tuple[str]] = None,
    max_appearances: Dict[str, int] = None,
    min_appearances: Dict[str, int] = None,
    needable_stages: List[str] = None,
    threshold: float = 1e-05,
):
    """Рекурсивное построение потенциально возможных путей из словаря с переходами. + Есть
    возможность передать лист из пар этапов -> (главный, зависимый), то есть зависимый этап
    не появится в логе, без главного этапа. Есть возможность передать словарь с числом
    максимального количества определенного этапа, в словаре не обязательно указывать все этапы,
    по умолчанию пологается, что каждый этап может возникнуть неограниченное число раз

    Parameters:
    ----------
    trace : List[str]
        набор переходов (с учётом мнимых (мнимые этапы – этапы которые отсутствуют
        в логе ,но имеются на графе, чтобы иметь возможность определять с чего)
    prob : float
        вероятность перехода из родительского этапа в дочерний этап, by default = 1.0
    independent_stages : List[Tuple[str]]
        невозможные комбинации этапов (этапы которые не могут встретиться в одном экземпляре),
        by default None
    dependent_stages : List[Tuple[str]]
        обязательные комбинации этапов (этапы которые всегда появляются вместе), by default None
    max_appearances : Dict[str, int]
        максимальное возможное количество этапа в одном экземпляре – какое максимальное количество
        раз может встретиться этап в одном экземпляре, by default None
    min_appearances : Dict[str, int]
        минимальное возможное количество этапа в одном экземпляре – какое минимальное количество
        раз может встретиться этап в одном экземпляре, by default None
    needable_stages : List[str]
        обязательные этапы – этапы которые должны присутствовать в каждом экземпляре процесса, by
        default None
    threshold : float
        вероятность после которой пути отсекаются, by default 1e-05,


    """
    if trace[-1] == "end":
        # проверка на обязательные этапы в пути и что они указаны
        need_flag = any([action in trace for action in needable_stages]) if needable_stages is not None else True
        # проверка на мин кол-во этапов, если такие были встречены в trace
        min_appear = (
            all([trace.count(key) >= value for key, value in min_appearances.items() if key in trace])
            if min_appearances is not None
            else True
        )
        if min_appear and need_flag:
            chains.append((trace, prob))

    elif prob >= threshold:
        possible_actions = list(transitions[trace[-1]].keys())
        # удалит зависимые этапы, если в trace не появился главный этап
        if dependent_stages is not None:
            for main, depend in dependent_stages:
                if main not in trace and depend in possible_actions:
                    possible_actions.remove(depend)
        if independent_stages is not None:
            for stage_a, stage_b in independent_stages:
                if stage_a in trace and stage_b in possible_actions:
                    possible_actions.remove(stage_b)
                if stage_b in trace and stage_a in possible_actions:
                    possible_actions.remove(stage_a)
        # удалит этапы, которые уже встретились максимальное кол-во раз
        if max_appearances is not None:
            possible_actions = [
                action
                for action in possible_actions
                if max_appearances.get(action, float("+inf")) > trace.count(action)
            ]

        for action in possible_actions:
            recursive_chainer(
                trace=trace + [action],
                prob=prob * transitions[trace[-1]][action],
                transitions=transitions,
                chains=chains,
                dependent_stages=dependent_stages,
                max_appearances=max_appearances,
                min_appearances=min_appearances,
                needable_stages=needable_stages,
                threshold=threshold,
            )
