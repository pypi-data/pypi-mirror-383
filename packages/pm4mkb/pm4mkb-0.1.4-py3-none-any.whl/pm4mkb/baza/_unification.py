# Прошу не добавлять сюда annotations
import typing
from hashlib import sha256
from typing import NoReturn, Optional, Union, Iterable, Set, Tuple
from abc import ABCMeta
from pandas import DataFrame, Series
from loguru import logger


class ModuleType:
    "...."
    def __init__(self, _type: type, _childrens: Optional[Set[object]]) -> NoReturn:
        self._type = _type
        self._childrens = _childrens
        self._name = str(_type) if _type != Union else 'Union'

    def __eq__(self, __value: object) -> bool:
        try:
            # TODO проверить что работает нормально
            if self._type == Union and __value._type == Union:
                return self.all_in(__value, self)
            elif self._type == Union:
                return self.union_eq(self, __value)
            elif __value._type == Union:
                return self.union_eq(__value, self)
            elif self._type != __value._type:
                return False
            if self._childrens is not None and __value._childrens is not None:
                if ((len(self._childrens) == len(__value._childrens)) or
                        (self._type == dict and __value._type == dict)):
                    return self.desc_eq(self, __value)
                return False
            # логика верна, здесь и должно быть True
            return True
        except Exception:
            logger.warning('При проверке типов произошла ошибка')
            return False

    def __hash__(self) -> int:
        # Я пологаю, что вероятность возникновения коллизий очень мала
        inthash = int.from_bytes(sha256(bytes(self.__repr__(), encoding='utf8')).digest(), 'big')
        if self._type == Union:
            return inthash // 10
        return inthash

    def __repr__(self) -> str:
        return f'{self._name} -> ({self._childrens})'

    @staticmethod
    def desc_eq(left: object, right: object) -> bool:
        return all([_left == _right for _left, _right in zip(left._childrens, right._childrens)])

    @staticmethod
    def union_eq(left: object, right: object) -> bool:
        return any([_left == right for _left in left._childrens])

    @staticmethod
    def all_in(left: object, right: object) -> bool:
        return all([
            any([_left == _right for _right in right._childrens])
            for _left in left._childrens
        ])


def get_nvals(iterator: iter, ncheck: int = 32) -> set:
    all_types = []
    for _ in range(ncheck):
        try:
            all_types.append(next(iterator))
        except StopIteration:
            break
    return all_types


def get_origin(obj_type: type) -> type:
    # Ориентировано на цепочки из typing, Optional -> Union[None, ...]
    if hasattr(obj_type, '__origin__'):
        return obj_type.__origin__
    return obj_type


def get_args(obj_type: type) -> Optional[Tuple[type]]:
    # аргументы типизации, если пустые, то None
    if hasattr(obj_type, '__args__'):
        return obj_type.__args__
    return None


def get_argtypes(obj: object) -> Optional[Tuple[Iterable]]:
    # забирает типы и значения у объекта если итерируемый
    # иначе вернет None, верхнеуровневая типизация присутствует
    if isinstance(obj, (DataFrame, Series)):
        return (None, 'empty')
    if hasattr(type(obj), '__class__') and type(obj).__class__ == ABCMeta:
        return (None, 'empty')
    if isinstance(obj, Iterable):
        if isinstance(obj, dict):
            keys = get_nvals(iter(obj.keys()))
            vals = [obj[key] for key in keys]
            return ((keys, vals), 'dict')
        return (obj, 'obj')
    return (None, 'empty')


def get_moduletype(typing_object: type) -> ModuleType:
    """Генерит что-то похожее на дерево, где друг за другом идут типы,
    каждая ветка заканчивается пустым значением, операция сравнения реализована
    + о порядке инициализации беспокоится не требуется, сортировка по умолчанию.
    # TODO потенциально требуется еще провести тесты
    """
    subtypes = get_args(typing_object)
    deep_typing = (
        set([get_moduletype(sub_type) for sub_type in subtypes])
        if subtypes is not None else
        subtypes
    )
    return ModuleType(get_origin(typing_object), deep_typing)


def get_objecttype(obj: object) -> ModuleType:
    """Для полной типизации объекта, строит структуру подобно дереву,
    работает со всеми типами, с любой глубиной объектов
    """
    def dict_worker(items: Iterable) -> Iterable:
        if len(items) > 0:
            items = [get_objecttype(item) for item in items]
            uniq_items = set(items)
            return [ModuleType(typing.Union, uniq_items)] if len(uniq_items) > 1 else items
        return items

    sub_objects, rtype = get_argtypes(obj)
    if rtype == 'empty':
        deep_objects = None
    elif rtype == 'dict':
        keys, vals = sub_objects
        keys = dict_worker(keys)
        vals = dict_worker(vals)
        deep_objects = set(keys + vals) if len(keys) > 0 else None
    else:
        items = sub_objects
        try:
            items = [get_objecttype(item) for item in items] if obj not in items else None
        except ValueError:
            # только потому что типы pandas самые мерзкие в мире типы данных
            items = [get_objecttype(item) for item in items]
        if items is not None:
            uniq_items = set(items)
            deep_objects = uniq_items if len(uniq_items) <= 1 else {ModuleType(typing.Union, uniq_items)}
        else:
            deep_objects = None
    # if _safety_deep == N:
    #     logger.warning('Problems with autotypecheker, uwu')
    #     deep_objects = None
    return ModuleType(type(obj), deep_objects)
