from collections.abc import Callable, Hashable, Iterable
from functools import reduce
from typing import TypeVar

T = TypeVar("T")
H = TypeVar("H", bound=Hashable)
TPost = TypeVar("TPost")
TPre = TypeVar("TPre")
K = TypeVar("K", bound=Hashable)
V = TypeVar("V")
type Filterer[T] = Callable[[T], bool]

type IterableVal = list["ValType"] | set[Hashable] | tuple["ValType", ...]
type ValType = Hashable | IterableVal | dict[Hashable, "ValType"]
type IterReturnType = list[ValType] | set[Hashable] | tuple[ValType]
type Mergeable[K, T] = str | object | list[T] | set[T] | tuple[T] | dict[K, "Mergeable"]


def make_hashable(ob: object) -> Hashable:
    def make_sequence_hashable(ob: list[T] | set[T]) -> tuple[T, ...]:
        return tuple(ob)

    def make_dict_hashable(ob: dict[K, V]) -> tuple[tuple[K, V], ...]:
        return tuple(ob.items())

    if isinstance(ob, Hashable):
        return ob
    if isinstance(ob, list | set):
        return make_sequence_hashable(ob)
    if isinstance(ob, dict):
        return make_dict_hashable(ob)
    return str(ob)


def join_as_sequence(  # noqa: C901,PLR0911
    lv: ValType,
    rv: ValType,
    default_new_type: type[list] | type[tuple] | type[set] = tuple,
    add_duplicates: bool = True,
) -> IterableVal:
    def keep_duplicates(a: Iterable, _) -> Iterable:
        return a

    def remove_duplicates(a: Iterable, b) -> Iterable:
        compare = set(b) if isinstance(b, list | set | tuple) else {b}
        return filter(lambda x: x not in compare, a)

    filtr = keep_duplicates if add_duplicates else remove_duplicates

    if isinstance(lv, list):
        if isinstance(rv, list | set | tuple):
            return lv + list(filtr(rv, lv))
        else:
            return lv if rv in lv else [*lv, rv]
    if isinstance(lv, tuple):
        if isinstance(rv, list | set | tuple):
            return (*lv, *filtr(rv, lv))
        else:
            return lv if rv in lv else (*lv, rv)
    if isinstance(lv, set):
        if isinstance(rv, list | set | tuple):
            return {*lv, *filtr(map(make_hashable, rv), lv)}
        else:
            return lv if make_hashable(rv) in lv else {*lv, make_hashable(rv)}

    if isinstance(rv, list):
        return [lv, *filtr(rv, lv)]
    if isinstance(rv, tuple):
        return (lv, *filtr(rv, lv))
    if isinstance(rv, set):
        return {make_hashable(lv), *filtr(rv, make_hashable(lv))}

    return default_new_type((lv, rv))


def merge_dicts(
    *dicts: dict[Hashable, ValType],
    default_new_sequence: type[list] | type[tuple] | type[set] = tuple,
    add_duplicates: bool = True,
) -> dict[Hashable, ValType]:
    def merge_values(right_val: ValType, left_val: ValType) -> ValType:  # noqa: PLR0911
        if left_val == right_val:
            return left_val
        if isinstance(left_val, dict) and isinstance(right_val, dict):
            return merge_dicts(left_val, right_val, default_new_sequence=default_new_sequence)
        if left_val is None:
            return right_val
        if right_val is None:
            return left_val
        if isinstance(left_val, dict):
            return left_val
        if isinstance(right_val, dict):
            return right_val
        return join_as_sequence(
            left_val,
            right_val,
            default_new_type=default_new_sequence,
            add_duplicates=add_duplicates,
        )

    def merge(
        left: dict[Hashable, ValType], right: dict[Hashable, ValType]
    ) -> dict[Hashable, ValType]:
        common_keys: set[Hashable] = set(left).intersection(set(right))
        common: dict[Hashable, ValType] = {}
        for key in common_keys:
            lv, rv = left[key], right[key]
            new_dict: dict[Hashable, ValType] = {key: merge_values(lv, rv)}
            common.update(new_dict)

        return left | right | common

    return reduce(merge, dicts)
