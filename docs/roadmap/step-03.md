## Etape 03 - Healthcheck + Version endpoint

Les routes `/health` et `/version` doivent etre exposees via `src/app/api/routes/`. Le endpoint health repond `{ "status": "ok" }`. Le endpoint version lit la version depuis `pyproject.toml` (clefs `tool.poetry.version` ou `project.version`) et retombe sur la constante `APP_VERSION` definie dans `src/app/core/config.py` en absence d'information fiable.

Mettre a jour `src/app/main.py` pour inclure ces routeurs et ajouter des tests dans `tests/test_health.py` et `tests/test_version.py` couvrant les cas de base et la resolution de version.
