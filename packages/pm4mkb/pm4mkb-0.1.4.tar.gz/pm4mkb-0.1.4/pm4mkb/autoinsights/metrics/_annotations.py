from __future__ import annotations

from enum import Enum
from itertools import chain, product
from typing import Iterable, NamedTuple

from pandas import DataFrame, MultiIndex


class MultiColumns(NamedTuple):
    """
    Класс колонок, которые будут отражены в автоинсайтах. Разделены на категории.

    Parameters
    ----------
    Enum : class
        Generic enumeration.
    """

    # Operation duration
    operation_increasing_duration: tuple[str, str]
    operation_stable_bottleneck: tuple[str, str]
    operation_variable_bottleneck: tuple[str, str]
    operation_one_incidents: tuple[str, str]
    operation_multi_incidents: tuple[str, str]
    # Process
    process_irregular_frequency: tuple[str, str]
    process_mistake: tuple[str, str]
    process_return: tuple[str, str]
    # Failure
    failure_mistake: tuple[str, str]
    failure_return: tuple[str, str]
    failure_structure: tuple[str, str]
    # Frequency loop
    loop_start: tuple[str, str]
    loop_self: tuple[str, str]
    loop_roundtrip: tuple[str, str]
    loop_ping_pong: tuple[str, str]
    loop_arbitrary: tuple[str, str]

    def as_header(self) -> MultiIndex:
        """
        Представление колонок в качестве двухуровнего header для DataFrame.

        Returns
        -------
        pd.MultiIndex
            На первом уровне "Категория", на втором уровне "Метрика".
        """
        header = DataFrame(self, columns=["Метрика", "Операция"])
        return MultiIndex.from_frame(header)


class InsightCategories(Enum):
    OPERATION_DURATION = "Длительность операции"
    PROCESS = "Длительность процесса"
    FAILURE = "Неуспех"
    LOOP = "Зацикленность"

    @classmethod
    def values(cls) -> list[str]:
        return [member.value for member in cls.__members__.values()]


class MetricNames(Enum):
    # Operation duration
    DURATION_INCREASE = "Растет со временем"
    STABLE_BOTTLENECK = "Bottle neck"
    VARIABLE_BOTTLENECK = "Нестандартизированная или ручная операция"
    # Incidents (duration)
    SINGLE = "Разовые инциденты"
    MULTI = "Многократные инциденты"
    # Process
    IRREGULAR = "Нерегулярная операция"
    # Failure
    MISTAKES = "Ошибки системы"
    RETURNS = "Возвраты и исправления"
    STRUCTURE = "Структурные причины"
    # Loop
    START = "В начало"
    SELF = "В себя"
    ROUNDTRIP = "«Возврат»"
    PING_PONG = "«Пинг-Понг»"
    ARBITRARY = "В произвольную операцию"

    @classmethod
    def _values_by_names(cls, names: Iterable[str]) -> list[str]:
        return [getattr(cls, name).value for name in names]

    @classmethod
    def as_mapping_to_insights(cls) -> Iterable[tuple[str, str]]:
        categorized_member_names = (
            ("DURATION_INCREASE", "STABLE_BOTTLENECK", "VARIABLE_BOTTLENECK", "SINGLE", "MULTI"),
            ("IRREGULAR", "MISTAKES", "RETURNS"),
            ("MISTAKES", "RETURNS", "STRUCTURE"),
            ("START", "SELF", "ROUNDTRIP", "PING_PONG", "ARBITRARY"),
        )
        metrics_of_insights = map(lambda cat_names: cls._values_by_names(cat_names), categorized_member_names)

        insight_metric_pairs: Iterable[Iterable[tuple[str, str]]] = (
            product([insight_category], metrics)
            for insight_category, metrics in zip(InsightCategories.values(), metrics_of_insights)
        )

        return chain(*insight_metric_pairs)


COLUMNS = MultiColumns(*MetricNames.as_mapping_to_insights())
