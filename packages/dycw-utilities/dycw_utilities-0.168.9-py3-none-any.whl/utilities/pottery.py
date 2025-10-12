from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass
from sys import maxsize
from typing import TYPE_CHECKING, override

from pottery import AIORedlock
from pottery.exceptions import ReleaseUnlockedLock
from redis.asyncio import Redis

from utilities.asyncio import sleep_td, timeout_td
from utilities.contextlib import enhanced_async_context_manager
from utilities.iterables import always_iterable
from utilities.whenever import MILLISECOND, SECOND, to_nanoseconds

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterable

    from whenever import Delta

    from utilities.types import MaybeIterable

_NUM: int = 1
_TIMEOUT_RELEASE: Delta = 10 * SECOND
_SLEEP: Delta = MILLISECOND


##


async def extend_lock(
    *, lock: AIORedlock | None = None, raise_on_redis_errors: bool | None = None
) -> None:
    """Extend a lock."""
    if lock is not None:
        await lock.extend(raise_on_redis_errors=raise_on_redis_errors)


##


@enhanced_async_context_manager
async def yield_access(
    redis: MaybeIterable[Redis],
    key: str,
    /,
    *,
    num: int = _NUM,
    timeout_release: Delta = _TIMEOUT_RELEASE,
    num_extensions: int | None = None,
    timeout_acquire: Delta | None = None,
    sleep: Delta = _SLEEP,
    throttle: Delta | None = None,
) -> AsyncIterator[AIORedlock]:
    """Acquire access to a locked resource."""
    if num <= 0:
        raise _YieldAccessNumLocksError(key=key, num=num)
    masters = (  # skipif-ci-and-not-linux
        {redis} if isinstance(redis, Redis) else set(always_iterable(redis))
    )
    locks = [  # skipif-ci-and-not-linux
        AIORedlock(
            key=f"{key}_{i}_of_{num}",
            masters=masters,
            auto_release_time=to_nanoseconds(timeout_release) / 1e9,
            num_extensions=maxsize if num_extensions is None else num_extensions,
        )
        for i in range(1, num + 1)
    ]
    lock: AIORedlock | None = None  # skipif-ci-and-not-linux
    try:  # skipif-ci-and-not-linux
        lock = await _get_first_available_lock(
            key, locks, num=num, timeout=timeout_acquire, sleep=sleep
        )
        yield lock
    finally:  # skipif-ci-and-not-linux
        await sleep_td(throttle)
        if lock is not None:
            with suppress(ReleaseUnlockedLock):
                await lock.release()


async def _get_first_available_lock(
    key: str,
    locks: Iterable[AIORedlock],
    /,
    *,
    num: int = _NUM,
    timeout: Delta | None = None,
    sleep: Delta | None = _SLEEP,
) -> AIORedlock:
    locks = list(locks)  # skipif-ci-and-not-linux
    error = _YieldAccessUnableToAcquireLockError(  # skipif-ci-and-not-linux
        key=key, num=num, timeout=timeout
    )
    async with timeout_td(timeout, error=error):  # skipif-ci-and-not-linux
        while True:
            if (result := await _get_first_available_lock_if_any(locks)) is not None:
                return result
            await sleep_td(sleep)


async def _get_first_available_lock_if_any(
    locks: Iterable[AIORedlock], /
) -> AIORedlock | None:
    for lock in locks:  # skipif-ci-and-not-linux
        if await lock.acquire(blocking=False):
            return lock
    return None  # skipif-ci-and-not-linux


@dataclass(kw_only=True, slots=True)
class YieldAccessError(Exception):
    key: str


@dataclass(kw_only=True, slots=True)
class _YieldAccessNumLocksError(YieldAccessError):
    num: int

    @override
    def __str__(self) -> str:
        return f"Number of locks for {self.key!r} must be positive; got {self.num}"


@dataclass(kw_only=True, slots=True)
class _YieldAccessUnableToAcquireLockError(YieldAccessError):
    num: int
    timeout: Delta | None

    @override
    def __str__(self) -> str:
        return f"Unable to acquire any 1 of {self.num} locks for {self.key!r} after {self.timeout}"  # skipif-ci-and-not-linux


__all__ = ["YieldAccessError", "extend_lock", "yield_access"]
