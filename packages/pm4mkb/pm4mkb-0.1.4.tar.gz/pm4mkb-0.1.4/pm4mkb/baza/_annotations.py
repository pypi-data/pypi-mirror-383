from typing import Union, TypeVar

from numpy import bool_, datetime64, number, str_

from pandas import DatetimeTZDtype

Case = Union[number, str_]
Stage = Union[number, str_]
DateTime = Union[datetime64, DatetimeTZDtype]
User = Union[number, str_]
Text = str_
Duration = number
CaseSuccess = bool_
T = TypeVar('T')
