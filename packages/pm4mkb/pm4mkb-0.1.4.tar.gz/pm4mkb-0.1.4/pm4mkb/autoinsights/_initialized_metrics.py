from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from _collections_abc import dict_keys

from .metrics import (
    ArbitraryLoop,
    FailureReturn,
    FailureStructure,
    IncreasingDuration,
    Irregular,
    Loop,
    OperationBottleneck,
    OperationOneIncidents,
    PingPong,
    ProcessMistake,
    ProcessMultiIncidents,
    StartLoop,
)

if TYPE_CHECKING:
    from ._auto_insights import AutoInsights
    from .metrics._base import Metric


class InsightfulMetrics(Enum):
    # Operation
    INCREASING_DURATION = (IncreasingDuration, "holder")
    STABLE_BOTTLENECK = (OperationBottleneck, "holder", "high_variance")
    VARIABLE_BOTTLENECK = (OperationBottleneck, "holder", "high_variance")
    ONE_INCIDENTS = (OperationOneIncidents, "holder")
    MULTI_INCIDENTS = (ProcessMultiIncidents, "holder", "successful_stage")
    # Process
    IRREGULAR_FREQUENCY = (Irregular, "holder", "successful_stage")
    MISTAKE = (ProcessMistake, "holder", "successful_stage", "MISTAKE_LEMMAS_PATH")
    RETURN = (ProcessMistake, "holder", "successful_stage", "REVERSAL_LEMMAS_PATH")
    # Failure
    FAILURE_MISTAKE = (FailureReturn, "holder", "successful_stage", "MISTAKE_LEMMAS_PATH")
    FAILURE_RETURN = (FailureReturn, "holder", "successful_stage", "REVERSAL_LEMMAS_PATH")
    FAILURE_STRUCTURE = (FailureStructure, "holder", "successful_stage", "MISTAKE_LEMMAS_PATH")
    # Frequency loop
    START = (StartLoop, "holder", "starting_stage")
    SELF = (Loop, "holder", "loop_length")
    ROUNDTRIP = (Loop, "holder", "loop_length")
    PING_PONG = (PingPong, "holder")
    ARBITRARY = (ArbitraryLoop, "holder")

    @classmethod
    def keys(
        cls,
    ) -> dict_keys[str]:
        return cls.__members__.keys()

    @classmethod
    def values(
        cls,
    ) -> tuple[tuple[Metric, str], ...]:
        return tuple(map(lambda member: member.value, cls.__members__.values()))


# TODO simplify
def initialize_metrics(insights_instance: AutoInsights) -> dict[str, Metric]:
    metrics_instances = dict.fromkeys(InsightfulMetrics.keys())

    for model_name, (model, *arg_names) in zip(InsightfulMetrics.keys(), InsightfulMetrics.values()):
        # Define arguments of the model with instance values from the self
        arguments = {name: getattr(insights_instance, name, None) for name in arg_names}

        # Replace the names of class attributes with appropriate for model
        for path_attribute_name in ("MISTAKE_LEMMAS_PATH", "REVERSAL_LEMMAS_PATH"):
            if arguments.get(path_attribute_name):
                # Metric class model accepts `_mistake_words_path` as an argument name
                arguments["_mistake_words_path"] = arguments.pop(path_attribute_name)

        # Assign extra arguments that are not in the self
        if model_name == "STABLE_BOTTLENECK":
            arguments["high_variance"] = False
        elif model_name == "VARIABLE_BOTTLENECK":
            arguments["high_variance"] = True
        elif model_name == "SELF":
            arguments["loop_length"] = 1
        elif model_name == "ROUNDTRIP":
            arguments["loop_length"] = 2
        elif model_name == "TRUE_TEXT":
            arguments["truthful"] = True
        elif model_name == "FALSE_TEXT":
            arguments["truthful"] = False

        metrics_instances[model_name] = model(**arguments)

    return metrics_instances
