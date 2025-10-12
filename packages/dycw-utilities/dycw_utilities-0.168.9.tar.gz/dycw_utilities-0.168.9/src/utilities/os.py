from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass
from os import cpu_count, environ, getenv
from typing import TYPE_CHECKING, Literal, assert_never, overload, override

from utilities.contextlib import enhanced_context_manager
from utilities.iterables import OneStrEmptyError, one_str
from utilities.platform import SYSTEM

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping


type IntOrAll = int | Literal["all"]


##


def get_cpu_count() -> int:
    """Get the CPU count."""
    count = cpu_count()
    if count is None:  # pragma: no cover
        raise GetCPUCountError
    return count


@dataclass(kw_only=True, slots=True)
class GetCPUCountError(Exception):
    @override
    def __str__(self) -> str:
        return "CPU count must not be None"  # pragma: no cover


CPU_COUNT = get_cpu_count()


##


def get_cpu_use(*, n: IntOrAll = "all") -> int:
    """Resolve for the number of CPUs to use."""
    match n:
        case int():
            if n >= 1:
                return n
            raise GetCPUUseError(n=n)
        case "all":
            return CPU_COUNT
        case never:
            assert_never(never)


@dataclass(kw_only=True, slots=True)
class GetCPUUseError(Exception):
    n: int

    @override
    def __str__(self) -> str:
        return f"Invalid number of CPUs to use: {self.n}"


##


@overload
def get_env_var(
    key: str, /, *, case_sensitive: bool = False, default: str, nullable: bool = False
) -> str: ...
@overload
def get_env_var(
    key: str,
    /,
    *,
    case_sensitive: bool = False,
    default: None = None,
    nullable: Literal[False] = False,
) -> str: ...
@overload
def get_env_var(
    key: str,
    /,
    *,
    case_sensitive: bool = False,
    default: str | None = None,
    nullable: bool = False,
) -> str | None: ...
def get_env_var(
    key: str,
    /,
    *,
    case_sensitive: bool = False,
    default: str | None = None,
    nullable: bool = False,
) -> str | None:
    """Get an environment variable."""
    try:
        key_use = one_str(environ, key, case_sensitive=case_sensitive)
    except OneStrEmptyError:
        match default, nullable:
            case None, False:
                raise GetEnvVarError(key=key, case_sensitive=case_sensitive) from None
            case None, True:
                return None
            case str(), _:
                return default
            case never:
                assert_never(never)
    return environ[key_use]


@dataclass(kw_only=True, slots=True)
class GetEnvVarError(Exception):
    key: str
    case_sensitive: bool = False

    @override
    def __str__(self) -> str:
        desc = f"No environment variable {self.key!r}"
        return desc if self.case_sensitive else f"{desc} (modulo case)"


##


def get_effective_group_id() -> int | None:
    """Get the effective group ID."""
    match SYSTEM:
        case "windows":  # skipif-not-windows
            return None
        case "mac" | "linux":  # skipif-windows
            from os import getegid

            return getegid()
        case never:
            assert_never(never)


def get_effective_user_id() -> int | None:
    """Get the effective user ID."""
    match SYSTEM:
        case "windows":  # skipif-not-windows
            return None
        case "mac" | "linux":  # skipif-windows
            from os import geteuid

            return geteuid()
        case never:
            assert_never(never)


EFFECTIVE_USER_ID = get_effective_user_id()
EFFECTIVE_GROUP_ID = get_effective_group_id()


##


def is_debug() -> bool:
    """Check if we are in `DEBUG` mode."""
    return get_env_var("DEBUG", nullable=True) is not None


##


def is_pytest() -> bool:
    """Check if `pytest` is running."""
    return get_env_var("PYTEST_VERSION", nullable=True) is not None


##


@enhanced_context_manager
def temp_environ(
    env: Mapping[str, str | None] | None = None, **env_kwargs: str | None
) -> Iterator[None]:
    """Context manager with temporary environment variable set."""
    mapping: dict[str, str | None] = ({} if env is None else dict(env)) | env_kwargs
    prev = {key: getenv(key) for key in mapping}

    def apply(mapping: Mapping[str, str | None], /) -> None:
        for key, value in mapping.items():
            if value is None:
                with suppress(KeyError):
                    del environ[key]
            else:
                environ[key] = value

    apply(mapping)
    try:
        yield
    finally:
        apply(prev)


__all__ = [
    "CPU_COUNT",
    "EFFECTIVE_GROUP_ID",
    "EFFECTIVE_USER_ID",
    "GetCPUCountError",
    "GetCPUUseError",
    "IntOrAll",
    "get_cpu_count",
    "get_cpu_use",
    "get_effective_group_id",
    "get_effective_user_id",
    "get_env_var",
    "is_debug",
    "is_pytest",
    "temp_environ",
]
