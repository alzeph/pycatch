"""Tests de non-régression sur le typage statique.

Ce fichier ne vérifie rien à l'exécution : `assert_type` est un no-op au
runtime. La vérification a lieu quand `mypy` analyse ce fichier (voir
`[tool.mypy] files` dans pyproject.toml) — une régression de typage sur
les génériques de `Result`/`Ok`/`Err`/`catch` fait échouer `mypy`, pas
`pytest`.
"""

from __future__ import annotations

from typing import assert_type

from pycatch import Err, Ok, Result, catch


def test_ok_map_preserves_success_type() -> None:
    res: Ok[int] = Ok(1)
    mapped = res.map(str)
    assert_type(mapped, Ok[str])


def test_err_map_err_preserves_error_type() -> None:
    res: Err[ValueError] = Err(ValueError("boom"))
    mapped = res.map_err(str)
    assert_type(mapped, Err[str])


def test_and_then_chains_result_type() -> None:
    def to_positive(n: int) -> Result[int, str]:
        return Ok(n) if n >= 0 else Err("negative")

    res: Ok[int] = Ok(1)
    chained = res.and_then(to_positive)
    assert_type(chained, Result[int, str])


def test_unwrap_or_returns_success_type() -> None:
    res: Result[int, str] = Ok(1)
    assert_type(res.unwrap_or(0), int)


def test_catch_sync_returns_result() -> None:
    @catch(ValueError)
    def parse(value: str) -> int:
        return int(value)

    assert_type(parse("1"), Result[int, ValueError])


async def test_catch_async_returns_awaitable_result() -> None:
    @catch(ValueError)
    async def parse(value: str) -> int:
        return int(value)

    assert_type(await parse("1"), Result[int, ValueError])


def test_catch_on_instance_method_binds_self() -> None:
    class Parser:
        @catch(ValueError)
        def parse(self, value: str) -> int:
            return int(value)

    assert_type(Parser().parse("1"), Result[int, ValueError])
