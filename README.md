# Codex App

This repository houses the backend service that Codex automation will grow step by step.
The backend is implemented with FastAPI and packaged under `src/app`.

## Getting started

1. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install the project in editable mode with development dependencies:
   ```bash
   pip install -e .[dev]
   ```

## Running the API locally

Launch the development server with Uvicorn:

```bash
uvicorn app.main:app --reload
```

The health endpoint is available at <http://127.0.0.1:8000/health> and returns service status metadata.

## Tests and coverage

Pytest is configured to collect coverage automatically with a minimum threshold of 85%.
Simply run:

```bash
pytest
```

The default options produce a terminal coverage report and fail the run if thresholds are not met.

## Operational docs

Codex operating guides live under `docs/codex/`.
Refer to `docs/codex/README.md` for automation rules and guard details.
