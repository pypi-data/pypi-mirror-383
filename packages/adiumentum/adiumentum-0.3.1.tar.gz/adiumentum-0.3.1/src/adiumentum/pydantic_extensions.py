"""
Idea: make BaseSequence[C, T] type,
    where C is list|set|tuple and T is the element type
"""

import json
from abc import ABC, abstractmethod
from collections.abc import Callable, Hashable, Mapping
from pathlib import Path
from types import GenericAlias
from typing import (
    Any,
    Literal,
    Self,
    TypeVar,
    cast,
    get_args,
)

from pydantic import ConfigDict, GetCoreSchemaHandler, GetJsonSchemaHandler, TypeAdapter
from pydantic.config import ExtraValues
from pydantic.fields import FieldInfo
from pydantic.json_schema import (
    DEFAULT_REF_TEMPLATE,
    GenerateJsonSchema,
    JsonSchemaMode,
    JsonSchemaValue,
)
from pydantic.main import IncEx
from pydantic_core import CoreSchema, core_schema

from .io_utils import JSONDict, write_json

T = TypeVar("T")
K_ = TypeVar("K_", bound=Hashable)
V_ = TypeVar("V_")
Mode = Literal["json", "python"] | str


VALID_MODES: set[Literal["json", "python"]] = {"json", "python"}


# TODO: next step: create BaseList (BaseModelList?)
# FoodPlanRaw, Entries, WeightSessionPlan, WorkoutPlanRaw, Partition


class AbstractCustom(ABC):
    model_config: ConfigDict = ConfigDict()
    __pydantic_core_schema__: CoreSchema

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.model_validate,
            core_schema.dict_schema(),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        core_schema: CoreSchema,
        handler: GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        json_schema = handler(core_schema)
        json_schema = handler.resolve_ref_schema(json_schema)
        return json_schema

    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        TypeError(f"Use `model_validate` to instantiate {self.__class__.__name__}")

    # @abstractmethod
    # def __init__(**data: Any) -> None: ...

    @classmethod
    @abstractmethod
    def get_adapter(cls) -> TypeAdapter: ...

    @abstractmethod
    def __repr__(self) -> str: ...

    @abstractmethod
    def __str__(self) -> str: ...

    @classmethod
    def model_fields(cls) -> dict[str, FieldInfo]:
        return {}

    @property
    def model_extra(self) -> dict[str, Any] | None:
        return None

    @property
    def model_fields_set(self) -> set[str]:
        return set()

    @classmethod
    @abstractmethod
    def model_construct(cls, _fields_set: set[str] | None = None, **values: Any) -> Self: ...

    @abstractmethod
    def model_copy(
        self, *, update: Mapping[str, Any] | None = None, deep: bool = False
    ) -> Self: ...

    def model_dump(
        self,
        *,
        mode: Literal["json", "python"] | str = "python",
        include: IncEx | None = None,
        exclude: IncEx | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        exclude_computed_fields: bool = False,
        round_trip: bool = False,
        warnings: (bool | Literal["none", "warn", "error"]) = True,
        fallback: Callable[[Any], Any] | None = None,
        serialize_as_any: bool = False,
    ) -> dict[str, Any]:
        if mode not in VALID_MODES:
            raise ValueError
        if exclude_computed_fields:
            raise ValueError

        return self.get_adapter().dump_python(
            self.pre_dump_hook(mode=mode),
            mode=mode,
            include=include,
            exclude=exclude,
            context=context,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
            fallback=fallback,
            serialize_as_any=serialize_as_any,
        )

    def model_dump_json(
        self,
        *,
        indent: int | None = None,
        ensure_ascii: bool = False,
        include: IncEx | None = None,
        exclude: IncEx | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        exclude_computed_fields: bool = False,
        round_trip: bool = False,
        warnings: (bool | Literal["none", "warn", "error"]) = True,
        fallback: Callable[[Any], Any] | None = None,
        serialize_as_any: bool = False,
    ) -> str:
        if ensure_ascii or exclude_computed_fields:
            raise ValueError
        from_hook = self.pre_dump_hook(mode="json")
        return (
            self.get_adapter()
            .dump_json(
                from_hook,
                indent=indent,
                include=include,
                exclude=exclude,
                context=context,
                by_alias=by_alias,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                exclude_none=exclude_none,
                round_trip=round_trip,
                warnings=warnings,
                fallback=fallback,
                serialize_as_any=serialize_as_any,
            )
            .decode("utf-8")
        )

    @classmethod
    def model_json_schema(
        cls,
        by_alias: bool = True,
        ref_template: str = DEFAULT_REF_TEMPLATE,
        schema_generator: type[GenerateJsonSchema] = GenerateJsonSchema,
        mode: JsonSchemaMode = "validation",
        *,
        union_format: Literal["any_of", "primitive_type_array"] = "any_of",
    ) -> dict[str, Any]:
        return cls.get_adapter().json_schema(
            by_alias=by_alias,
            ref_template=ref_template,
            schema_generator=schema_generator,
            mode=mode,
        )

    @classmethod
    def model_parametrized_name(cls, params: tuple[type[Any], ...]) -> str:
        raise NotImplementedError

    @classmethod
    def model_validate(
        cls,
        obj: Any,
        *,
        strict: bool | None = None,
        extra: ExtraValues | None = None,
        from_attributes: bool | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
    ) -> Self:
        if extra:
            raise ValueError
        adapter = cls.get_adapter()
        obj = cls.pre_validation_hook_python(obj)
        obj = adapter.validate_python(
            obj,
            strict=strict,
            from_attributes=from_attributes,
            context=context,
            by_alias=by_alias,
            by_name=by_name,
        )
        validated = cls(obj)
        return cls.post_validation_hook(validated)

    @classmethod
    def model_validate_json(
        cls,
        json_data: str | bytes | bytearray,
        *,
        strict: bool | None = None,
        extra: ExtraValues | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
    ) -> Self:
        if extra:
            raise ValueError
        adapter = cls.get_adapter()
        json_string = cls.pre_validation_hook_json(json_data)
        raw_validated = adapter.validate_json(
            json_string,
            strict=strict,
            context=context,
            by_alias=by_alias,
            by_name=by_name,
        )
        validated = cls(raw_validated)
        return cls.post_validation_hook(validated)

    @classmethod
    @abstractmethod
    def model_validate_strings(
        cls,
        obj: Any,
        *,
        strict: bool | None = None,
        extra: ExtraValues | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        by_name: bool | None = None,
    ) -> Self: ...

    @property
    def __annotations__(self) -> dict[str, Any]:  # type: ignore
        return self.get_adapter().__annotations__

    @classmethod
    def read(cls, read_path: Path) -> Self:
        return cls.model_validate_json(read_path.read_text())

    def write(self, write_path: Path) -> None:
        write_json(cast(JSONDict, self.model_dump(mode="json")), write_path)

    @staticmethod
    def pre_validation_hook_python(python_dict: dict) -> dict:
        return python_dict

    @staticmethod
    def pre_validation_hook_json(json_string: str | bytes | bytearray) -> str | bytes | bytearray:
        return json_string

    @staticmethod
    def post_validation_hook(validated: T) -> T:
        return validated

    def pre_dump_hook(self, *, mode: Mode) -> Self:
        if mode not in VALID_MODES:
            raise ValueError
        return self

    def post_dump_hook(self, dumped: T, *, mode: Mode) -> T:
        return dumped

    def schema(self) -> CoreSchema:
        return self.get_adapter().core_schema

    def schema_json(self) -> str:
        return json.dumps(self.model_json_schema())


class BaseDict[K, V](dict[K, V], AbstractCustom):
    """
    Dictionary type leveraging pydantic for validation and JSON serialization.
    """

    @classmethod
    def get_adapter(cls) -> TypeAdapter[dict[K, V]]:
        """Return a TypeAdapter for this subclass, preserving its key/value types."""
        for base in getattr(cls, "__orig_bases__", []):
            if isinstance(base, GenericAlias):
                key_type, val_type = get_args(base)
                return TypeAdapter(dict[key_type, val_type])  # type: ignore[valid-type]
        raise TypeError("Key and value types not found.")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{dict.__repr__(self)}"

    def __str__(self) -> str:
        raise NotImplementedError


class BaseList[T](list[T], AbstractCustom):
    """
    Dictionary type leveraging pydantic for validation and JSON serialization.
    """

    @classmethod
    def get_adapter(cls) -> TypeAdapter[list[T]]:
        """Return a TypeAdapter for this subclass, preserving its key/value types."""
        for base in getattr(cls, "__orig_bases__", []):
            if isinstance(base, GenericAlias):
                element_type = get_args(base)[0]
                return TypeAdapter(list[element_type])  # type: ignore[valid-type]
        raise TypeError("Key and value types not found.")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{list.__repr__(self)}"

    def __str__(self) -> str:
        raise NotImplementedError


class BaseSet[T](set[T], AbstractCustom):
    """
    Dictionary type leveraging pydantic for validation and JSON serialization.

    TODO: make dump as list if not all members hashable.
    """

    @classmethod
    def get_adapter(cls) -> TypeAdapter[set[T]]:
        """Return a TypeAdapter for this subclass, preserving its key/value types."""
        for base in getattr(cls, "__orig_bases__", []):
            if isinstance(base, GenericAlias):
                element_type = get_args(base)[0]
                return TypeAdapter(set[element_type])  # type: ignore[valid-type]
        raise TypeError("Key and value types not found.")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}{set.__repr__(self)}"

    def __str__(self) -> str:
        raise NotImplementedError

    def model_dump(
        self,
        *,
        mode: Literal["json", "python"] | str = "python",
        include: IncEx | None = None,
        exclude: IncEx | None = None,
        context: Any | None = None,
        by_alias: bool | None = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        exclude_computed_fields: bool = False,
        round_trip: bool = False,
        warnings: (bool | Literal["none", "warn", "error"]) = True,
        fallback: Callable[[Any], Any] | None = None,
        serialize_as_any: bool = False,
    ) -> dict[str, Any]:
        if mode not in VALID_MODES:
            raise ValueError
        if exclude_computed_fields:
            raise ValueError

        return BaseList.model_validate(self).model_dump(
            mode=mode,
            include=include,
            exclude=exclude,
            context=context,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
            fallback=fallback,
            serialize_as_any=serialize_as_any,
        )
