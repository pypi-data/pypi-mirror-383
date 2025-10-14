from __future__ import annotations

from collections.abc import Collection, Iterator
from re import escape
from typing import TYPE_CHECKING, Any, ClassVar, TypeGuard

from pytest import mark, param, raises

from utilities.more_itertools import (
    BucketMappingError,
    Split,
    bucket_mapping,
    partition_list,
    partition_typeguard,
    peekable,
    yield_splits,
)
from utilities.text import strip_and_dedent

if TYPE_CHECKING:
    from collections.abc import Iterable


class TestBucketMapping:
    iterable: ClassVar[list[str]] = ["a1", "b1", "c1", "a2", "b2", "c2", "b3"]
    iterable_unique: ClassVar[list[str]] = ["a1", "b2", "c3"]

    def test_main(self) -> None:
        mapping = bucket_mapping(self.iterable, lambda x: x[0])
        assert set(mapping) == {"a", "b", "c"}
        for value in mapping.values():
            assert isinstance(value, Iterator)
            assert not isinstance(value, Collection)
        assert list(mapping["a"]) == ["a1", "a2"]
        assert list(mapping["b"]) == ["b1", "b2", "b3"]
        assert list(mapping["c"]) == ["c1", "c2"]

    def test_list(self) -> None:
        mapping = bucket_mapping(self.iterable, lambda x: x[0], post="list")
        assert set(mapping) == {"a", "b", "c"}
        for value in mapping.values():
            assert isinstance(value, list)
        assert mapping["a"] == ["a1", "a2"]
        assert mapping["b"] == ["b1", "b2", "b3"]
        assert mapping["c"] == ["c1", "c2"]

    def test_tuple(self) -> None:
        mapping = bucket_mapping(self.iterable, lambda x: x[0], post="tuple")
        assert set(mapping) == {"a", "b", "c"}
        for value in mapping.values():
            assert isinstance(value, tuple)
        assert mapping["a"] == ("a1", "a2")
        assert mapping["b"] == ("b1", "b2", "b3")
        assert mapping["c"] == ("c1", "c2")

    def test_set(self) -> None:
        mapping = bucket_mapping(self.iterable, lambda x: x[0], post="set")
        assert set(mapping) == {"a", "b", "c"}
        for value in mapping.values():
            assert isinstance(value, set)
        assert mapping["a"] == {"a1", "a2"}
        assert mapping["b"] == {"b1", "b2", "b3"}
        assert mapping["c"] == {"c1", "c2"}

    def test_frozenset(self) -> None:
        mapping = bucket_mapping(self.iterable, lambda x: x[0], post="frozenset")
        assert set(mapping) == {"a", "b", "c"}
        for value in mapping.values():
            assert isinstance(value, frozenset)
        assert mapping["a"] == frozenset({"a1", "a2"})
        assert mapping["b"] == frozenset({"b1", "b2", "b3"})
        assert mapping["c"] == frozenset({"c1", "c2"})

    def test_unique(self) -> None:
        mapping = bucket_mapping(self.iterable_unique, lambda x: x[0], post="unique")
        expected = {"a": "a1", "b": "b2", "c": "c3"}
        assert mapping == expected

    def test_pre(self) -> None:
        mapping = bucket_mapping(
            self.iterable, lambda x: x[0], pre=lambda x: int(x[-1])
        )
        assert set(mapping) == {"a", "b", "c"}
        for value in mapping.values():
            assert isinstance(value, Iterator)
            assert not isinstance(value, Collection)
        assert list(mapping["a"]) == [1, 2]
        assert list(mapping["b"]) == [1, 2, 3]
        assert list(mapping["c"]) == [1, 2]

    def test_pre_and_list(self) -> None:
        mapping = bucket_mapping(
            self.iterable, lambda x: x[0], pre=lambda x: int(x[-1]), post="list"
        )
        assert set(mapping) == {"a", "b", "c"}
        for value in mapping.values():
            assert isinstance(value, list)
        assert mapping["a"] == [1, 2]
        assert mapping["b"] == [1, 2, 3]
        assert mapping["c"] == [1, 2]

    def test_pre_and_tuple(self) -> None:
        mapping = bucket_mapping(
            self.iterable, lambda x: x[0], pre=lambda x: int(x[-1]), post="tuple"
        )
        assert set(mapping) == {"a", "b", "c"}
        for value in mapping.values():
            assert isinstance(value, tuple)
        assert mapping["a"] == (1, 2)
        assert mapping["b"] == (1, 2, 3)
        assert mapping["c"] == (1, 2)

    def test_pre_and_set(self) -> None:
        mapping = bucket_mapping(
            self.iterable, lambda x: x[0], pre=lambda x: int(x[-1]), post="set"
        )
        assert set(mapping) == {"a", "b", "c"}
        for value in mapping.values():
            assert isinstance(value, set)
        assert mapping["a"] == {1, 2}
        assert mapping["b"] == {1, 2, 3}
        assert mapping["c"] == {1, 2}

    def test_pre_and_frozenset(self) -> None:
        mapping = bucket_mapping(
            self.iterable, lambda x: x[0], pre=lambda x: int(x[-1]), post="frozenset"
        )
        assert set(mapping) == {"a", "b", "c"}
        for value in mapping.values():
            assert isinstance(value, frozenset)
        assert mapping["a"] == frozenset({1, 2})
        assert mapping["b"] == frozenset({1, 2, 3})
        assert mapping["c"] == frozenset({1, 2})

    def test_pre_and_unique(self) -> None:
        mapping = bucket_mapping(
            self.iterable_unique,
            lambda x: x[0],
            pre=lambda x: int(x[-1]),
            post="unique",
        )
        expected = {"a": 1, "b": 2, "c": 3}
        assert mapping == expected

    def test_error_unique(self) -> None:
        with raises(
            BucketMappingError,
            match=escape(
                "Buckets must contain exactly one item each; got 'a' (#1: 'a1', #2: 'a2'), 'b' (#1: 'b1', #2: 'b2'), 'c' (#1: 'c1', #2: 'c2')"
            ),
        ):
            _ = bucket_mapping(self.iterable, lambda x: x[0], post="unique")

    def test_error_pre_and_unique(self) -> None:
        with raises(
            BucketMappingError,
            match=escape(
                "Buckets must contain exactly one item each; got 'a' (#1: 1, #2: 2), 'b' (#1: 1, #2: 2), 'c' (#1: 1, #2: 2)"
            ),
        ):
            _ = bucket_mapping(
                self.iterable, lambda x: x[0], pre=lambda x: int(x[-1]), post="unique"
            )


class TestPartitionList:
    def test_main(self) -> None:
        def is_even(x: int, /) -> bool:
            return x % 2 == 0

        iterable = [1, 2, 3, 4]
        false, true = partition_list(is_even, iterable)
        assert isinstance(false, list)
        assert false == [1, 3]
        assert isinstance(true, list)
        assert true == [2, 4]


class TestPartitionTypeguard:
    def test_main(self) -> None:
        def is_int(x: Any, /) -> TypeGuard[int]:
            return isinstance(x, int)

        iterable = [1, 2.0, 3, 4.0]
        false, true = partition_typeguard(is_int, iterable)
        for el in false:
            assert isinstance(el, int | float)
        for el in true:
            assert isinstance(el, int)


class TestPeekable:
    def test_dropwhile(self) -> None:
        it = peekable(range(10))
        it.dropwhile(lambda x: x <= 4)
        assert it.peek() == 5
        result = list(it)
        expected = [5, 6, 7, 8, 9]
        assert result == expected

    def test_iter(self) -> None:
        it = peekable(range(10))
        values: list[int] = []
        for value in it:
            assert isinstance(value, int)
            values.append(value)
        assert len(values) == 10

    def test_next(self) -> None:
        it = peekable(range(10))
        value = next(it)
        assert isinstance(value, int)

    def test_peek_non_empty(self) -> None:
        it = peekable(range(10))
        value = it.peek()
        assert isinstance(value, int)

    def test_peek_empty_without_default(self) -> None:
        it: peekable[int] = peekable([])
        with raises(StopIteration):
            _ = it.peek()

    def test_peek_empty_with_default(self) -> None:
        it: peekable[int] = peekable([])
        value = it.peek(default="default")
        assert isinstance(value, str)

    def test_takewhile(self) -> None:
        it = peekable(range(10))
        result1 = list(it.takewhile(lambda x: x <= 4))
        expected1 = [0, 1, 2, 3, 4]
        assert result1 == expected1
        assert it.peek() == 5
        result2 = list(it)
        expected2 = [5, 6, 7, 8, 9]
        assert result2 == expected2

    def test_combined(self) -> None:
        it = peekable(range(10))
        result1 = list(it.takewhile(lambda x: x <= 2))
        expected1 = [0, 1, 2]
        assert result1 == expected1
        assert it.peek() == 3
        it.dropwhile(lambda x: x <= 4)
        assert it.peek() == 5
        result2 = list(it.takewhile(lambda x: x <= 6))
        expected2 = [5, 6]
        assert result2 == expected2
        result3 = list(it)
        expected3 = [7, 8, 9]
        assert result3 == expected3


class TestYieldSplits:
    @mark.parametrize(
        ("iterable", "head", "tail", "min_frac", "freq", "expected"),
        [
            param(
                "abcde",
                3,
                1,
                None,
                None,
                [
                    Split(head=["a", "b", "c"], tail=["d"]),
                    Split(head=["b", "c", "d"], tail=["e"]),
                ],
                id="3/1",
            ),
            param(
                "abcde",
                3,
                1,
                0.4,
                None,
                [
                    Split(head=["a", "b"], tail=["c"]),
                    Split(head=["a", "b", "c"], tail=["d"]),
                    Split(head=["b", "c", "d"], tail=["e"]),
                ],
                id="3/1, min-frac=0.4",
            ),
            param(
                "abcdefg",
                3,
                2,
                None,
                None,
                [
                    Split(head=["a", "b", "c"], tail=["d", "e"]),
                    Split(head=["c", "d", "e"], tail=["f", "g"]),
                ],
                id="3/2, clean tail",
            ),
            param(
                "abcdefgh",
                3,
                2,
                None,
                None,
                [
                    Split(head=["a", "b", "c"], tail=["d", "e"]),
                    Split(head=["c", "d", "e"], tail=["f", "g"]),
                    Split(head=["e", "f", "g"], tail=["h"]),
                ],
                id="3/2, truncated tail",
            ),
            param(
                "abcdefgh",
                3,
                2,
                None,
                1,
                [
                    Split(head=["a", "b", "c"], tail=["d", "e"]),
                    Split(head=["b", "c", "d"], tail=["e", "f"]),
                    Split(head=["c", "d", "e"], tail=["f", "g"]),
                    Split(head=["d", "e", "f"], tail=["g", "h"]),
                    Split(head=["e", "f", "g"], tail=["h"]),
                ],
                id="3/2, freq=1",
            ),
            param("abc", 5, 1, None, None, [], id="len(iterable) < head"),
            param("abc", 1, 5, None, None, [], id="len(iterable) < tail"),
        ],
    )
    def test_main(
        self,
        *,
        iterable: Iterable[str],
        head: int,
        tail: int,
        min_frac: float | None,
        freq: int | None,
        expected: list[Split[list[str]]],
    ) -> None:
        splits = list(yield_splits(iterable, head, tail, min_frac=min_frac, freq=freq))
        assert splits == expected

    def test_repr(self) -> None:
        split = Split(head=["a", "b", "c"], tail=["d"])
        result = repr(split)
        expected = strip_and_dedent(
            """
            Split(
                head=
                    ['a', 'b', 'c']
                tail=
                    ['d']
            )
            """
        )
        assert result == expected
