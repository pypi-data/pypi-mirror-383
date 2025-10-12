"""
Defines classes responsible for managing different data operations through the `DataEditor` class.

Classes to process the `DataHolder` class data:
    DTypeManager: manages event log favorable data type conversion operations.
    DateTimeManager: manages event log datetime data.
    DurationManager: manages event log stage duration data.
    SortingManager: manages event log sorting operations.
    CalendarManager: manages event log calendar arrangement.
    SuccessManager: manages event log indication of case ID success.
"""

from __future__ import annotations

from .calendar import CalendarManager
from .data_type import DTypeManager
from .datetime import DateTimeManager
from .duration import DurationManager
from .sorting import SortingManager
from .success import SuccessManager


__all__ = [
    "DTypeManager",
    "DateTimeManager",
    "DurationManager",
    "SortingManager",
    "CalendarManager",
    "SuccessManager",
]
