# pycatch

[![CI](https://github.com/alzeph/pycatch/actions/workflows/ci.yml/badge.svg)](https://github.com/alzeph/pycatch/actions/workflows/ci.yml)
[![Coverage: 100%](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](https://github.com/alzeph/pycatch/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](pyproject.toml)

> **Release candidate.** `pycatch` est en `1.0.0rc1` : l'API est considérée
> figée mais n'a pas encore été éprouvée par un usage réel en dehors de ce
> dépôt. Les retours (issues, cas d'usage, bugs) sont les bienvenus avant
> de tagger la version `1.0.0` finale — voir [RELEASING.md](RELEASING.md).

Gestion d'erreurs fluide pour Python, inspirée du type `Result` de Rust.

`pycatch` expose `Result`, `Ok`, `Err` et un décorateur `catch` pour éviter
d'empiler des dizaines de `try/except` imbriqués. Les erreurs deviennent des
valeurs explicites dans le typage de vos fonctions, et se traitent avec le
pattern matching natif de Python (`match`/`case`).

## Installation

Le paquet est publié sur PyPI sous le nom `pycatch-safe` (le nom `pycatch`
était déjà pris) — l'import Python, lui, reste `pycatch` :

```bash
pip install pycatch-safe
```

```python
import pycatch
```

## Pourquoi

**Avant** — les erreurs possibles sont invisibles dans la signature :

```python
def get_user_avatar(user_id: int) -> str:
    user = db.fetch_user(user_id)       # peut lever UserNotFound
    res = http_client.get(user.avatar_url)  # peut lever HTTPError ou Timeout
    return res.json()["url"]            # peut lever KeyError
```

**Après** — la signature annonce la couleur : ça réussit avec `str`, ou ça
échoue avec une erreur explicite :

```python
def get_user_avatar(user_id: int) -> Result[str, UserError]:
    ...
```

## Usage

### Le décorateur `catch`

`catch(*exceptions)` capture les exceptions listées et retourne un `Result`
au lieu de lever — tout le reste continue de se propager normalement.

```python
from pycatch import Ok, Err, catch

@catch(ValueError, KeyError)
def parse_age(data: dict) -> int:
    return int(data["age"])

res = parse_age({"age": "invalid"})

match res:
    case Ok(val):
        print(f"Âge : {val}")
    case Err(err):
        print(f"Erreur capturée : {err}")
```

`catch` fonctionne aussi bien sur des fonctions `async def` que sur des
méthodes d'instance :

```python
class Parser:
    @catch(ValueError)
    async def parse(self, value: str) -> int:
        return int(value)
```

### Pattern matching sur le type d'exception

```python
match result:
    case Ok(age):
        print(f"User age is valid: {age}")
    case Err(ValueError() as err):
        print(f"Invalid age provided: {err}")
    case Err(KeyError() as err):
        print(f"Missing age field in payload: {err}")
```

### L'API `Result`

`Ok[T]` et `Err[E]` exposent la même API, façon Rust :

| Méthode | Description |
| --- | --- |
| `is_ok()` / `is_err()` | Teste la variante |
| `ok()` / `err()` | `T \| None` / `E \| None` |
| `unwrap()` / `unwrap_err()` | Extrait la valeur ou l'erreur, lève `UnwrapError` si la variante ne correspond pas |
| `unwrap_or(default)` | Valeur, ou `default` si `Err` |
| `unwrap_or_else(fn)` | Valeur, ou `fn(error)` si `Err` |
| `unwrap_or_raise()` | Valeur, ou relève l'exception d'origine contenue dans `Err` — pont vers du code legacy basé sur des exceptions |
| `map(fn)` | Transforme la valeur si `Ok`, no-op si `Err` |
| `map_err(fn)` | Transforme l'erreur si `Err`, no-op si `Ok` |
| `map_or(default, fn)` | `fn(valeur)` si `Ok`, `default` si `Err` |
| `map_or_else(default_fn, fn)` | `fn(valeur)` si `Ok`, `default_fn(erreur)` si `Err` |
| `and_then(fn)` | Chaîne une opération qui retourne elle-même un `Result` — évite d'imbriquer les `try/except` |
| `or_else(fn)` | Chaîne un `Result` de repli sur l'erreur si `Err`, no-op si `Ok` |
| `inspect(fn)` / `inspect_err(fn)` | Effet de bord (logging...) sur la valeur/l'erreur sans casser la chaîne fluide |

`pycatch` expose aussi `is_ok(result)` / `is_err(result)`, deux fonctions
utilisant `TypeIs` ([PEP 742](https://peps.python.org/pep-0742/)) pour
rétrécir le type de `result` en dehors du pattern matching :

```python
from pycatch import Result, is_ok

def describe(res: Result[int, str]) -> str:
    if is_ok(res):
        return f"succès : {res.value}"  # res est ici typé Ok[int]
    return f"échec : {res.error}"       # res est ici typé Err[str]
```

```python
result = (
    parse_age({"age": "30"})
    .map(lambda age: age + 1)
    .and_then(lambda age: Ok(age) if age < 150 else Err(ValueError("trop vieux")))
)
```

`Ok` et `Err` sont de simples constructeurs, librement instanciables — pas de
factory imposée : `Ok(42)`, `Err(ValueError("..."))`.

## Typage

Le package est entièrement typé (`py.typed`, `mypy --strict`), avec des
génériques modernes (PEP 695, Python 3.12+). Le décorateur `catch` préserve
la signature de la fonction décorée grâce à `ParamSpec`.

## Compatibilité

`pycatch` nécessite **Python 3.12+**. C'est un choix assumé, pas un oubli :
`Ok`/`Err`/`Result` utilisent la syntaxe générique moderne de
[PEP 695](https://peps.python.org/pep-0695/) (`class Ok[T]`,
`type Result[T, E] = ...`), qui n'existe pas avant 3.12. Supporter 3.10/3.11
demanderait de réécrire ces génériques avec `Generic[T]`/`TypeVar` — ce
n'est pas prévu à court terme, mais une contribution est bienvenue si ce
besoin se fait sentir.

## Par rapport aux alternatives

Deux bibliothèques Python occupent un terrain proche :

- **[`result`](https://github.com/rustedpy/result)** propose une API très
  proche (`Ok`, `Err`, `is_ok`/`is_err`, `map`, `unwrap_or`, pattern
  matching...) et un décorateur équivalent (`as_result`). Le dépôt a été
  **archivé par son auteur le 25 juin 2026** ("this project is no longer
  maintained") : une base solide, mais qui ne recevra plus de correctifs.
- **[`returns`](https://github.com/dry-python/returns)** est un écosystème
  de programmation fonctionnelle bien plus large : `Result`, mais aussi
  `Maybe`, `IO`/`IOResult`, `Future`/`FutureResult`, `RequiresContext`,
  composition monadique, higher-kinded types émulés... Puissant pour
  adopter la programmation fonctionnelle dans son ensemble, avec une
  courbe d'apprentissage et une surface d'API nettement plus importantes
  si le seul besoin est de remplacer des `try/except`.

`pycatch` vise un périmètre plus restreint et assumé : seulement `Result`
et un décorateur `catch`, activement maintenu, ciblant explicitement
Python 3.12+ pour s'appuyer sur les génériques natifs du langage
(PEP 695) plutôt que de réimplémenter du typage générique compatible avec
une plage de versions plus large.

*(Comparaison établie en août 2026 — vérifiez l'état actuel de ces projets
avant de faire votre choix.)*

## Développement

```bash
uv sync
uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy
uv run pytest --cov=pycatch --cov-report=term-missing
```

Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour contribuer,
[CHANGELOG.md](CHANGELOG.md) pour l'historique des versions, et
[RELEASING.md](RELEASING.md) pour le process de publication.

## Licence

[MIT](LICENSE)
