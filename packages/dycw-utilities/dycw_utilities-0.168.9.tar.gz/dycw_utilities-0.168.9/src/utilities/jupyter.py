from __future__ import annotations

from contextlib import ExitStack
from dataclasses import dataclass, field, replace
from itertools import chain
from typing import TYPE_CHECKING, Any, Self

from utilities.ipython import check_ipython_class

if TYPE_CHECKING:
    from types import TracebackType


def is_jupyter() -> bool:
    """Check if `jupyter` is running."""
    try:
        from ipykernel.zmqshell import (  # pyright: ignore[reportMissingImports]
            ZMQInteractiveShell,
        )
    except ImportError:
        return False
    return check_ipython_class(ZMQInteractiveShell)  # pragma: no cover


_DEFAULT_ROWS = 7
_DEFAULT_COLS = 100


@dataclass(slots=True)
class _Show:
    """Context manager which adjusts the display of NDFrames."""

    rows: int | None = field(default=_DEFAULT_ROWS)
    columns: int | None = field(default=_DEFAULT_COLS, kw_only=True)
    dp: int | None = field(default=None, kw_only=True)
    stack: ExitStack = field(default_factory=ExitStack, kw_only=True)

    def __call__(
        self,
        rows: int | None = _DEFAULT_ROWS,
        *,
        dp: int | None = None,
        columns: int | None = _DEFAULT_COLS,
    ) -> Self:
        return replace(self, rows=rows, dp=dp, columns=columns)

    def __enter__(self) -> None:
        self._enter_pandas()
        self._enter_polars()
        _ = self.stack.__enter__()

    def _enter_pandas(self) -> None:
        try:
            from pandas import option_context
        except ModuleNotFoundError:  # pragma: no cover
            pass
        else:
            kwargs: dict[str, Any] = {}
            if self.dp is not None:
                kwargs["display.precision"] = self.dp
            if self.rows is not None:
                kwargs["display.min_rows"] = kwargs["display.max_rows"] = self.rows
            if self.columns is not None:
                kwargs["display.max_columns"] = self.columns
            if len(kwargs) >= 1:
                context = option_context(*chain(*kwargs.items()))
                self.stack.enter_context(context)

    def _enter_polars(self) -> None:
        try:
            from polars import Config
        except ModuleNotFoundError:  # pragma: no cover
            pass
        else:
            kwargs: dict[str, Any] = {}
            if self.dp is not None:
                kwargs["float_precision"] = self.dp
            if self.rows is not None:
                kwargs["tbl_rows"] = self.rows
            if self.columns is not None:
                kwargs["tbl_cols"] = self.columns
            config = Config(**kwargs)
            _ = self.stack.enter_context(config)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        _ = self.stack.__exit__(exc_type, exc_val, traceback)


show = _Show()


__all__ = ["is_jupyter", "show"]
