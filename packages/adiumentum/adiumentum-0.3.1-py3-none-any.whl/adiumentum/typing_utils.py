import re
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from types import UnionType
from typing import Annotated, Any, Protocol, Self, TypeVar, Union

T = TypeVar("T")


type Atomic = int | float | str | bool | None
ClassInfo = type | UnionType | tuple["ClassInfo"]
JSONPrimitive = int | float | str | None
JSONDict = dict[str, Union[JSONPrimitive, "JSONDict", list[Union["JSONDict | JSONPrimitive"]]]]
JSONList = list[JSONPrimitive | JSONDict]


def areinstances(iterable_instance: Iterable[Any], class_or_tuple: ClassInfo) -> bool:
    return all(map(lambda inst: isinstance(inst, class_or_tuple), iterable_instance))


def fallback_if_none(orig: T | None, alt: T) -> T:
    return alt if (orig is None) else orig


def call_fallback_if_none(orig: T | None, alt: Callable[[], T]) -> T:
    return alt() if (orig is None) else orig


class SupportsGe(Protocol):
    def __ge__(self: T, __other: T) -> bool: ...


class SupportsGt(Protocol):
    def __gt__(self: T, __other: T) -> bool: ...


class SupportsLe(Protocol):
    def __le__(self: T, __other: T) -> bool: ...


class SupportsLt(Protocol):
    def __lt__(self: T, __other: T) -> bool: ...


@dataclass(frozen=True)
class _BaseMetadata:
    """Base class for all metadata.

    This exists mainly so that implementers
    can do `isinstance(..., BaseMetadata)` while traversing field annotations.
    """

    __slots__ = ()


@dataclass(frozen=True)
class Ge(_BaseMetadata):
    """Ge(ge=x) implies that the value must be greater than or equal to x.

    It can be used with any type that supports the ``>=`` operator,
    including numbers, dates and times, strings, sets, and so on.
    """

    ge: SupportsGe


@dataclass(frozen=True)
class Gt(_BaseMetadata):
    """Gt(gt=x) implies that the value must be greater than x.

    It can be used with any type that supports the ``>`` operator,
    including numbers, dates and times, strings, sets, and so on.
    """

    gt: SupportsGt


@dataclass(frozen=True)
class Lt(_BaseMetadata):
    """Lt(lt=x) implies that the value must be less than x.

    It can be used with any type that supports the ``<`` operator,
    including numbers, dates and times, strings, sets, and so on.
    """

    lt: SupportsLt


@dataclass(frozen=True)
class Le(_BaseMetadata):
    """Le(le=x) implies that the value must be less than x.

    It can be used with any type that supports the ``<=`` operator,
    including numbers, dates and times, strings, sets, and so on.
    """

    le: SupportsLe


class SupportsIO(ABC):
    @classmethod
    @abstractmethod
    def read(cls, read_path: Path) -> Self: ...

    @abstractmethod
    def write(self, write_path: Path) -> None: ...


class Pattern:
    DATE: re.Pattern[str] = re.compile(r"^[12]\d\d\d-(0?\d|1[012]|)-(0?\d|[12]\d|3[01])$")
    DATE_STRICT: re.Pattern[str] = re.compile(r"^[12]\d\d\d-(0\d|1[012]|)-(0\d|[12]\d|3[01])$")
    DATE_LOOSE: re.Pattern[str] = re.compile(r"(\d{2,4})[^\d](\d\d?)[^\d](\d\d?)")
    ID: re.Pattern[str] = re.compile(r"^[A-Za-z][A-Za-z0-9_]+$")
    ID_OR_2IDS: re.Pattern[str] = re.compile(r"^[A-Za-z][A-Za-z0-9_]+,[A-Za-z][A-Za-z0-9_]+$")
    NATURAL: re.Pattern[str] = re.compile(r"^[1-9][0-9]*$")
    PROPORTION: re.Pattern[str] = re.compile(r"^0?\.[0-9]+$")
    PROPORTION_OR_2: re.Pattern[str] = re.compile(r"^0?\.[0-9]+$|^0?\.[0-9]+,0?\.[0-9]+$")


TimeAmountRaw = str | int

Natural = Annotated[int, Ge(ge=0)]
Nonnegative = Annotated[float, Ge(ge=0)]
Positive = Annotated[float, Gt(gt=0)]
PositiveScore = Annotated[float, Gt(gt=0.0), Lt(lt=5.0)]
NegativeScore = Annotated[float, Gt(gt=-5.0), Lt(lt=0.0)]
Proportion = Annotated[float, Ge(ge=0.0), Le(le=1.0)]
NonnegativeInt = Annotated[int, Ge(ge=0)]
NonnegativeFloat = Annotated[float, Ge(ge=0.0)]
PolarityScore = Annotated[float, Ge(ge=-1.0), Le(le=1.0)]
