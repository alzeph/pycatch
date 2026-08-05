"""La variante échec de `Result`."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, NoReturn

from .errors import UnwrapError

if TYPE_CHECKING:
    from .result import Result

__all__ = ["Err"]


@dataclass(frozen=True, slots=True)
class Err[E]:
    """Variante échec d'un `Result`."""

    error: E

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def ok(self) -> None:
        return None

    def err(self) -> E:
        return self.error

    def unwrap(self) -> NoReturn:
        raise UnwrapError(self, f"called `unwrap()` on an `Err` value: {self.error!r}")

    def unwrap_err(self) -> E:
        return self.error

    def unwrap_or_raise(self) -> NoReturn:
        """Relève l'exception d'origine — pont vers du code qui attend un try/except.

        Contrairement à `unwrap()`, qui lève `UnwrapError` quel que soit le
        contenu de `error`, cette méthode relève `error` lui-même quand c'est
        une exception (traceback d'origine préservé), pour interfacer un
        `Result` produit par `catch` avec du code legacy basé sur des
        exceptions.
        """
        if isinstance(self.error, BaseException):
            raise self.error
        raise UnwrapError(
            self,
            f"called `unwrap_or_raise()` on an `Err` value that is not an exception: "
            f"{self.error!r}",
        )

    def unwrap_or[T](self, default: T) -> T:
        return default

    def unwrap_or_else[T](self, fn: Callable[[E], T]) -> T:
        return fn(self.error)

    def map[T, U](self, fn: Callable[[T], U]) -> Err[E]:
        return self

    def map_err[F](self, fn: Callable[[E], F]) -> Err[F]:
        return Err(fn(self.error))

    def and_then[T, U, F](self, fn: Callable[[T], Result[U, F]]) -> Err[E]:
        return self

    def __repr__(self) -> str:
        return f"Err({self.error!r})"
