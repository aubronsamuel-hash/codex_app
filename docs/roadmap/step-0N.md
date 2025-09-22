# Step 0N - Backend bootstrap baseline

## Context
- The backend stack is FastAPI with SQLAlchemy, Alembic, and Pydantic, so the project needs a Python package layout that supports that stack from the start ([docs/codex/PROMPT.backend.step-template.md](../codex/PROMPT.backend.step-template.md)).
- Guards enforce 70% global coverage and 60% on changed files, so the initial skeleton must ship with tests that satisfy those thresholds ([tools/guards/policy.toml](../../tools/guards/policy.toml)).
- The auto-review checklist requires documenting public surfaces, which applies once we expose a health endpoint ([docs/codex/checklists/auto_review.md](../codex/checklists/auto_review.md)).

## Objectives
- Scaffold a `src/app` package with a FastAPI application factory and an `/health` endpoint returning service status metadata.
- Provide pytest-based tests with coverage instrumentation that keep the baseline above guard thresholds.
- Publish developer instructions for installing dependencies, running the server locally, and executing tests with coverage.

## Tasks
1. Add a `pyproject.toml` configured for a `codex-app` package under `src/`, including runtime dependencies (`fastapi`, `pydantic`, `uvicorn`) and dev dependencies (`pytest`, `pytest-cov`, `httpx`).
2. Create `app/main.py` with a `create_app()` factory, module-level `app` instance, and router registration.
3. Add `app/api/health.py` that defines the `/health` route and response schema.
4. Implement pytest tests covering the factory and health endpoint behaviour.
5. Configure pytest coverage defaults (fail-under >= 85%) via `pyproject.toml` or config file.
6. Update `README.md` with setup, run, and test instructions.

## Acceptance Criteria
- `pytest` with coverage succeeds locally without additional flags.
- Coverage thresholds meet or exceed policy (>= 85% overall from configuration).
- `GET /health` responds with HTTP 200 and expected JSON payload in tests.
- Documentation shows developers how to install dependencies, run the API, and execute tests.
