## Etape 03 - Healthcheck + Version endpoint

* **Contexte**:
  Nous avons mis en place la base FastAPI, les tests et la configuration CI/CD.
  Prochaine étape: ajouter un **endpoint health** et un **endpoint version**, indispensables pour l’observabilité et la supervision CI/CD (smoke tests, monitoring, etc.).

* **Attendu**:

  1. Ajouter dans `src/app/api/` deux routes:

     * `GET /health` → retourne `{"status": "ok"}`.
     * `GET /version` → retourne `{"version": "<numéro>"}` basé sur `pyproject.toml` ou une constante `APP_VERSION` définie dans `src/app/core/config.py`.
  2. Mettre à jour `src/app/main.py` pour inclure ces endpoints.
  3. Écrire des tests unitaires dédiés (`tests/test_health.py`, `tests/test_version.py`).
  4. Vérifier que la CI backend passe avec couverture complète des deux nouveaux endpoints.
  5. Ajouter une validation dans la CI (workflow `backend-tests.yml`) pour exécuter ces tests.

* **Sorties**:

  * `src/app/api/routes/health.py`
  * `src/app/api/routes/version.py`
  * `src/app/core/config.py` (constante `APP_VERSION`)
  * `tests/test_health.py`
  * `tests/test_version.py`
  * CI verte avec >95% coverage.

* **Commit**:

  ```
  feat(api): add health and version endpoints
  ```

* **Ref**: `docs/roadmap/step-03.md`

* **VALIDATE? yes/no**
