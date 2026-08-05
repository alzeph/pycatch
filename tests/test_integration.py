"""Test d'intégration bout-en-bout : reprend le scénario `get_user_avatar`
du README pour démontrer l'usage réel de `catch` + `and_then` — chaîner des
étapes qui peuvent échouer avec des types d'erreur *différents*, sans
imbriquer de try/except.
"""

from __future__ import annotations

from dataclasses import dataclass

from pycatch import Err, Ok, Result, catch


class UserNotFoundError(Exception):
    pass


class HTTPError(Exception):
    pass


@dataclass
class User:
    id: int
    avatar_url: str


class Database:
    def __init__(self, users: dict[int, User]) -> None:
        self._users = users

    @catch(UserNotFoundError)
    def fetch_user(self, user_id: int) -> User:
        try:
            return self._users[user_id]
        except KeyError:
            raise UserNotFoundError(f"no user with id {user_id}") from None


class HTTPClient:
    def __init__(self, responses: dict[str, dict[str, str]]) -> None:
        self._responses = responses

    @catch(HTTPError)
    def get_json(self, url: str) -> dict[str, str]:
        if url not in self._responses:
            raise HTTPError(f"unreachable: {url}")
        return self._responses[url]


@catch(KeyError)
def extract_url(payload: dict[str, str]) -> str:
    return payload["url"]


def get_user_avatar(db: Database, http: HTTPClient, user_id: int) -> Result[str, Exception]:
    return (
        db.fetch_user(user_id)
        .and_then(lambda user: http.get_json(user.avatar_url))
        .and_then(extract_url)
    )


class TestGetUserAvatar:
    def test_happy_path(self) -> None:
        db = Database({1: User(id=1, avatar_url="https://x/avatar/1")})
        http = HTTPClient({"https://x/avatar/1": {"url": "https://cdn/1.png"}})

        assert get_user_avatar(db, http, 1) == Ok("https://cdn/1.png")

    def test_user_not_found(self) -> None:
        db = Database({})
        http = HTTPClient({})

        res = get_user_avatar(db, http, 404)

        assert isinstance(res.unwrap_err(), UserNotFoundError)

    def test_http_error(self) -> None:
        db = Database({1: User(id=1, avatar_url="https://x/avatar/1")})
        http = HTTPClient({})

        res = get_user_avatar(db, http, 1)

        assert isinstance(res.unwrap_err(), HTTPError)

    def test_malformed_payload(self) -> None:
        db = Database({1: User(id=1, avatar_url="https://x/avatar/1")})
        http = HTTPClient({"https://x/avatar/1": {"not_url": "oops"}})

        res = get_user_avatar(db, http, 1)

        assert isinstance(res.unwrap_err(), KeyError)

    def test_match_discriminates_the_three_failure_modes(self) -> None:
        db = Database({})
        http = HTTPClient({})

        match get_user_avatar(db, http, 1):
            case Ok(_):
                raise AssertionError("ne devrait pas être Ok")
            case Err(UserNotFoundError()):
                pass
            case Err(err):
                raise AssertionError(f"erreur inattendue : {err!r}")
