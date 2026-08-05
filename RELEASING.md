# Process de release

## Configuration initiale de PyPI (une seule fois)

`pycatch` publie via le *trusted publishing* de PyPI (OIDC) : aucun token
long-lived à gérer, l'autorisation est liée à ce dépôt et à ce workflow
GitHub Actions précis.

> **Avant la première publication**, vérifier que le nom du package
> (`pycatch` dans `pyproject.toml`) est bien disponible sur PyPI. Si ce
> n'est pas le cas, le renommer *avant* de publier — un renommage après
> coup casse tous les `pip install`/`import` existants.

1. Créer un compte PyPI si besoin.
2. Sur <https://pypi.org/manage/account/publishing/>, ajouter un
   *pending trusted publisher* (le projet n'a pas besoin d'exister sur
   PyPI au préalable) :
   - PyPI project name : le nom retenu dans `pyproject.toml`
   - Owner : `alzeph`
   - Repository name : `pycatch`
   - Workflow name : `publish.yml`
   - Environment name : `pypi`
3. Dans les paramètres GitHub du dépôt (`Settings > Environments`), créer
   un environnement `pypi` (protège la publication, permet d'ajouter des
   reviewers si besoin).

## Publier une version

1. Mettre à jour `__version__` dans `src/pycatch/__init__.py` (la version
   du package est single-sourcée depuis ce fichier, voir
   `[tool.hatch.version]` dans `pyproject.toml`).
2. Déplacer le contenu de `## [Unreleased]` dans `CHANGELOG.md` sous une
   nouvelle section `## [X.Y.Z] - AAAA-MM-JJ`, et mettre à jour les liens
   de comparaison en bas de fichier.
3. Vérifier localement : `uv run ruff check src tests && uv run ruff
   format --check src tests && uv run mypy && uv run pytest --cov=pycatch
   --cov-fail-under=100 && uv build`.
4. Commit ("Release X.Y.Z"), merge sur `main`.
5. Tag et push : `git tag vX.Y.Z && git push origin vX.Y.Z`.
6. Créer une [GitHub Release](https://github.com/alzeph/pycatch/releases/new)
   à partir de ce tag. La publier déclenche `.github/workflows/publish.yml`,
   qui build et publie automatiquement sur PyPI.
   - Pour une pré-version (`rc`, `b`, `a`), cocher **"Set as a pre-release"**
     sur GitHub — PyPI la traitera comme une pré-version (non installée par
     défaut par `pip install pycatch`, il faudra `pip install
     pycatch --pre` ou fixer la version exacte).

## Politique release candidate avant le 1.0.0 final

`1.0.0rc1` est une *release candidate* : l'API est considérée figée mais
n'a pas encore été éprouvée par un usage réel en dehors de ce dépôt.
Avant de tagger `1.0.0` (final) :

- laisser la RC disponible au moins quelques semaines pour recueillir des
  retours (issues, cas d'usage réels, éventuels bugs de typage comme celui
  trouvé sur `Err.and_then` avant la RC) ;
- ne merger que des corrections de bug sur `main` pendant cette période,
  pas de nouvelle fonctionnalité qui changerait l'API publique ;
- si un changement d'API s'avère nécessaire suite aux retours, publier
  `1.0.0rc2` plutôt que de modifier `1.0.0rc1` a posteriori.

Une fois `1.0.0` taggé, voir la politique de compatibilité dans
[CONTRIBUTING.md](CONTRIBUTING.md#politique-de-compatibilité-et-dépréciation).
