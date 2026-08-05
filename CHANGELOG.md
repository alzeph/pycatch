# Changelog

Toutes les modifications notables de ce projet sont documentées ici.

Le format suit [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [Unreleased]

## [1.0.0rc1] - 2026-08-05

Première version publique (release candidate). Aucune version antérieure
n'a été publiée sur PyPI — le développement `0.x` est resté interne à ce
dépôt. Distribuée sur PyPI sous le nom `pycatch-safe` (`pycatch` était déjà
pris) ; l'import Python reste `import pycatch`.

### Added

- `Result[T, E]`, `Ok[T]` et `Err[E]` : type de résultat façon Rust,
  compatible avec le pattern matching (`match`/`case`).
- API `Ok`/`Err` : `is_ok`, `is_err`, `ok`, `err`, `unwrap`, `unwrap_err`,
  `unwrap_or`, `unwrap_or_else`, `unwrap_or_raise`, `map`, `map_err`,
  `and_then`.
- Décorateur `catch(*exceptions)` : capture les exceptions listées et
  retourne un `Result` au lieu de lever. Fonctionne sur des fonctions
  synchrones, des coroutines `async def` et des méthodes d'instance, en
  préservant la signature d'origine (`ParamSpec`).
- `UnwrapError`, levée par `unwrap()`/`unwrap_err()` quand la variante
  attendue est absente.
- Package entièrement typé (`py.typed`, `mypy --strict`, génériques PEP 695).

[Unreleased]: https://github.com/alzeph/pycatch/compare/v1.0.0rc1...HEAD
[1.0.0rc1]: https://github.com/alzeph/pycatch/releases/tag/v1.0.0rc1
