from __future__ import annotations

from collections.abc import Iterable
from io import StringIO
from logging import DEBUG, WARNING, FileHandler, StreamHandler, getLogger
from math import inf, isnan, nan
from pathlib import Path
from re import search
from typing import TYPE_CHECKING, Any

from hypothesis import assume, given
from hypothesis.strategies import (
    booleans,
    builds,
    dictionaries,
    integers,
    lists,
    none,
    sampled_from,
    sets,
    tuples,
)
from polars import Object, String, UInt64
from pytest import approx, mark, param, raises
from whenever import ZonedDateTime

from tests.conftest import SKIPIF_CI_AND_WINDOWS
from tests.test_objects.objects import (
    CustomError,
    SubFrozenSet,
    SubList,
    SubSet,
    SubTuple,
    TruthEnum,
    objects,
)
from tests.test_typing_funcs.with_future import (
    DataClassFutureCustomEquality,
    DataClassFutureDefaultInInitChild,
    DataClassFutureDefaultInInitParent,
    DataClassFutureInt,
    DataClassFutureIntDefault,
    DataClassFutureLiteral,
    DataClassFutureLiteralNullable,
    DataClassFutureNestedInnerFirstInner,
    DataClassFutureNestedInnerFirstOuter,
    DataClassFutureNestedOuterFirstInner,
    DataClassFutureNestedOuterFirstOuter,
    DataClassFutureNone,
    DataClassFutureTypeLiteral,
    DataClassFutureTypeLiteralNullable,
)
from utilities.hypothesis import (
    date_periods,
    dates,
    int64s,
    paths,
    temp_paths,
    text_ascii,
    text_printable,
    time_periods,
    zoned_date_time_periods,
    zoned_date_times,
)
from utilities.iterables import always_iterable, one
from utilities.logging import get_logging_level_number
from utilities.math import MAX_INT64, MIN_INT64
from utilities.operator import is_equal
from utilities.orjson import (
    _LOG_RECORD_DEFAULT_ATTRS,
    OrjsonFormatter,
    OrjsonLogRecord,
    Unserializable,
    _DeserializeInvalidJSONError,
    _DeserializeNoObjectsError,
    _DeserializeObjectNotFoundError,
    _object_hook_get_object,
    _SerializeIntegerError,
    deserialize,
    get_log_records,
    read_object,
    serialize,
    write_object,
)
from utilities.polars import check_polars_dataframe, zoned_date_time_dtype
from utilities.sentinel import Sentinel, sentinel
from utilities.types import LogLevel, MaybeIterable, PathLike
from utilities.typing import get_args, is_sequence_of
from utilities.tzlocal import LOCAL_TIME_ZONE
from utilities.whenever import (
    HOUR,
    MINUTE,
    SECOND,
    DatePeriod,
    TimePeriod,
    ZonedDateTimePeriod,
    get_now,
)
from utilities.zoneinfo import UTC

if TYPE_CHECKING:
    from collections.abc import Sequence

    from whenever import Date

    from utilities.types import Dataclass, StrMapping


# formatter


class TestGetLogRecords:
    def test_main(self, *, tmp_path: Path) -> None:
        logger = getLogger(str(tmp_path))
        logger.addHandler(handler := FileHandler(file := tmp_path.joinpath("log")))
        handler.setFormatter(OrjsonFormatter())
        logger.warning("", extra={"a": 1, "b": 2, "_ignored": 3})
        output = get_log_records(tmp_path, parallelism="threads")
        assert output.path == tmp_path
        assert output.files == [file]
        assert output.num_files == 1
        assert output.num_files_ok == 1
        assert output.num_files_error == 0
        assert output.num_lines == 1
        assert output.num_lines_ok == 1
        assert output.num_lines_blank == 0
        assert output.num_lines_error == 0
        assert len(output.records) == 1
        assert output.missing == set()
        assert output.other_errors == []
        # properties
        assert output.frac_files_ok == 1.0
        assert output.frac_files_error == 0.0
        assert output.frac_lines_ok == 1.0
        assert output.frac_lines_blank == 0.0
        assert output.frac_lines_error == 0.0

        # record
        record = one(output.records)
        assert record.name == str(tmp_path)
        assert record.message == ""
        assert record.level == WARNING
        assert record.line_num == approx(118, rel=0.1)
        assert abs(record.datetime - get_now()) <= MINUTE
        assert record.func_name == "test_main"
        assert record.stack_info is None
        assert record.extra is not None
        assert record.extra["a"] == 1
        assert record.extra["b"] == 2
        assert record.log_file == file
        assert record.log_file_line_num == 1

        # magic methods
        assert isinstance(output[0], OrjsonLogRecord)
        assert is_sequence_of(output[:], OrjsonLogRecord)
        assert len(output) == 1

    @given(
        items=lists(
            tuples(
                sampled_from(get_args(LogLevel)),
                text_ascii(),
                dictionaries(text_ascii(), int64s()),
            )
        ),
        root=temp_paths(),
    )
    def test_dataframe(
        self, *, root: Path, items: Sequence[tuple[LogLevel, str, StrMapping]]
    ) -> None:
        logger = getLogger(str(root))
        logger.addHandler(handler := FileHandler(root.joinpath("log")))
        logger.setLevel(DEBUG)
        handler.setFormatter(OrjsonFormatter())
        for level_, message_, extra_ in items:
            _ = assume(set(extra_) & set(_LOG_RECORD_DEFAULT_ATTRS) == set())
            logger.log(get_logging_level_number(level_), message_, extra=extra_)
        output = get_log_records(root, parallelism="threads")
        check_polars_dataframe(
            output.dataframe,
            height=len(items),
            schema_list={
                "index": UInt64,
                "name": String,
                "message": String,
                "level": UInt64,
                "path_name": String,
                "line_num": UInt64,
                "datetime": zoned_date_time_dtype(time_zone=LOCAL_TIME_ZONE),
                "func_name": String,
                "stack_info": String,
                "extra": Object,
                "log_file": String,
                "log_file_line_num": UInt64,
            },
        )

    @given(
        items=lists(
            tuples(
                sampled_from(get_args(LogLevel)),
                text_ascii(),
                dictionaries(text_ascii(), int64s()),
            )
        ),
        root=temp_paths(),
        index=integers() | none(),
        min_index=integers() | none(),
        max_index=integers() | none(),
        name=text_ascii() | none(),
        message=text_ascii() | none(),
        level=sampled_from(get_args(LogLevel)) | none(),
        min_level=sampled_from(get_args(LogLevel)) | none(),
        max_level=sampled_from(get_args(LogLevel)) | none(),
        date=dates() | none(),
        min_date=dates() | none(),
        max_date=dates() | none(),
        datetime=zoned_date_times() | none(),
        min_datetime=zoned_date_times() | none(),
        max_datetime=zoned_date_times() | none(),
        func_name=booleans() | text_ascii() | none(),
        extra=booleans() | text_ascii() | sets(text_ascii()) | none(),
        log_file=booleans() | paths() | text_ascii() | none(),
        log_file_line_num=booleans() | integers() | none(),
        min_log_file_line_num=integers() | none(),
        max_log_file_line_num=integers() | none(),
    )
    def test_filter(
        self,
        *,
        root: Path,
        items: Sequence[tuple[LogLevel, str, StrMapping]],
        index: int | None,
        min_index: int | None,
        max_index: int | None,
        name: str | None,
        message: str | None,
        level: LogLevel | None,
        min_level: LogLevel | None,
        max_level: LogLevel | None,
        date: Date | None,
        min_date: Date | None,
        max_date: Date | None,
        datetime: ZonedDateTime | None,
        min_datetime: ZonedDateTime | None,
        max_datetime: ZonedDateTime | None,
        func_name: bool | str | None,
        extra: bool | MaybeIterable[str] | None,
        log_file: bool | PathLike | None,
        log_file_line_num: bool | int | None,
        min_log_file_line_num: int | None,
        max_log_file_line_num: int | None,
    ) -> None:
        logger = getLogger(str(root))
        logger.addHandler(handler := FileHandler(root.joinpath("log")))
        logger.setLevel(DEBUG)
        handler.setFormatter(OrjsonFormatter())
        for level_, message_, extra_ in items:
            _ = assume(set(extra_) & set(_LOG_RECORD_DEFAULT_ATTRS) == set())
            logger.log(get_logging_level_number(level_), "%s", message_, extra=extra_)
        output = get_log_records(root, parallelism="threads")
        output = output.filter(
            index=index,
            min_index=min_index,
            max_index=max_index,
            name=name,
            message=message,
            level=level,
            min_level=min_level,
            max_level=max_level,
            date=date,
            min_date=min_date,
            max_date=max_date,
            datetime=datetime,
            min_datetime=min_datetime,
            max_datetime=max_datetime,
            func_name=func_name,
            extra=extra,
            log_file=log_file,
            log_file_line_num=log_file_line_num,
            min_log_file_line_num=min_log_file_line_num,
            max_log_file_line_num=max_log_file_line_num,
        )
        records = output.records
        if index is not None:
            assert all(r.index == index for r in records)
        if min_index is not None:
            assert all(r.index >= min_index for r in records)
        if max_index is not None:
            assert all(r.index <= max_index for r in records)
        if name is not None:
            assert all(search(name, r.name) for r in records)
        if message is not None:
            assert all(search(message, r.message) for r in records)
        if level is not None:
            assert all(r.level == get_logging_level_number(level) for r in records)
        if min_level is not None:
            assert all(r.level >= get_logging_level_number(min_level) for r in records)
        if max_level is not None:
            assert all(r.level <= get_logging_level_number(max_level) for r in records)
        if date is not None:
            assert all(r.date == date for r in records)
        if min_date is not None:
            assert all(r.date >= min_date for r in records)
        if max_date is not None:
            assert all(r.date <= max_date for r in records)
        if datetime is not None:
            assert all(r.datetime == datetime for r in records)
        if min_datetime is not None:
            assert all(r.datetime >= min_datetime for r in records)
        if max_datetime is not None:
            assert all(r.datetime <= max_datetime for r in records)
        if func_name is not None:
            match func_name:
                case bool() as has_func_name:
                    assert all(
                        (r.func_name is not None) is has_func_name for r in records
                    )
                case str():
                    assert all(
                        (r.func_name is not None) and search(func_name, r.func_name)
                        for r in records
                    )
        if extra is not None:
            match extra:
                case bool() as has_extra:
                    assert all((r.extra is not None) is has_extra for r in records)
                case str() | Iterable() as keys:
                    assert all(
                        (r.extra is not None)
                        and set(r.extra).issuperset(always_iterable(keys))
                        for r in records
                    )
        if log_file is not None:
            match log_file:
                case bool() as has_log_file:
                    assert all(
                        (r.log_file is not None) is has_log_file for r in records
                    )
                case Path() | str():
                    assert all(
                        (r.log_file is not None)
                        and search(str(log_file), str(r.log_file))
                        for r in records
                    )
        if log_file_line_num is not None:
            match log_file_line_num:
                case bool() as has_log_file_line_num:
                    assert all(
                        (r.log_file_line_num is not None) is has_log_file_line_num
                        for r in records
                    )
                case int():
                    assert all(
                        r.log_file_line_num == log_file_line_num for r in records
                    )
        if min_log_file_line_num is not None:
            assert all(
                (r.log_file_line_num is not None)
                and (r.log_file_line_num >= min_log_file_line_num)
                for r in records
            )
        if max_log_file_line_num is not None:
            assert all(
                (r.log_file_line_num is not None)
                and (r.log_file_line_num <= max_log_file_line_num)
                for r in records
            )

    def test_skip_blank_lines(self, *, tmp_path: Path) -> None:
        logger = getLogger(str(tmp_path))
        logger.addHandler(handler := FileHandler(file := tmp_path.joinpath("log")))
        handler.setFormatter(OrjsonFormatter())
        _ = file.write_text("\n")
        logger.warning("", extra={"a": 1, "b": 2, "_ignored": 3})
        result = get_log_records(tmp_path, parallelism="threads")
        assert result.path == tmp_path
        assert result.num_lines == 2
        assert result.num_lines_ok == 1
        assert result.num_lines_blank == 1
        assert result.num_lines_error == 0

    def test_skip_dir(self, *, tmp_path: Path) -> None:
        tmp_path.joinpath("dir").mkdir()
        result = get_log_records(tmp_path, parallelism="threads")
        assert result.path == tmp_path
        assert result.num_files == 0
        assert result.num_files_ok == 0
        assert result.num_files_error == 0
        assert len(result.other_errors) == 0

    @SKIPIF_CI_AND_WINDOWS
    def test_error_file(self, *, tmp_path: Path) -> None:
        file = tmp_path.joinpath("log")
        _ = file.write_bytes(b"\x80")
        result = get_log_records(tmp_path, parallelism="threads")
        assert result.path == tmp_path
        assert result.files == [file]
        assert result.num_files == 1
        assert result.num_files_ok == 0
        assert result.num_files_error == 1
        assert len(result.other_errors) == 1
        assert isinstance(one(result.other_errors), UnicodeDecodeError)

    def test_error_deserialize_due_to_missing(self, *, tmp_path: Path) -> None:
        logger = getLogger(str(tmp_path))
        logger.addHandler(handler := FileHandler(file := tmp_path.joinpath("log")))
        handler.setFormatter(OrjsonFormatter())
        logger.warning("", extra={"obj": DataClassFutureIntDefault()})
        result = get_log_records(tmp_path, parallelism="threads")
        assert result.path == tmp_path
        assert result.files == [file]
        assert result.num_lines == 1
        assert result.num_lines_ok == 0
        assert result.num_lines_error == 1
        assert result.missing == {DataClassFutureIntDefault.__qualname__}
        assert result.other_errors == []

    def test_error_deserialize_due_to_decode(self, *, tmp_path: Path) -> None:
        file = tmp_path.joinpath("log")
        _ = file.write_text("message")
        result = get_log_records(tmp_path, parallelism="threads")
        assert result.path == tmp_path
        assert result.files == [file]
        assert result.num_lines == 1
        assert result.num_lines_ok == 0
        assert result.num_lines_error == 1
        assert result.missing == set()
        assert len(result.other_errors) == 1
        assert isinstance(one(result.other_errors), _DeserializeInvalidJSONError)


class TestOrjsonFormatter:
    def test_main(self, *, tmp_path: Path) -> None:
        logger = getLogger(str(tmp_path))
        logger.addHandler(handler := StreamHandler(buffer := StringIO()))
        handler.setFormatter(OrjsonFormatter())
        logger.warning("message", extra={"a": 1, "b": 2, "_ignored": 3})
        record = deserialize(buffer.getvalue().encode(), objects={OrjsonLogRecord})
        assert isinstance(record, OrjsonLogRecord)
        assert record.name == str(tmp_path)
        assert record.message == "message"
        assert record.level == WARNING
        assert record.path_name == Path(__file__)
        assert abs(record.datetime - get_now()) <= SECOND
        assert record.func_name == TestOrjsonFormatter.test_main.__name__
        assert record.stack_info is None
        assert record.extra is not None
        assert record.extra["a"] == 1
        assert record.extra["b"] == 2


# serialize/deserialize


class TestSerializeAndDeserialize:
    @given(obj=objects(all_=True, parsable=True))
    def test_all(self, *, obj: Any) -> None:
        ser = serialize(obj, globalns=globals())
        result = deserialize(
            ser,
            objects={
                CustomError,
                DataClassFutureCustomEquality,
                DataClassFutureInt,
                DataClassFutureIntDefault,
                DataClassFutureLiteral,
                DataClassFutureLiteralNullable,
                DataClassFutureNestedInnerFirstInner,
                DataClassFutureNestedInnerFirstOuter,
                DataClassFutureNestedOuterFirstInner,
                DataClassFutureNestedOuterFirstOuter,
                DataClassFutureNone,
                DataClassFutureTypeLiteral,
                DataClassFutureTypeLiteralNullable,
                SubFrozenSet,
                SubList,
                SubSet,
                SubTuple,
                TruthEnum,
            },
        )
        assert is_equal(result, obj)

    @given(obj=objects(parsable=True))
    def test_base(self, *, obj: Any) -> None:
        result = deserialize(serialize(obj))
        assert is_equal(result, obj)

    @given(obj=objects(dataclass_custom_equality=True, parsable=True))
    def test_dataclass_custom_equality(self, *, obj: Any) -> None:
        result = deserialize(serialize(obj), objects={DataClassFutureCustomEquality})
        assert is_equal(result, obj)

    @given(obj=objects(dataclass_default_in_init_child=True, parsable=True))
    def test_dataclass_default_in_init_child_hook_in_serialize(
        self, *, obj: Any
    ) -> None:
        def hook(cls: type[Dataclass], mapping: StrMapping, /) -> StrMapping:
            if issubclass(cls, DataClassFutureDefaultInInitParent):
                mapping = {k: v for k, v in mapping.items() if k != "int_"}
            return mapping

        result = deserialize(
            serialize(obj, dataclass_hook=hook),
            objects={DataClassFutureDefaultInInitChild},
        )
        assert is_equal(result, obj)

    @given(obj=objects(dataclass_default_in_init_child=True, parsable=True))
    def test_dataclass_default_in_init_child_hook_in_deserialize(
        self, *, obj: Any
    ) -> None:
        def hook(cls: type[Dataclass], mapping: StrMapping, /) -> StrMapping:
            if issubclass(cls, DataClassFutureDefaultInInitParent):
                mapping = {k: v for k, v in mapping.items() if k != "int_"}
            return mapping

        result = deserialize(
            serialize(obj),
            dataclass_hook=hook,
            objects={DataClassFutureDefaultInInitChild},
        )
        assert is_equal(result, obj)

    @given(obj=objects(dataclass_int=True, parsable=True))
    def test_dataclass_int(self, *, obj: Any) -> None:
        result = deserialize(serialize(obj), objects={DataClassFutureInt})
        assert is_equal(result, obj)

    @given(obj=objects(dataclass_int_default=True, parsable=True))
    def test_dataclass_int_default(self, *, obj: Any) -> None:
        result = deserialize(serialize(obj), objects={DataClassFutureIntDefault})
        assert is_equal(result, obj)

    @given(obj=objects(dataclass_literal=True, parsable=True))
    def test_dataclass_literal(self, *, obj: Any) -> None:
        result = deserialize(serialize(obj), objects={DataClassFutureLiteral})
        assert is_equal(result, obj)

    @given(obj=objects(dataclass_literal_nullable=True, parsable=True))
    def test_dataclass_literal_nullable(self, *, obj: Any) -> None:
        result = deserialize(serialize(obj), objects={DataClassFutureLiteralNullable})
        assert is_equal(result, obj)

    @given(obj=objects(dataclass_nested=True, parsable=True))
    def test_dataclass_nested(self, *, obj: Any) -> None:
        ser = serialize(obj, globalns=globals())
        result = deserialize(
            ser,
            objects={
                DataClassFutureNestedInnerFirstInner,
                DataClassFutureNestedInnerFirstOuter,
                DataClassFutureNestedOuterFirstInner,
                DataClassFutureNestedOuterFirstOuter,
            },
        )
        assert is_equal(result, obj)

    @given(obj=objects(dataclass_none=True, parsable=True))
    def test_dataclass_none(self, *, obj: Any) -> None:
        ser = serialize(obj, globalns=globals())
        result = deserialize(ser, objects={DataClassFutureNone})
        assert is_equal(result, obj)

    @given(obj=objects(dataclass_type_literal=True, parsable=True))
    def test_dataclass_type_literal(self, *, obj: Any) -> None:
        result = deserialize(serialize(obj), objects={DataClassFutureTypeLiteral})
        assert is_equal(result, obj)

    @given(obj=objects(dataclass_type_literal_nullable=True, parsable=True))
    def test_dataclass_type_literal_nullable(self, *, obj: Any) -> None:
        result = deserialize(
            serialize(obj), objects={DataClassFutureTypeLiteralNullable}
        )
        assert is_equal(result, obj)

    @given(obj=builds(DataClassFutureNone))
    def test_dataclass_no_objects_error(self, *, obj: DataClassFutureNone) -> None:
        ser = serialize(obj)
        with raises(
            _DeserializeNoObjectsError,
            match=r"Objects required to deserialize '.*' from .*",
        ):
            _ = deserialize(ser)

    @given(obj=builds(DataClassFutureNone))
    def test_dataclass_empty_error(self, *, obj: DataClassFutureNone) -> None:
        ser = serialize(obj)
        with raises(
            _DeserializeObjectNotFoundError,
            match=r"Unable to find object to deserialize '.*' from .*",
        ):
            _ = deserialize(ser, objects=set())

    @given(period=date_periods())
    def test_date_periods(self, *, period: DatePeriod) -> None:
        result = deserialize(serialize(period))
        assert result == period

    def test_deserialize_hook(self) -> None:
        obj = DataClassFutureDefaultInInitChild()
        ser = serialize(obj)
        with raises(TypeError, match=r"got an unexpected keyword argument 'int_'"):
            _ = deserialize(ser, objects={DataClassFutureDefaultInInitChild})

        def hook(cls: type[Dataclass], mapping: StrMapping, /) -> StrMapping:
            if issubclass(cls, DataClassFutureDefaultInInitParent):
                mapping = {k: v for k, v in mapping.items() if k != "int_"}
            return mapping

        result = deserialize(
            ser, dataclass_hook=hook, objects={DataClassFutureDefaultInInitChild}
        )
        assert result == obj

    @given(obj=objects(enum=True, parsable=True))
    def test_enum(self, *, obj: Any) -> None:
        result = deserialize(serialize(obj), objects={TruthEnum})
        assert is_equal(result, obj)

    @given(obj=objects(exception_class=True, parsable=True))
    def test_exception_class(self, *, obj: Any) -> None:
        result = deserialize(serialize(obj), objects={CustomError})
        assert is_equal(result, obj)

    @given(obj=objects(exception_instance=True, parsable=True))
    def test_exception_instance(self, *, obj: Any) -> None:
        result = deserialize(serialize(obj), objects={CustomError})
        assert is_equal(result, obj)

    @mark.parametrize("value", [param(inf), param(-inf)])
    def test_inf(self, *, value: float) -> None:
        result = deserialize(serialize(value))
        assert result == value

    def test_nan(self) -> None:
        result = deserialize(serialize(nan))
        assert isnan(result)

    def test_none(self) -> None:
        result = deserialize(serialize(None))
        assert result is None

    @given(obj=objects(sub_frozenset=True, parsable=True))
    def test_sub_frozenset(self, *, obj: Any) -> None:
        result = deserialize(serialize(obj), objects={SubFrozenSet})
        assert is_equal(result, obj)

    @given(obj=objects(sub_list=True, parsable=True))
    def test_sub_list(self, *, obj: Any) -> None:
        result = deserialize(serialize(obj), objects={SubList})
        assert is_equal(result, obj)

    @given(obj=objects(sub_set=True, parsable=True))
    def test_sub_set(self, *, obj: Any) -> None:
        result = deserialize(serialize(obj), objects={SubSet})
        assert is_equal(result, obj)

    @given(obj=objects(sub_tuple=True, parsable=True))
    def test_sub_tuple(self, *, obj: Any) -> None:
        result = deserialize(serialize(obj), objects={SubTuple})
        assert is_equal(result, obj)

    @given(period=time_periods())
    def test_time_periods(self, *, period: TimePeriod) -> None:
        result = deserialize(serialize(period))
        assert result == period

    def test_unserializable(self) -> None:
        ser = serialize(sentinel)
        exp_ser = b'{"[dc|Unserializable]":{"qualname":"Sentinel","repr":"<sentinel>","str":"<sentinel>"}}'
        assert ser == exp_ser
        result = deserialize(ser)
        exp_res = Unserializable(
            qualname="Sentinel", repr="<sentinel>", str="<sentinel>"
        )
        assert result == exp_res

    @given(period=zoned_date_time_periods())
    def test_zoned_date_time_period(self, *, period: ZonedDateTimePeriod) -> None:
        result = deserialize(serialize(period))
        assert result == period


class TestSerialize:
    @given(text=text_printable())
    def test_before(self, *, text: str) -> None:
        result = serialize(text, before=str.upper)
        expected = serialize(text.upper())
        assert result == expected

    def test_dataclass(self) -> None:
        obj = DataClassFutureNone(none=None)
        result = serialize(obj)
        expected = b'{"[dc|DataClassFutureNone]":{"none":"[0]"}}'
        assert result == expected

    def test_dataclass_nested(self) -> None:
        obj = DataClassFutureNestedOuterFirstOuter(
            inner=DataClassFutureNestedOuterFirstInner(int_=0)
        )
        result = serialize(obj, globalns=globals())
        expected = b'{"[dc|DataClassFutureNestedOuterFirstOuter]":{"inner":{"[dc|DataClassFutureNestedOuterFirstInner]":{"int_":0}}}}'
        assert result == expected

    def test_dataclass_hook_main(self) -> None:
        obj = DataClassFutureDefaultInInitChild()

        def hook(cls: type[Dataclass], mapping: StrMapping, /) -> StrMapping:
            if issubclass(cls, DataClassFutureDefaultInInitParent):
                mapping = {k: v for k, v in mapping.items() if k != "int_"}
            return mapping

        result = serialize(obj, dataclass_hook=hook)
        expected = b'{"[dc|DataClassFutureDefaultInInitChild]":{}}'
        assert result == expected

    def test_enum(self) -> None:
        result = serialize(TruthEnum.true)
        expected = b'{"[e|TruthEnum]":1}'
        assert result == expected

    def test_exception_class(self) -> None:
        class CustomError(Exception): ...

        result = serialize(CustomError)
        expected = b'"[Ex|TestSerialize.test_exception_class.<locals>.CustomError]"'
        assert result == expected

    def test_exception_instance(self) -> None:
        class CustomError(Exception): ...

        result = serialize(CustomError(1, 2, 3))
        expected = b'{"[ex|TestSerialize.test_exception_instance.<locals>.CustomError]":{"[tu]":[1,2,3]}}'
        assert result == expected

    def test_none(self) -> None:
        result = serialize(None)
        expected = b'"[0]"'
        assert result == expected

    @given(x=sampled_from([MIN_INT64 - 1, MAX_INT64 + 1]))
    def test_pre_process(self, *, x: int) -> None:
        with raises(_SerializeIntegerError, match=r"Integer .* is out of range"):
            _ = serialize(x)

    def test_zoned_date_time_period(self) -> None:
        start = ZonedDateTime(2000, 1, 2, 12, 34, 45, tz=UTC.key)
        result = serialize(ZonedDateTimePeriod(start, start + HOUR))
        expected = b'"[zp]2000-01-02T12:34:45,2000-01-02T13:34:45+00:00[UTC]"'
        assert result == expected


class TestDeserialize:
    def test_error_invalid_json(self) -> None:
        with raises(
            _DeserializeInvalidJSONError, match=r"Invalid JSON: b'invalid json'"
        ):
            _ = deserialize(b"invalid json")


class TestObjectHookGetObject:
    def test_main(self) -> None:
        result = _object_hook_get_object(Sentinel.__qualname__, objects={Sentinel})
        assert result is Sentinel

    def test_redirect(self) -> None:
        qualname = f"old_{Sentinel.__qualname__}"
        result = _object_hook_get_object(qualname, redirects={qualname: Sentinel})
        assert result is Sentinel

    def test_unserializable(self) -> None:
        result = _object_hook_get_object(Unserializable.__qualname__)
        assert result is Unserializable

    def test_error_no_objects(self) -> None:
        with raises(
            _DeserializeNoObjectsError,
            match=r"Objects required to deserialize 'qualname' from .*",
        ):
            _ = _object_hook_get_object("qualname")

    def test_error_object_not_found(self) -> None:
        with raises(
            _DeserializeObjectNotFoundError,
            match=r"Unable to find object to deserialize 'qualname' from .*",
        ):
            _ = _object_hook_get_object("qualname", objects=set())


class TestReadAndWriteObject:
    @given(root=temp_paths(), obj=objects(parsable=True), compress=booleans())
    def test_main(self, *, root: Path, obj: Any, compress: bool) -> None:
        path = root.joinpath("file.json")
        write_object(obj, path, compress=compress)
        assert path.is_file()
        result = read_object(path, decompress=compress)
        assert is_equal(result, obj)
