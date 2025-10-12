from __future__ import annotations
from typing import TYPE_CHECKING, Tuple

from numpy import concatenate
from numpy.random import normal, shuffle, choice

if TYPE_CHECKING:
    from typing import List
    from numpy import float64
    from numpy.typing import NDArray


class DURATION_ERRORS(Tuple):
    """Ошибки для функции генерации длительности"""
    MEAN: str = 'Среднее не может быть отрицательным или превышать 1 год'
    VAR: str = 'Дисперсия не может быть отрицательной или превышать 1 год'
    INC_LEN: str = 'Размерности списков не совпадают'
    TYPE: str = 'Тип данных границ не является допустимым'
    BAD_GEN: str = 'Не удалось сгенерировать достаточное количество значений, попробуйте проверить значения'


def get_duration(mean_list: List[float], var_list: List[float], weights: List[float] = None, sample: int = 1000,
                 borders: Tuple[float] = (0, float('+inf')), attempt2gen: int = 5) -> NDArray[float64]:
    """По сути "смешиватель" нормальных распределений с учетом вклада каждого смешиваемого
    распределения на итоговый результат. Чем больше параметр sample, тем более предсказуемым
    будет результат (рекомендуется использовать plot_dist, чтобы наглядно увидеть результат
    генерации)

    Parameters
    ----------
    mean_list : List[float]
        набор медианных значений для нормальных распределений
    var_list : List[float]
        набор дисперсий значений для нормальных распределений
    weights : List[float], optional
        веса или вклад каждого распределения в итоговый набор значений, by default None
    sample : int, optional
        размер получаемой выборки, by default 1000
    borders : Tuple[float], optional
        границы, которые явно обрезают выходящие за них значения (это значит, что если установить
        границы (0, -1), то генерация вернет ошибку, так как итоговая выборка не наберет
        n = sample элементов), by default (0, float('+inf'))
    attempt2gen : int, optional
        попытки генерации, если интервал в borders слишком мал, или распределения сильно
        размыто, то делается несколько попыток сгенерировать выборку и отфильтровать её, чтобы
        достич нужного n = sample количества элементов, by default 5

    Returns
    -------
    NDArray[float64]
        набор из времени в секундах
    """
    def is_numeric(border_object: object) -> bool:
        return isinstance(border_object, float) or isinstance(border_object, int)
    # веса для генерации, может помочь настроить например выброс
    weights = (
        [weight / sum(weights) for weight in weights]
        if weights is not None else
        [1 / len(mean_list) for _ in mean_list]
    )
    # разные проверки, для минимизации непредвиденых генераций
    assert all([mean > 0 and mean < 365 * 24 * 60 * 60 for mean in mean_list]), ValueError(DURATION_ERRORS.MEAN)
    assert all([mean > 0 and mean < 365 * 24 * 60 * 60 for mean in var_list]), ValueError(DURATION_ERRORS.VAR)
    assert len(mean_list) == len(var_list) and len(mean_list) == len(weights), ValueError(DURATION_ERRORS.INC_LEN)
    assert is_numeric(borders[0]) and is_numeric(borders[1]), ValueError(DURATION_ERRORS.TYPE)

    local_sample = sample
    while attempt2gen > 0:
        duration_array = concatenate([
            normal(mean, var, int(local_sample * weight))
            for mean, var, weight in zip(mean_list, var_list, weights)
        ])
        shuffle(duration_array)
        # по умолчанию не генерируется время меньше 0, но если задать левую границу самому, то можно
        duration_array = duration_array[((duration_array >= borders[0]) & (duration_array <= borders[1]))]
        if duration_array.shape[0] >= sample:
            return choice(duration_array, size=sample)

        local_sample = int(local_sample * 1.2)
        attempt2gen -= 1

    raise RuntimeError(DURATION_ERRORS.BAD_GEN)
