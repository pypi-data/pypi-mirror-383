from __future__ import annotations

import sys
from dataclasses import dataclass
from functools import cache, cached_property, lru_cache, partial, wraps
from itertools import chain
from operator import neg
from pathlib import Path
from subprocess import check_output
from sys import executable
from types import NoneType
from typing import TYPE_CHECKING, Any, ClassVar, cast

from hypothesis import given
from hypothesis.strategies import (
    DataObject,
    booleans,
    builds,
    data,
    dictionaries,
    integers,
    lists,
    none,
    permutations,
    sampled_from,
)
from pytest import mark, param, raises

from utilities.errors import ImpossibleCaseError
from utilities.functions import (
    EnsureBoolError,
    EnsureBytesError,
    EnsureClassError,
    EnsureDateError,
    EnsureFloatError,
    EnsureIntError,
    EnsureMemberError,
    EnsureNotNoneError,
    EnsureNumberError,
    EnsurePathError,
    EnsurePlainDateTimeError,
    EnsureStrError,
    EnsureTimeDeltaError,
    EnsureTimeError,
    EnsureZonedDateTimeError,
    MaxNullableError,
    MinNullableError,
    apply_decorators,
    ensure_bool,
    ensure_bytes,
    ensure_class,
    ensure_date,
    ensure_float,
    ensure_int,
    ensure_member,
    ensure_not_none,
    ensure_number,
    ensure_path,
    ensure_plain_date_time,
    ensure_str,
    ensure_time,
    ensure_time_delta,
    ensure_zoned_date_time,
    first,
    get_class,
    get_class_name,
    get_func_name,
    get_func_qualname,
    identity,
    is_none,
    is_not_none,
    map_object,
    max_nullable,
    min_nullable,
    not_func,
    second,
    yield_object_attributes,
    yield_object_cached_properties,
    yield_object_properties,
)
from utilities.sentinel import sentinel
from utilities.text import parse_bool, strip_and_dedent
from utilities.whenever import NOW_UTC, ZERO_TIME, get_now, get_today

if TYPE_CHECKING:
    import datetime as dt
    from collections.abc import Callable, Iterable

    from whenever import PlainDateTime, TimeDelta, ZonedDateTime

    from utilities.types import Number


class TestApplyDecorators:
    @given(n=integers())
    def test_main(self, *, n: int) -> None:
        counter = 0

        def negate(x: int, /) -> int:
            return -x

        def increment[**P, T](func: Callable[P, T], /) -> Callable[P, T]:
            @wraps(func)
            def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
                nonlocal counter
                counter += 1
                return func(*args, **kwargs)

            return wrapped

        decorated = apply_decorators(negate, increment)
        assert counter == 0
        assert negate(n) == -n
        assert counter == 0
        assert decorated(n) == -n
        assert counter == 1


class TestEnsureBool:
    @given(case=sampled_from([(True, False), (True, True), (None, True)]))
    def test_main(self, *, case: tuple[bool | None, bool]) -> None:
        obj, nullable = case
        _ = ensure_bool(obj, nullable=nullable)

    @given(
        case=sampled_from([
            (False, "Object '.*' of type '.*' must be a boolean"),
            (True, "Object '.*' of type '.*' must be a boolean or None"),
        ])
    )
    def test_error(self, *, case: tuple[bool, str]) -> None:
        nullable, match = case
        with raises(EnsureBoolError, match=match):
            _ = ensure_bool(sentinel, nullable=nullable)


class TestEnsureBytes:
    @given(case=sampled_from([(b"", False), (b"", True), (None, True)]))
    def test_main(self, *, case: tuple[bytes | None, bool]) -> None:
        obj, nullable = case
        _ = ensure_bytes(obj, nullable=nullable)

    @given(
        case=sampled_from([
            (False, "Object '.*' of type '.*' must be a byte string"),
            (True, "Object '.*' of type '.*' must be a byte string or None"),
        ])
    )
    def test_error(self, *, case: tuple[bool, str]) -> None:
        nullable, match = case
        with raises(EnsureBytesError, match=match):
            _ = ensure_bytes(sentinel, nullable=nullable)


class TestEnsureClass:
    @given(
        case=sampled_from([
            (True, bool, False),
            (True, bool, True),
            (True, (bool,), False),
            (True, (bool,), True),
            (None, bool, True),
        ])
    )
    def test_main(self, *, case: tuple[Any, Any, bool]) -> None:
        obj, cls, nullable = case
        _ = ensure_class(obj, cls, nullable=nullable)

    @given(
        case=sampled_from([
            (False, "Object '.*' of type '.*' must be an instance of '.*'"),
            (True, "Object '.*' of type '.*' must be an instance of '.*' or None"),
        ])
    )
    def test_error(self, *, case: tuple[bool, str]) -> None:
        nullable, match = case
        with raises(EnsureClassError, match=match):
            _ = ensure_class(sentinel, bool, nullable=nullable)


class TestEnsureDate:
    @given(case=sampled_from([(get_today(), False), (get_today(), True), (None, True)]))
    def test_main(self, *, case: tuple[dt.date | None, bool]) -> None:
        obj, nullable = case
        _ = ensure_date(obj, nullable=nullable)

    @given(
        case=sampled_from([
            (False, "Object '.*' of type '.*' must be a date"),
            (True, "Object '.*' of type '.*' must be a date or None"),
        ])
    )
    def test_error(self, *, case: tuple[bool, str]) -> None:
        nullable, match = case
        with raises(EnsureDateError, match=match):
            _ = ensure_date(sentinel, nullable=nullable)


class TestEnsureFloat:
    @given(case=sampled_from([(0.0, False), (0.0, True), (None, True)]))
    def test_main(self, *, case: tuple[float | None, bool]) -> None:
        obj, nullable = case
        _ = ensure_float(obj, nullable=nullable)

    @given(
        case=sampled_from([
            (False, "Object '.*' of type '.*' must be a float"),
            (True, "Object '.*' of type '.*' must be a float or None"),
        ])
    )
    def test_error(self, *, case: tuple[bool, str]) -> None:
        nullable, match = case
        with raises(EnsureFloatError, match=match):
            _ = ensure_float(sentinel, nullable=nullable)


class TestEnsureInt:
    @given(case=sampled_from([(0, False), (0, True), (None, True)]))
    def test_main(self, *, case: tuple[int | None, bool]) -> None:
        obj, nullable = case
        _ = ensure_int(obj, nullable=nullable)

    @given(
        case=sampled_from([
            (False, "Object '.*' of type '.*' must be an integer"),
            (True, "Object '.*' of type '.*' must be an integer or None"),
        ])
    )
    def test_error(self, *, case: tuple[bool, str]) -> None:
        nullable, match = case
        with raises(EnsureIntError, match=match):
            _ = ensure_int(sentinel, nullable=nullable)


class TestEnsureMember:
    @given(
        case=sampled_from([
            (True, True),
            (True, False),
            (False, True),
            (False, False),
            (None, True),
        ])
    )
    def test_main(self, *, case: tuple[Any, bool]) -> None:
        obj, nullable = case
        _ = ensure_member(obj, {True, False}, nullable=nullable)

    @given(
        case=sampled_from([
            (False, "Object .* must be a member of .*"),
            (True, "Object .* must be a member of .* or None"),
        ])
    )
    def test_error(self, *, case: tuple[bool, str]) -> None:
        nullable, match = case
        with raises(EnsureMemberError, match=match):
            _ = ensure_member(sentinel, {True, False}, nullable=nullable)


class TestEnsureNotNone:
    def test_main(self) -> None:
        maybe_int = cast("int | None", 0)
        result = ensure_not_none(maybe_int)
        assert result == 0

    def test_error(self) -> None:
        with raises(EnsureNotNoneError, match=r"Object must not be None"):
            _ = ensure_not_none(None)

    def test_error_with_desc(self) -> None:
        with raises(EnsureNotNoneError, match=r"Name must not be None"):
            _ = ensure_not_none(None, desc="Name")


class TestEnsureNumber:
    @given(case=sampled_from([(0, False), (0.0, False), (0.0, True), (None, True)]))
    def test_main(self, *, case: tuple[Number, bool]) -> None:
        obj, nullable = case
        _ = ensure_number(obj, nullable=nullable)

    @given(
        case=sampled_from([
            (False, "Object '.*' of type '.*' must be a number"),
            (True, "Object '.*' of type '.*' must be a number or None"),
        ])
    )
    def test_error(self, *, case: tuple[bool, str]) -> None:
        nullable, match = case
        with raises(EnsureNumberError, match=match):
            _ = ensure_number(sentinel, nullable=nullable)


class TestEnsurePath:
    @given(case=sampled_from([(Path.home(), False), (Path.home(), True), (None, True)]))
    def test_main(self, *, case: tuple[int | None, bool]) -> None:
        obj, nullable = case
        _ = ensure_path(obj, nullable=nullable)

    @given(
        case=sampled_from([
            (False, "Object '.*' of type '.*' must be a Path"),
            (True, "Object '.*' of type '.*' must be a Path or None"),
        ])
    )
    def test_error(self, *, case: tuple[bool, str]) -> None:
        nullable, match = case
        with raises(EnsurePathError, match=match):
            _ = ensure_path(sentinel, nullable=nullable)


class TestEnsurePlainDateTime:
    @given(
        case=sampled_from([
            (NOW_UTC.to_plain(), False),
            (NOW_UTC.to_plain(), True),
            (None, True),
        ])
    )
    def test_main(self, *, case: tuple[PlainDateTime | None, bool]) -> None:
        obj, nullable = case
        _ = ensure_plain_date_time(obj, nullable=nullable)

    @given(
        case=sampled_from([
            (False, "Object '.*' of type '.*' must be a plain date-time"),
            (True, "Object '.*' of type '.*' must be a plain date-time or None"),
        ])
    )
    def test_error(self, *, case: tuple[bool, str]) -> None:
        nullable, match = case
        with raises(EnsurePlainDateTimeError, match=match):
            _ = ensure_plain_date_time(sentinel, nullable=nullable)


class TestEnsureStr:
    @given(case=sampled_from([("", False), ("", True), (None, True)]))
    def test_main(self, *, case: tuple[bool | None, bool]) -> None:
        obj, nullable = case
        _ = ensure_str(obj, nullable=nullable)

    @given(
        case=sampled_from([
            (False, "Object '.*' of type '.*' must be a string"),
            (True, "Object '.*' of type '.*' must be a string or None"),
        ])
    )
    def test_error(self, *, case: tuple[bool, str]) -> None:
        nullable, match = case
        with raises(EnsureStrError, match=match):
            _ = ensure_str(sentinel, nullable=nullable)


class TestEnsureTime:
    @given(
        case=sampled_from([
            (get_now().time(), False),
            (get_now().time(), True),
            (None, True),
        ])
    )
    def test_main(self, *, case: tuple[dt.time | None, bool]) -> None:
        obj, nullable = case
        _ = ensure_time(obj, nullable=nullable)

    @given(
        case=sampled_from([
            (False, "Object '.*' of type '.*' must be a time"),
            (True, "Object '.*' of type '.*' must be a time or None"),
        ])
    )
    def test_error(self, *, case: tuple[bool, str]) -> None:
        nullable, match = case
        with raises(EnsureTimeError, match=match):
            _ = ensure_time(sentinel, nullable=nullable)


class TestEnsureTimeDelta:
    @given(case=sampled_from([(ZERO_TIME, False), (ZERO_TIME, True), (None, True)]))
    def test_main(self, *, case: tuple[TimeDelta | None, bool]) -> None:
        obj, nullable = case
        _ = ensure_time_delta(obj, nullable=nullable)

    @given(
        case=sampled_from([
            (False, "Object '.*' of type '.*' must be a time-delta"),
            (True, "Object '.*' of type '.*' must be a time-delta or None"),
        ])
    )
    def test_error(self, *, case: tuple[bool, str]) -> None:
        nullable, match = case
        with raises(EnsureTimeDeltaError, match=match):
            _ = ensure_time_delta(sentinel, nullable=nullable)


class TestEnsureZonedDateTime:
    @given(case=sampled_from([(NOW_UTC, False), (NOW_UTC, True), (None, True)]))
    def test_main(self, *, case: tuple[ZonedDateTime | None, bool]) -> None:
        obj, nullable = case
        _ = ensure_zoned_date_time(obj, nullable=nullable)

    @given(
        case=sampled_from([
            (False, "Object '.*' of type '.*' must be a zoned date-time"),
            (True, "Object '.*' of type '.*' must be a zoned date-time or None"),
        ])
    )
    def test_error(self, *, case: tuple[bool, str]) -> None:
        nullable, match = case
        with raises(EnsureZonedDateTimeError, match=match):
            _ = ensure_zoned_date_time(sentinel, nullable=nullable)


class TestFirst:
    @given(x=integers(), y=integers())
    def test_main(self, *, x: int, y: int) -> None:
        pair = x, y
        result = first(pair)
        assert result == x


class TestGetClass:
    @given(case=sampled_from([(None, NoneType), (NoneType, NoneType)]))
    def test_main(self, *, case: tuple[Any, type[Any]]) -> None:
        obj, expected = case
        result = get_class(obj)
        assert result is expected


class TestGetClassName:
    def test_class(self) -> None:
        class Example: ...

        assert get_class_name(Example) == "Example"

    def test_instance(self) -> None:
        class Example: ...

        assert get_class_name(Example()) == "Example"

    def test_qual(self) -> None:
        assert (
            get_class_name(ImpossibleCaseError, qual=True)
            == "utilities.errors.ImpossibleCaseError"
        )


class TestGetFuncNameAndGetFuncQualName:
    @given(
        case=sampled_from([
            (identity, "identity", "utilities.functions.identity"),
            (
                lambda x: x,  # pyright: ignore[reportUnknownLambdaType]
                "<lambda>",
                "tests.test_functions.TestGetFuncNameAndGetFuncQualName.<lambda>",
            ),
            (len, "len", "builtins.len"),
            (neg, "neg", "_operator.neg"),
            (object.__init__, "object.__init__", "builtins.object.__init__"),
            (object.__str__, "object.__str__", "builtins.object.__str__"),
            (repr, "repr", "builtins.repr"),
            (str, "str", "builtins.str"),
            (str.join, "str.join", "builtins.str.join"),
            (sys.exit, "exit", "sys.exit"),
        ])
    )
    def test_main(self, *, case: tuple[Callable[..., Any], str, str]) -> None:
        func, exp_name, exp_qual_name = case
        assert get_func_name(func) == exp_name
        assert get_func_qualname(func) == exp_qual_name

    def test_cache(self) -> None:
        @cache
        def cache_func(x: int, /) -> int:
            return x

        assert get_func_name(cache_func) == "cache_func"
        assert (
            get_func_qualname(cache_func)
            == "tests.test_functions.TestGetFuncNameAndGetFuncQualName.test_cache.<locals>.cache_func"
        )

    def test_decorated(self) -> None:
        @wraps(identity)
        def wrapped[T](x: T, /) -> T:
            return identity(x)

        assert get_func_name(wrapped) == "identity"
        assert get_func_qualname(wrapped) == "utilities.functions.identity"

    def test_lru_cache(self) -> None:
        @lru_cache
        def lru_cache_func(x: int, /) -> int:
            return x

        assert get_func_name(lru_cache_func) == "lru_cache_func"
        assert (
            get_func_qualname(lru_cache_func)
            == "tests.test_functions.TestGetFuncNameAndGetFuncQualName.test_lru_cache.<locals>.lru_cache_func"
        )

    def test_object(self) -> None:
        class Example:
            def __call__[T](self, x: T, /) -> T:
                return identity(x)

        obj = Example()
        assert get_func_name(obj) == "Example"
        assert get_func_qualname(obj) == "tests.test_functions.Example"

    def test_obj_method(self) -> None:
        class Example:
            def obj_method[T](self, x: T) -> T:
                return identity(x)

        obj = Example()
        assert get_func_name(obj.obj_method) == "Example.obj_method"
        assert (
            get_func_qualname(obj.obj_method)
            == "tests.test_functions.TestGetFuncNameAndGetFuncQualName.test_obj_method.<locals>.Example.obj_method"
        )

    def test_obj_classmethod(self) -> None:
        class Example:
            @classmethod
            def obj_classmethod[T](cls: T) -> T:
                return identity(cls)

        assert get_func_name(Example.obj_classmethod) == "Example.obj_classmethod"
        assert (
            get_func_qualname(Example.obj_classmethod)
            == "tests.test_functions.TestGetFuncNameAndGetFuncQualName.test_obj_classmethod.<locals>.Example.obj_classmethod"
        )

    def test_obj_staticmethod(self) -> None:
        class Example:
            @staticmethod
            def obj_staticmethod[T](x: T) -> T:
                return identity(x)

        assert get_func_name(Example.obj_staticmethod) == "Example.obj_staticmethod"
        assert (
            get_func_qualname(Example.obj_staticmethod)
            == "tests.test_functions.TestGetFuncNameAndGetFuncQualName.test_obj_staticmethod.<locals>.Example.obj_staticmethod"
        )

    def test_partial(self) -> None:
        part = partial(identity)
        assert get_func_name(part) == "identity"
        assert get_func_qualname(part) == "utilities.functions.identity"


class TestIdentity:
    @given(x=integers())
    def test_main(self, *, x: int) -> None:
        assert identity(x) == x


class TestIsNoneAndIsNotNone:
    @given(
        case=sampled_from([
            (is_none, None, True),
            (is_none, 0, False),
            (is_not_none, None, False),
            (is_not_none, 0, True),
        ])
    )
    def test_main(self, *, case: tuple[Callable[[Any], bool], Any, bool]) -> None:
        func, obj, expected = case
        result = func(obj)
        assert result is expected


class TestMapObject:
    @given(x=integers())
    def test_int(self, *, x: int) -> None:
        result = map_object(neg, x)
        expected = -x
        assert result == expected

    @given(x=dictionaries(integers(), integers()))
    def test_dict(self, *, x: dict[int, int]) -> None:
        result = map_object(neg, x)
        expected = {k: -v for k, v in x.items()}
        assert result == expected

    @given(x=lists(integers()))
    def test_sequences(self, *, x: list[int]) -> None:
        result = map_object(neg, x)
        expected = list(map(neg, x))
        assert result == expected

    @given(data=data())
    def test_dataclasses(self, *, data: DataObject) -> None:
        @dataclass(kw_only=True, slots=True)
        class Example:
            x: int = 0

        obj = data.draw(builds(Example))
        result = map_object(neg, obj)
        expected = {"x": -obj.x}
        assert result == expected

    @given(x=lists(dictionaries(integers(), integers())))
    def test_nested(self, *, x: list[dict[int, int]]) -> None:
        result = map_object(neg, x)
        expected = [{k: -v for k, v in x_i.items()} for x_i in x]
        assert result == expected

    @given(x=lists(integers()))
    def test_before(self, *, x: list[int]) -> None:
        def before(x: Any, /) -> Any:
            return x + 1 if isinstance(x, int) else x

        result = map_object(neg, x, before=before)
        expected = [-(i + 1) for i in x]
        assert result == expected


class TestMinMaxNullable:
    @given(
        data=data(),
        values=lists(integers(), min_size=1),
        nones=lists(none()),
        case=sampled_from([(min_nullable, min), (max_nullable, max)]),
    )
    def test_main(
        self,
        *,
        data: DataObject,
        values: list[int],
        nones: list[None],
        case: tuple[
            Callable[[Iterable[int | None]], int], Callable[[Iterable[int]], int]
        ],
    ) -> None:
        func_nullable, func_builtin = case
        values_use = data.draw(permutations(list(chain(values, nones))))
        result = func_nullable(values_use)
        expected = func_builtin(values)
        assert result == expected

    @given(
        nones=lists(none()),
        value=integers(),
        func=sampled_from([min_nullable, max_nullable]),
    )
    def test_default(
        self, *, nones: list[None], value: int, func: Callable[..., int]
    ) -> None:
        result = func(nones, default=value)
        assert result == value

    @given(nones=lists(none()))
    def test_error_min_nullable(self, *, nones: list[None]) -> None:
        with raises(
            MinNullableError, match=r"Minimum of an all-None iterable is undefined"
        ):
            _ = min_nullable(nones)

    @given(nones=lists(none()))
    def test_error_max_nullable(self, *, nones: list[None]) -> None:
        with raises(
            MaxNullableError, match=r"Maximum of an all-None iterable is undefined"
        ):
            max_nullable(nones)


class TestNotFunc:
    @given(x=booleans())
    def test_main(self, *, x: bool) -> None:
        def return_x() -> bool:
            return x

        return_not_x = not_func(return_x)
        result = return_not_x()
        expected = not x
        assert result is expected


class TestSecond:
    @given(x=integers(), y=integers())
    def test_main(self, *, x: int, y: int) -> None:
        pair = x, y
        assert second(pair) == y


class TestSkipIfOptimize:
    @mark.parametrize("optimize", [param(True), param(False)])
    def test_main(self, *, optimize: bool) -> None:
        code = strip_and_dedent("""
            from utilities.functions import skip_if_optimize

            is_run = False

            @skip_if_optimize
            def func() -> None:
                global is_run
                is_run = True

            func()
            print(is_run)
        """)

        args = [executable]
        if optimize:
            args.append("-O")
        args.extend(["-c", code])
        is_run = parse_bool(check_output(args, text=True))
        assert is_run is not optimize


class TestYieldObjectAttributes:
    @given(n=integers())
    def test_main(self, *, n: int) -> None:
        class Example:
            attr: ClassVar[int] = n

        attrs = dict(yield_object_attributes(Example))
        assert len(attrs) == 29
        assert attrs["attr"] == n


class TestYieldObjectCachedProperties:
    @given(cprop=integers(), prop=integers())
    def test_main(self, *, cprop: int, prop: int) -> None:
        class Example:
            @cached_property
            def cprop(self) -> int:
                return cprop

            @property
            def prop(self) -> int:
                return prop

        obj = Example()
        cprops = dict(yield_object_cached_properties(obj))
        expected = {"cprop": cprop}
        assert cprops == expected

    @given(cprop=integers())
    def test_skip(self, *, cprop: int) -> None:
        @dataclass(kw_only=True)
        class Example:
            def __post_init__(self) -> None:
                _ = self._cached_properties

            @cached_property
            def cprop(self) -> int:
                return cprop

            @cached_property
            def _cached_properties(self) -> list[tuple[str, Any]]:
                return list(
                    yield_object_cached_properties(self, skip={"_cached_properties"})
                )

        obj = Example()
        assert obj._cached_properties == [("cprop", cprop)]
        assert obj.cprop == cprop


class TestYieldObjectProperties:
    @given(cprop=integers(), prop=integers())
    def test_main(self, *, cprop: int, prop: int) -> None:
        class Example:
            @cached_property
            def cprop(self) -> int:
                return cprop

            @property
            def prop(self) -> int:
                return prop

        obj = Example()
        props = dict(yield_object_properties(obj))
        expected = {"prop": prop}
        assert props == expected
