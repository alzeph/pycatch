import pytest

from pycatch import Err, Ok, UnwrapError


class TestOk:
    def test_is_ok_is_err(self) -> None:
        res = Ok(42)
        assert res.is_ok() is True
        assert res.is_err() is False

    def test_ok_err(self) -> None:
        res = Ok(42)
        assert res.ok() == 42
        assert res.err() is None

    def test_unwrap(self) -> None:
        assert Ok(42).unwrap() == 42

    def test_unwrap_err_raises(self) -> None:
        with pytest.raises(UnwrapError):
            Ok(42).unwrap_err()

    def test_unwrap_or_raise(self) -> None:
        assert Ok(42).unwrap_or_raise() == 42

    def test_unwrap_or(self) -> None:
        assert Ok(42).unwrap_or(0) == 42

    def test_unwrap_or_else(self) -> None:
        assert Ok(42).unwrap_or_else(lambda _e: 0) == 42

    def test_map(self) -> None:
        assert Ok(21).map(lambda v: v * 2) == Ok(42)

    def test_map_err_is_noop(self) -> None:
        res = Ok(42)
        assert res.map_err(lambda e: str(e)) == res

    def test_and_then(self) -> None:
        assert Ok(21).and_then(lambda v: Ok(v * 2)) == Ok(42)

    def test_repr(self) -> None:
        assert repr(Ok(42)) == "Ok(42)"

    def test_equality(self) -> None:
        assert Ok(1) == Ok(1)
        assert Ok(1) != Ok(2)
        assert Ok(1) != Err(1)


class TestErr:
    def test_is_ok_is_err(self) -> None:
        res = Err("boom")
        assert res.is_ok() is False
        assert res.is_err() is True

    def test_ok_err(self) -> None:
        res = Err("boom")
        assert res.ok() is None
        assert res.err() == "boom"

    def test_unwrap_raises(self) -> None:
        with pytest.raises(UnwrapError):
            Err("boom").unwrap()

    def test_unwrap_err(self) -> None:
        assert Err("boom").unwrap_err() == "boom"

    def test_unwrap_or_raise_reraises_the_original_exception(self) -> None:
        original = ValueError("invalid")
        with pytest.raises(ValueError) as exc_info:
            Err(original).unwrap_or_raise()
        assert exc_info.value is original

    def test_unwrap_or_raise_on_non_exception_error_raises_unwrap_error(self) -> None:
        with pytest.raises(UnwrapError):
            Err("boom").unwrap_or_raise()

    def test_unwrap_or(self) -> None:
        assert Err("boom").unwrap_or(0) == 0

    def test_unwrap_or_else(self) -> None:
        assert Err("boom").unwrap_or_else(lambda e: len(e)) == 4

    def test_map_is_noop(self) -> None:
        res: Err[str] = Err("boom")
        assert res.map(lambda v: v * 2) == res

    def test_map_err(self) -> None:
        assert Err("boom").map_err(str.upper) == Err("BOOM")

    def test_and_then_is_noop(self) -> None:
        res: Err[str] = Err("boom")
        assert res.and_then(lambda v: Ok(v)) == res

    def test_repr(self) -> None:
        assert repr(Err("boom")) == "Err('boom')"

    def test_equality(self) -> None:
        assert Err("boom") == Err("boom")
        assert Err("boom") != Err("bang")


class TestPatternMatching:
    def test_match_ok(self) -> None:
        res = Ok(42)
        match res:
            case Ok(value):
                assert value == 42
            case Err(_):
                pytest.fail("ne devrait pas matcher Err")

    def test_match_err_by_exception_type(self) -> None:
        res = Err(ValueError("invalid"))
        match res:
            case Ok(_):
                pytest.fail("ne devrait pas matcher Ok")
            case Err(ValueError() as err):
                assert str(err) == "invalid"
            case Err(_):
                pytest.fail("aurait dû matcher ValueError")

    def test_match_err_discriminates_exception_type(self) -> None:
        res = Err(KeyError("age"))
        match res:
            case Err(ValueError()):
                pytest.fail("ne devrait pas matcher ValueError")
            case Err(KeyError() as err):
                assert err.args == ("age",)
