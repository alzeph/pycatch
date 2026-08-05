"""Exception levée par les opérations `unwrap` qui échouent."""

from __future__ import annotations

__all__ = ["UnwrapError"]


class UnwrapError(Exception):
    """Levée par `unwrap()` ou `unwrap_err()` quand la variante attendue est absente."""

    def __init__(self, result: object, message: str) -> None:
        self.result = result
        super().__init__(message)
