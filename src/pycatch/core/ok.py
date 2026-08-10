"""La variante succès de `Result`."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, NoReturn

from .errors import UnwrapError

if TYPE_CHECKING:
    from .result import Result

__all__ = ["Ok"]


@dataclass(frozen=True, slots=True)
class Ok[T]:
    """Variante succès d'un `Result`."""

    value: T

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    def ok(self) -> T:
        return self.value

    def err(self) -> None:
        return None

    def unwrap(self) -> T:
        return self.value

    def unwrap_err(self) -> NoReturn:
        raise UnwrapError(self, f"called `unwrap_err()` on an `Ok` value: {self.value!r}")

    def unwrap_or_raise(self) -> T:
        return self.value

    def unwrap_or(self, default: T) -> T:
        return self.value

    def unwrap_or_else[E](self, fn: Callable[[E], T]) -> T:
        return self.value

    def map[U](self, fn: Callable[[T], U]) -> Ok[U]:
        return Ok(fn(self.value))

    def map_err[E, F](self, fn: Callable[[E], F]) -> Ok[T]:
        return self

    def and_then[U, E](self, fn: Callable[[T], Result[U, E]]) -> Result[U, E]:
        return fn(self.value)

    def or_else[E, F](self, fn: Callable[[E], Result[T, F]]) -> Ok[T]:
        return self

    def map_or[U](self, default: U, fn: Callable[[T], U]) -> U:
        return fn(self.value)

    def map_or_else[E, U](self, default_fn: Callable[[E], U], fn: Callable[[T], U]) -> U:
        return fn(self.value)

    def inspect(self, fn: Callable[[T], None]) -> Ok[T]:
        fn(self.value)
        return self

    def inspect_err[E](self, fn: Callable[[E], None]) -> Ok[T]:
        return self

    def __repr__(self) -> str:
        return f"Ok({self.value!r})"
