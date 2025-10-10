from collections.abc import Callable, Hashable, Iterable
from functools import reduce
from typing import TypeVar, overload

T = TypeVar("T")
TPost = TypeVar("TPost")
TPre = TypeVar("TPre")
K = TypeVar("K", bound=Hashable)
V = TypeVar("V")
type Filterer[T] = Callable[[T], bool]


@overload
def endomap(callable_: Callable[[TPre], TPost], sequence: list[TPre]) -> list[TPost]: ...
@overload
def endomap(callable_: Callable[[TPre], TPost], sequence: set[TPre]) -> set[TPost]: ...
@overload
def endomap(
    callable_: Callable[[TPre], TPost], sequence: tuple[TPre, ...]
) -> tuple[TPost, ...]: ...


def endomap(callable_, sequence):
    return type(sequence)(map(callable_, sequence))


@overload
def endofilter(callable_: Callable[[T], bool], sequence: list[T]) -> list[T]: ...
@overload
def endofilter(callable_: Callable[[T], bool], sequence: set[T]) -> set[T]: ...
@overload
def endofilter(callable_: Callable[[T], bool], sequence: tuple[T, ...]) -> tuple[T, ...]: ...


def endofilter(callable_, sequence):
    return type(sequence)(filter(callable_, sequence))


def lmap(callable_: Callable[[TPre], TPost], iterable: Iterable[TPre]) -> list[TPost]:
    return list(map(callable_, iterable))


def smap(callable_: Callable[[TPre], TPost], iterable: Iterable[TPre]) -> set[TPost]:
    return set(map(callable_, iterable))


def tmap(callable_: Callable[[TPre], TPost], iterable: Iterable[TPre]) -> tuple[TPost, ...]:
    return tuple(map(callable_, iterable))


def vmap(callable_: Callable[[TPre], TPost], dictionary: dict[K, TPre]) -> dict[K, TPost]:
    return {k: callable_(v) for k, v in dictionary.items()}


def kmap(callable_: Callable[[TPre], TPost], dictionary: dict[TPre, V]) -> dict[TPost, V]:
    return {callable_(k): v for k, v in dictionary.items()}


def dmap(callable_: Callable[[TPre], TPost], dictionary: dict[TPre, TPre]) -> dict[TPost, TPost]:
    return {callable_(k): callable_(v) for k, v in dictionary.items()}


def lfilter(filterer: Filterer[T], iterable: Iterable[T]) -> list[T]:
    return list(filter(filterer, iterable))


def sfilter(filterer: Filterer[T], iterable: Iterable[T]) -> set[T]:
    return set(filter(filterer, iterable))


def tfilter(filterer: Filterer[T], iterable: Iterable[T]) -> tuple[T, ...]:
    return tuple(filter(filterer, iterable))


def vfilter(filterer: Filterer[V], dictionary: dict[K, V]) -> dict[K, V]:
    return {k: v for k, v in dictionary.items() if filterer(v)}


def kfilter(filterer: Filterer[K], dictionary: dict[K, V]) -> dict[K, V]:
    return {k: v for k, v in dictionary.items() if filterer(k)}


def dfilter(filterer: Filterer[T], dictionary: dict[T, T]) -> dict[T, T]:
    return {k: v for k, v in dictionary.items() if filterer(k) and filterer(v)}


def identity[T](x: T) -> T:
    return x


def fold_dictionaries[K, V](dicts: Iterable[dict[K, V]]) -> dict[K, V]:
    def _or(dict1: dict[K, V], dict2: dict[K, V]) -> dict[K, V]:
        return dict1 | dict2

    return reduce(_or, dicts)
