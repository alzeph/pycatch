"""Le décorateur `catch` : transforme les exceptions levées en `Result`."""

from __future__ import annotations

import functools
import inspect
from collections.abc import Callable, Coroutine
from typing import Any, overload

from pycatch.core import Err, Ok, Result

__all__ = ["catch"]


class _Catch[E: Exception]:
    """Objet retourné par `catch(...)`, appliqué comme décorateur sur une fonction."""

    def __init__(self, exceptions: tuple[type[E], ...]) -> None:
        self._exceptions = exceptions

    # L'overload async doit rester en premier : `Callable[P, T]` ci-dessous matche
    # structurellement aussi une coroutine (avec T = Coroutine[...]), donc mypy
    # signale un chevauchement alors que l'ordre garantit la bonne résolution.
    @overload
    def __call__[T, **P](  # type: ignore[overload-overlap]
        self, fn: Callable[P, Coroutine[Any, Any, T]]
    ) -> Callable[P, Coroutine[Any, Any, Result[T, E]]]: ...

    @overload
    def __call__[T, **P](self, fn: Callable[P, T]) -> Callable[P, Result[T, E]]: ...

    def __call__(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        if inspect.iscoroutinefunction(fn):
            return self._wrap_async(fn)
        return self._wrap_sync(fn)

    def _wrap_sync(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Result[Any, E]:
            try:
                return Ok(fn(*args, **kwargs))
            except self._exceptions as exc:
                return Err(exc)

        return wrapper

    def _wrap_async(self, fn: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Result[Any, E]:
            try:
                return Ok(await fn(*args, **kwargs))
            except self._exceptions as exc:
                return Err(exc)

        return wrapper


def catch[E: Exception](*exceptions: type[E]) -> _Catch[E]:
    """Décorateur : capture les exceptions listées et retourne un `Result` au lieu de lever.

    Toute exception non listée continue de se propager normalement — la
    signature du `Result` ne doit annoncer que ce qui est réellement capturé.

    Exemple :
        @catch(ValueError, KeyError)
        def parse_age(data: dict) -> int:
            return int(data["age"])

        match parse_age({"age": "invalid"}):
            case Ok(val): ...
            case Err(err): ...
    """
    return _Catch(exceptions)
