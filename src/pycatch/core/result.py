"""Le type `Result[T, E]`, union des deux variantes `Ok` et `Err`."""

from __future__ import annotations

from .err import Err
from .ok import Ok

__all__ = ["Result"]

type Result[T, E] = Ok[T] | Err[E]
