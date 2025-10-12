from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from dataclasses import asdict, dataclass
from functools import _lru_cache_wrapper, cached_property, partial, reduce, wraps
from inspect import getattr_static
from pathlib import Path
from re import findall
from types import (
    BuiltinFunctionType,
    FunctionType,
    MethodDescriptorType,
    MethodType,
    MethodWrapperType,
    WrapperDescriptorType,
)
from typing import TYPE_CHECKING, Any, Literal, TypeGuard, cast, overload, override

from whenever import Date, PlainDateTime, Time, TimeDelta, ZonedDateTime

from utilities.reprlib import get_repr, get_repr_and_class
from utilities.sentinel import Sentinel, is_sentinel, sentinel
from utilities.types import Dataclass, Number, SupportsRichComparison, TypeLike

if TYPE_CHECKING:
    from collections.abc import Container


def apply_decorators[F1: Callable, F2: Callable](
    func: F1, /, *decorators: Callable[[F2], F2]
) -> F1:
    """Apply a set of decorators to a function."""
    return reduce(_apply_decorators_one, decorators, func)


def _apply_decorators_one[F: Callable](acc: F, el: Callable[[Any], Any], /) -> F:
    return el(acc)


##


@overload
def ensure_bool(obj: Any, /, *, nullable: bool) -> bool | None: ...
@overload
def ensure_bool(obj: Any, /, *, nullable: Literal[False] = False) -> bool: ...
def ensure_bool(obj: Any, /, *, nullable: bool = False) -> bool | None:
    """Ensure an object is a boolean."""
    try:
        return ensure_class(obj, bool, nullable=nullable)
    except EnsureClassError as error:
        raise EnsureBoolError(obj=error.obj, nullable=nullable) from None


@dataclass(kw_only=True, slots=True)
class EnsureBoolError(Exception):
    obj: Any
    nullable: bool

    @override
    def __str__(self) -> str:
        return _make_error_msg(self.obj, "a boolean", nullable=self.nullable)


##


@overload
def ensure_bytes(obj: Any, /, *, nullable: bool) -> bytes | None: ...
@overload
def ensure_bytes(obj: Any, /, *, nullable: Literal[False] = False) -> bytes: ...
def ensure_bytes(obj: Any, /, *, nullable: bool = False) -> bytes | None:
    """Ensure an object is a bytesean."""
    try:
        return ensure_class(obj, bytes, nullable=nullable)
    except EnsureClassError as error:
        raise EnsureBytesError(obj=error.obj, nullable=nullable) from None


@dataclass(kw_only=True, slots=True)
class EnsureBytesError(Exception):
    obj: Any
    nullable: bool

    @override
    def __str__(self) -> str:
        return _make_error_msg(self.obj, "a byte string", nullable=self.nullable)


##


@overload
def ensure_class[T](obj: Any, cls: type[T], /, *, nullable: bool) -> T | None: ...
@overload
def ensure_class[T](
    obj: Any, cls: type[T], /, *, nullable: Literal[False] = False
) -> T: ...
@overload
def ensure_class[T1, T2](
    obj: Any, cls: tuple[type[T1], type[T2]], /, *, nullable: bool
) -> T1 | T2 | None: ...
@overload
def ensure_class[T1, T2](
    obj: Any, cls: tuple[type[T1], type[T2]], /, *, nullable: Literal[False] = False
) -> T1 | T2: ...
@overload
def ensure_class[T1, T2, T3](
    obj: Any, cls: tuple[type[T1], type[T2], type[T3]], /, *, nullable: bool
) -> T1 | T2 | T3 | None: ...
@overload
def ensure_class[T1, T2, T3](
    obj: Any,
    cls: tuple[type[T1], type[T2], type[T3]],
    /,
    *,
    nullable: Literal[False] = False,
) -> T1 | T2 | T3: ...
@overload
def ensure_class[T1, T2, T3, T4](
    obj: Any, cls: tuple[type[T1], type[T2], type[T3], type[T4]], /, *, nullable: bool
) -> T1 | T2 | T3 | T4 | None: ...
@overload
def ensure_class[T1, T2, T3, T4](
    obj: Any,
    cls: tuple[type[T1], type[T2], type[T3], type[T4]],
    /,
    *,
    nullable: Literal[False] = False,
) -> T1 | T2 | T3 | T4: ...
@overload
def ensure_class[T1, T2, T3, T4, T5](
    obj: Any,
    cls: tuple[type[T1], type[T2], type[T3], type[T4], type[T5]],
    /,
    *,
    nullable: bool,
) -> T1 | T2 | T3 | T4 | T5 | None: ...
@overload
def ensure_class[T1, T2, T3, T4, T5](
    obj: Any,
    cls: tuple[type[T1], type[T2], type[T3], type[T4], type[T5]],
    /,
    *,
    nullable: Literal[False] = False,
) -> T1 | T2 | T3 | T4 | T5: ...
@overload
def ensure_class[T](
    obj: Any, cls: TypeLike[T], /, *, nullable: bool = False
) -> Any: ...
def ensure_class[T](obj: Any, cls: TypeLike[T], /, *, nullable: bool = False) -> Any:
    """Ensure an object is of the required class."""
    if isinstance(obj, cls) or ((obj is None) and nullable):
        return obj
    raise EnsureClassError(obj=obj, cls=cls, nullable=nullable)


@dataclass(kw_only=True, slots=True)
class EnsureClassError(Exception):
    obj: Any
    cls: TypeLike[Any]
    nullable: bool

    @override
    def __str__(self) -> str:
        return _make_error_msg(
            self.obj,
            f"an instance of {get_class_name(self.cls)!r}",
            nullable=self.nullable,
        )


##


@overload
def ensure_date(obj: Any, /, *, nullable: bool) -> Date | None: ...
@overload
def ensure_date(obj: Any, /, *, nullable: Literal[False] = False) -> Date: ...
def ensure_date(obj: Any, /, *, nullable: bool = False) -> Date | None:
    """Ensure an object is a date."""
    try:
        return ensure_class(obj, Date, nullable=nullable)
    except EnsureClassError as error:
        raise EnsureDateError(obj=error.obj, nullable=nullable) from None


@dataclass(kw_only=True, slots=True)
class EnsureDateError(Exception):
    obj: Any
    nullable: bool

    @override
    def __str__(self) -> str:
        return _make_error_msg(self.obj, "a date", nullable=self.nullable)


##


@overload
def ensure_float(obj: Any, /, *, nullable: bool) -> float | None: ...
@overload
def ensure_float(obj: Any, /, *, nullable: Literal[False] = False) -> float: ...
def ensure_float(obj: Any, /, *, nullable: bool = False) -> float | None:
    """Ensure an object is a float."""
    try:
        return ensure_class(obj, float, nullable=nullable)
    except EnsureClassError as error:
        raise EnsureFloatError(obj=error.obj, nullable=nullable) from None


@dataclass(kw_only=True, slots=True)
class EnsureFloatError(Exception):
    obj: Any
    nullable: bool

    @override
    def __str__(self) -> str:
        return _make_error_msg(self.obj, "a float", nullable=self.nullable)


##


@overload
def ensure_int(obj: Any, /, *, nullable: bool) -> int | None: ...
@overload
def ensure_int(obj: Any, /, *, nullable: Literal[False] = False) -> int: ...
def ensure_int(obj: Any, /, *, nullable: bool = False) -> int | None:
    """Ensure an object is an integer."""
    try:
        return ensure_class(obj, int, nullable=nullable)
    except EnsureClassError as error:
        raise EnsureIntError(obj=error.obj, nullable=nullable) from None


@dataclass(kw_only=True, slots=True)
class EnsureIntError(Exception):
    obj: Any
    nullable: bool

    @override
    def __str__(self) -> str:
        return _make_error_msg(self.obj, "an integer", nullable=self.nullable)


##


@overload
def ensure_member[T](
    obj: Any, container: Container[T], /, *, nullable: bool
) -> T | None: ...
@overload
def ensure_member[T](
    obj: Any, container: Container[T], /, *, nullable: Literal[False] = False
) -> T: ...
def ensure_member[T](
    obj: Any, container: Container[T], /, *, nullable: bool = False
) -> T | None:
    """Ensure an object is a member of the container."""
    if (obj in container) or ((obj is None) and nullable):
        return obj
    raise EnsureMemberError(obj=obj, container=container, nullable=nullable)


@dataclass(kw_only=True, slots=True)
class EnsureMemberError(Exception):
    obj: Any
    container: Container[Any]
    nullable: bool

    @override
    def __str__(self) -> str:
        return _make_error_msg(
            self.obj, f"a member of {get_repr(self.container)}", nullable=self.nullable
        )


##


def ensure_not_none[T](obj: T | None, /, *, desc: str = "Object") -> T:
    """Ensure an object is not None."""
    if obj is None:
        raise EnsureNotNoneError(desc=desc)
    return obj


@dataclass(kw_only=True, slots=True)
class EnsureNotNoneError(Exception):
    desc: str = "Object"

    @override
    def __str__(self) -> str:
        return f"{self.desc} must not be None"


##


@overload
def ensure_number(obj: Any, /, *, nullable: bool) -> Number | None: ...
@overload
def ensure_number(obj: Any, /, *, nullable: Literal[False] = False) -> Number: ...
def ensure_number(obj: Any, /, *, nullable: bool = False) -> Number | None:
    """Ensure an object is a number."""
    try:
        return ensure_class(obj, (int, float), nullable=nullable)
    except EnsureClassError as error:
        raise EnsureNumberError(obj=error.obj, nullable=nullable) from None


@dataclass(kw_only=True, slots=True)
class EnsureNumberError(Exception):
    obj: Any
    nullable: bool

    @override
    def __str__(self) -> str:
        return _make_error_msg(self.obj, "a number", nullable=self.nullable)


##


@overload
def ensure_path(obj: Any, /, *, nullable: bool) -> Path | None: ...
@overload
def ensure_path(obj: Any, /, *, nullable: Literal[False] = False) -> Path: ...
def ensure_path(obj: Any, /, *, nullable: bool = False) -> Path | None:
    """Ensure an object is a Path."""
    try:
        return ensure_class(obj, Path, nullable=nullable)
    except EnsureClassError as error:
        raise EnsurePathError(obj=error.obj, nullable=nullable) from None


@dataclass(kw_only=True, slots=True)
class EnsurePathError(Exception):
    obj: Any
    nullable: bool

    @override
    def __str__(self) -> str:
        return _make_error_msg(self.obj, "a Path", nullable=self.nullable)


##


@overload
def ensure_plain_date_time(obj: Any, /, *, nullable: bool) -> PlainDateTime | None: ...
@overload
def ensure_plain_date_time(
    obj: Any, /, *, nullable: Literal[False] = False
) -> PlainDateTime: ...
def ensure_plain_date_time(
    obj: Any, /, *, nullable: bool = False
) -> PlainDateTime | None:
    """Ensure an object is a plain date-time."""
    try:
        return ensure_class(obj, PlainDateTime, nullable=nullable)
    except EnsureClassError as error:
        raise EnsurePlainDateTimeError(obj=error.obj, nullable=nullable) from None


@dataclass(kw_only=True, slots=True)
class EnsurePlainDateTimeError(Exception):
    obj: Any
    nullable: bool

    @override
    def __str__(self) -> str:
        return _make_error_msg(self.obj, "a plain date-time", nullable=self.nullable)


##


@overload
def ensure_str(obj: Any, /, *, nullable: bool) -> str | None: ...
@overload
def ensure_str(obj: Any, /, *, nullable: Literal[False] = False) -> str: ...
def ensure_str(obj: Any, /, *, nullable: bool = False) -> str | None:
    """Ensure an object is a string."""
    try:
        return ensure_class(obj, str, nullable=nullable)
    except EnsureClassError as error:
        raise EnsureStrError(obj=error.obj, nullable=nullable) from None


@dataclass(kw_only=True, slots=True)
class EnsureStrError(Exception):
    obj: Any
    nullable: bool

    @override
    def __str__(self) -> str:
        return _make_error_msg(self.obj, "a string", nullable=self.nullable)


##


@overload
def ensure_time(obj: Any, /, *, nullable: bool) -> Time | None: ...
@overload
def ensure_time(obj: Any, /, *, nullable: Literal[False] = False) -> Time: ...
def ensure_time(obj: Any, /, *, nullable: bool = False) -> Time | None:
    """Ensure an object is a time."""
    try:
        return ensure_class(obj, Time, nullable=nullable)
    except EnsureClassError as error:
        raise EnsureTimeError(obj=error.obj, nullable=nullable) from None


@dataclass(kw_only=True, slots=True)
class EnsureTimeError(Exception):
    obj: Any
    nullable: bool

    @override
    def __str__(self) -> str:
        return _make_error_msg(self.obj, "a time", nullable=self.nullable)


##


@overload
def ensure_time_delta(obj: Any, /, *, nullable: bool) -> TimeDelta | None: ...
@overload
def ensure_time_delta(
    obj: Any, /, *, nullable: Literal[False] = False
) -> TimeDelta: ...
def ensure_time_delta(obj: Any, /, *, nullable: bool = False) -> TimeDelta | None:
    """Ensure an object is a timedelta."""
    try:
        return ensure_class(obj, TimeDelta, nullable=nullable)
    except EnsureClassError as error:
        raise EnsureTimeDeltaError(obj=error.obj, nullable=nullable) from None


@dataclass(kw_only=True, slots=True)
class EnsureTimeDeltaError(Exception):
    obj: Any
    nullable: bool

    @override
    def __str__(self) -> str:
        return _make_error_msg(self.obj, "a time-delta", nullable=self.nullable)


##


@overload
def ensure_zoned_date_time(obj: Any, /, *, nullable: bool) -> ZonedDateTime | None: ...
@overload
def ensure_zoned_date_time(
    obj: Any, /, *, nullable: Literal[False] = False
) -> ZonedDateTime: ...
def ensure_zoned_date_time(
    obj: Any, /, *, nullable: bool = False
) -> ZonedDateTime | None:
    """Ensure an object is a zoned date-time."""
    try:
        return ensure_class(obj, ZonedDateTime, nullable=nullable)
    except EnsureClassError as error:
        raise EnsureZonedDateTimeError(obj=error.obj, nullable=nullable) from None


@dataclass(kw_only=True, slots=True)
class EnsureZonedDateTimeError(Exception):
    obj: Any
    nullable: bool

    @override
    def __str__(self) -> str:
        return _make_error_msg(self.obj, "a zoned date-time", nullable=self.nullable)


##


def first[T](pair: tuple[T, Any], /) -> T:
    """Get the first element in a pair."""
    return pair[0]


##


@overload
def get_class[T](obj: type[T], /) -> type[T]: ...
@overload
def get_class[T](obj: T, /) -> type[T]: ...
def get_class[T](obj: T | type[T], /) -> type[T]:
    """Get the class of an object, unless it is already a class."""
    return obj if isinstance(obj, type) else type(obj)


##


def get_class_name(obj: Any, /, *, qual: bool = False) -> str:
    """Get the name of the class of an object, unless it is already a class."""
    cls = get_class(obj)
    return f"{cls.__module__}.{cls.__qualname__}" if qual else cls.__name__


##


def get_func_name(obj: Callable[..., Any], /) -> str:
    """Get the name of a callable."""
    if isinstance(obj, BuiltinFunctionType):
        return obj.__name__
    if isinstance(obj, FunctionType):
        name = obj.__name__
        pattern = r"^.+\.([A-Z]\w+\." + name + ")$"
        try:
            (full_name,) = findall(pattern, obj.__qualname__)
        except ValueError:
            return name
        return full_name
    if isinstance(obj, MethodType):
        return f"{get_class_name(obj.__self__)}.{obj.__name__}"
    if isinstance(
        obj,
        MethodType | MethodDescriptorType | MethodWrapperType | WrapperDescriptorType,
    ):
        return obj.__qualname__
    if isinstance(obj, _lru_cache_wrapper):
        return cast("Any", obj).__name__
    if isinstance(obj, partial):
        return get_func_name(obj.func)
    return get_class_name(obj)


##


def get_func_qualname(obj: Callable[..., Any], /) -> str:
    """Get the qualified name of a callable."""
    if isinstance(
        obj, BuiltinFunctionType | FunctionType | MethodType | _lru_cache_wrapper
    ):
        return f"{obj.__module__}.{obj.__qualname__}"
    if isinstance(
        obj, MethodDescriptorType | MethodWrapperType | WrapperDescriptorType
    ):
        return f"{obj.__objclass__.__module__}.{obj.__qualname__}"
    if isinstance(obj, partial):
        return get_func_qualname(obj.func)
    return f"{obj.__module__}.{get_class_name(obj)}"


##


def identity[T](obj: T, /) -> T:
    """Return the object itself."""
    return obj


##


def is_none(obj: Any, /) -> TypeGuard[None]:
    """Check if an object is `None`."""
    return obj is None


##


def is_not_none(obj: Any, /) -> bool:
    """Check if an object is not `None`."""
    return obj is not None


##


def map_object[T](
    func: Callable[[Any], Any], obj: T, /, *, before: Callable[[Any], Any] | None = None
) -> T:
    """Map a function over an object, across a variety of structures."""
    if before is not None:
        obj = before(obj)
    match obj:
        case dict():
            return type(obj)({
                k: map_object(func, v, before=before) for k, v in obj.items()
            })
        case frozenset() | list() | set() | tuple():
            return type(obj)(map_object(func, i, before=before) for i in obj)
        case Dataclass():
            return map_object(func, asdict(obj), before=before)
        case _:
            return func(obj)


##


@overload
def min_nullable[T: SupportsRichComparison](
    iterable: Iterable[T | None], /, *, default: Sentinel = ...
) -> T: ...
@overload
def min_nullable[T: SupportsRichComparison, U](
    iterable: Iterable[T | None], /, *, default: U = ...
) -> T | U: ...
def min_nullable[T: SupportsRichComparison, U](
    iterable: Iterable[T | None], /, *, default: U | Sentinel = sentinel
) -> T | U:
    """Compute the minimum of a set of values; ignoring nulls."""
    values = (i for i in iterable if i is not None)
    if is_sentinel(default):
        try:
            return min(values)
        except ValueError:
            raise MinNullableError(values=values) from None
    return min(values, default=default)


@dataclass(kw_only=True, slots=True)
class MinNullableError[T: SupportsRichComparison](Exception):
    values: Iterable[T]

    @override
    def __str__(self) -> str:
        return "Minimum of an all-None iterable is undefined"


@overload
def max_nullable[T: SupportsRichComparison](
    iterable: Iterable[T | None], /, *, default: Sentinel = ...
) -> T: ...
@overload
def max_nullable[T: SupportsRichComparison, U](
    iterable: Iterable[T | None], /, *, default: U = ...
) -> T | U: ...
def max_nullable[T: SupportsRichComparison, U](
    iterable: Iterable[T | None], /, *, default: U | Sentinel = sentinel
) -> T | U:
    """Compute the maximum of a set of values; ignoring nulls."""
    values = (i for i in iterable if i is not None)
    if is_sentinel(default):
        try:
            return max(values)
        except ValueError:
            raise MaxNullableError(values=values) from None
    return max(values, default=default)


@dataclass(kw_only=True, slots=True)
class MaxNullableError[TSupportsRichComparison](Exception):
    values: Iterable[TSupportsRichComparison]

    @override
    def __str__(self) -> str:
        return "Maximum of an all-None iterable is undefined"


##


def not_func[**P](func: Callable[P, bool], /) -> Callable[P, bool]:
    """Lift a boolean-valued function to return its conjugation."""

    @wraps(func)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> bool:
        return not func(*args, **kwargs)

    return wrapped


##


def second[U](pair: tuple[Any, U], /) -> U:
    """Get the second element in a pair."""
    return pair[1]


##


def skip_if_optimize[**P](func: Callable[P, None], /) -> Callable[P, None]:
    """Skip a function if we are in the optimized mode."""
    if __debug__:
        return func

    @wraps(func)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> None:
        _ = (args, kwargs)

    return wrapped


##


def yield_object_attributes(
    obj: Any,
    /,
    *,
    skip: Iterable[str] | None = None,
    static_type: type[Any] | None = None,
) -> Iterator[tuple[str, Any]]:
    """Yield all the object attributes."""
    skip = None if skip is None else set(skip)
    for name in dir(obj):
        if ((skip is None) or (name not in skip)) and (
            (static_type is None) or isinstance(getattr_static(obj, name), static_type)
        ):
            value = getattr(obj, name)
            yield name, value


##


def yield_object_properties(
    obj: Any, /, *, skip: Iterable[str] | None = None
) -> Iterator[tuple[str, Any]]:
    """Yield all the object properties."""
    yield from yield_object_attributes(obj, skip=skip, static_type=property)


def yield_object_cached_properties(
    obj: Any, /, *, skip: Iterable[str] | None = None
) -> Iterator[tuple[str, Any]]:
    """Yield all the object cached properties."""
    yield from yield_object_attributes(obj, skip=skip, static_type=cached_property)


##


def _make_error_msg(obj: Any, desc: str, /, *, nullable: bool = False) -> str:
    msg = f"{get_repr_and_class(obj)} must be {desc}"
    if nullable:
        msg += " or None"
    return msg


__all__ = [
    "EnsureBoolError",
    "EnsureBytesError",
    "EnsureClassError",
    "EnsureDateError",
    "EnsureFloatError",
    "EnsureIntError",
    "EnsureMemberError",
    "EnsureNotNoneError",
    "EnsureNumberError",
    "EnsurePathError",
    "EnsurePlainDateTimeError",
    "EnsureStrError",
    "EnsureTimeDeltaError",
    "EnsureTimeError",
    "EnsureZonedDateTimeError",
    "MaxNullableError",
    "MinNullableError",
    "apply_decorators",
    "ensure_bool",
    "ensure_bytes",
    "ensure_class",
    "ensure_date",
    "ensure_float",
    "ensure_int",
    "ensure_member",
    "ensure_not_none",
    "ensure_number",
    "ensure_path",
    "ensure_plain_date_time",
    "ensure_str",
    "ensure_time",
    "ensure_time_delta",
    "ensure_zoned_date_time",
    "first",
    "get_class",
    "get_class_name",
    "get_func_name",
    "get_func_qualname",
    "identity",
    "is_none",
    "is_not_none",
    "map_object",
    "max_nullable",
    "min_nullable",
    "not_func",
    "second",
    "skip_if_optimize",
    "yield_object_attributes",
    "yield_object_cached_properties",
    "yield_object_properties",
]
