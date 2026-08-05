import pytest

from pycatch import Err, Ok, catch


class TestSync:
    def test_returns_ok_on_success(self) -> None:
        @catch(ValueError)
        def parse(value: str) -> int:
            return int(value)

        assert parse("42") == Ok(42)

    def test_returns_err_on_listed_exception(self) -> None:
        @catch(ValueError)
        def parse(value: str) -> int:
            return int(value)

        res = parse("invalid")
        assert res.is_err()
        assert isinstance(res.unwrap_err(), ValueError)

    def test_propagates_unlisted_exception(self) -> None:
        @catch(ValueError)
        def boom() -> int:
            raise KeyError("nope")

        with pytest.raises(KeyError):
            boom()

    def test_multi_exceptions(self) -> None:
        @catch(ValueError, KeyError)
        def parse_age(data: dict[str, str]) -> int:
            return int(data["age"])

        assert parse_age({"age": "30"}) == Ok(30)
        assert isinstance(parse_age({"age": "invalid"}).unwrap_err(), ValueError)
        assert isinstance(parse_age({}).unwrap_err(), KeyError)

    def test_preserves_function_metadata(self) -> None:
        @catch(ValueError)
        def parse_age(data: dict[str, str]) -> int:
            """Parse l'âge depuis les données."""
            return int(data["age"])

        assert parse_age.__name__ == "parse_age"
        assert parse_age.__doc__ == "Parse l'âge depuis les données."

    def test_match_on_result(self) -> None:
        @catch(ValueError, KeyError)
        def parse_age(data: dict[str, str]) -> int:
            return int(data["age"])

        match parse_age({"age": "invalid"}):
            case Ok(_):
                pytest.fail("ne devrait pas être Ok")
            case Err(ValueError() as err):
                assert "invalid literal" in str(err)
            case Err(_):
                pytest.fail("aurait dû matcher ValueError")

    def test_passes_args_and_kwargs_through(self) -> None:
        @catch(ValueError)
        def add(a: int, *, b: int) -> int:
            return a + b

        assert add(1, b=2) == Ok(3)

    def test_on_instance_method(self) -> None:
        class Parser:
            def __init__(self, factor: int) -> None:
                self.factor = factor

            @catch(ValueError)
            def parse(self, value: str) -> int:
                return int(value) * self.factor

        parser = Parser(factor=10)
        assert parser.parse("4") == Ok(40)
        assert isinstance(parser.parse("nope").unwrap_err(), ValueError)


class TestAsync:
    @pytest.mark.asyncio
    async def test_returns_ok_on_success(self) -> None:
        @catch(ValueError)
        async def parse(value: str) -> int:
            return int(value)

        assert await parse("42") == Ok(42)

    @pytest.mark.asyncio
    async def test_returns_err_on_listed_exception(self) -> None:
        @catch(ValueError)
        async def parse(value: str) -> int:
            return int(value)

        res = await parse("invalid")
        assert res.is_err()
        assert isinstance(res.unwrap_err(), ValueError)

    @pytest.mark.asyncio
    async def test_propagates_unlisted_exception(self) -> None:
        @catch(ValueError)
        async def boom() -> int:
            raise KeyError("nope")

        with pytest.raises(KeyError):
            await boom()
