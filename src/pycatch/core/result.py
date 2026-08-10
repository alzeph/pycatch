"""Le type `Result[T, E]`, union des deux variantes `Ok` et `Err`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .err import Err
from .ok import Ok

if TYPE_CHECKING:
    from typing_extensions import TypeIs

__all__ = ["Result", "is_err", "is_ok"]

type Result[T, E] = Ok[T] | Err[E]


def is_ok[T, E](result: Result[T, E]) -> TypeIs[Ok[T]]:
    """Teste si `result` est un `Ok`, avec rétrécissement de type (`TypeIs`).

    Contrairement à `result.is_ok()`, mypy sait ensuite que `result` est un
    `Ok[T]` dans le bloc `if` — utile en dehors du pattern matching :

        if is_ok(result):
            reveal_type(result)  # Ok[T]
    """
    return isinstance(result, Ok)


def is_err[T, E](result: Result[T, E]) -> TypeIs[Err[E]]:
    """Teste si `result` est un `Err`, avec rétrécissement de type (`TypeIs`)."""
    return isinstance(result, Err)
