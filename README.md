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

The service exposes lightweight diagnostics endpoints:

- Health check: <http://127.0.0.1:8000/health>
- Version metadata: <http://127.0.0.1:8000/version>

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/version
```

### Configuration

Settings can be overridden with environment variables before launching the server:

| Variable     | Default       | Description                          |
|--------------|---------------|--------------------------------------|
| `APP_NAME`   | `Codex App`   | Friendly name exposed in `/health`.  |
| `APP_ENV`    | `development` | Execution environment label.         |
| `APP_VERSION`| `0.1.0`       | Version served by `/version`.        |
| `HOST`       | `127.0.0.1`   | Bind address for local development.  |
| `PORT`       | `8000`        | Bind port for the ASGI server.       |

Example (PowerShell or Bash):

```bash
export APP_ENV=production
export HOST=0.0.0.0
export PORT=9000
uvicorn app.main:app --reload --host "$HOST" --port "$PORT"
```

## Tests, coverage, and guards

Pytest is configured to collect coverage automatically with a minimum threshold of 85%.
Run the suite directly when you need a quick check:

```bash
python -m pytest
```

Before opening a pull request execute the consolidated guard harness. It installs no extra tools beyond pytest and ensures the
repository meets Codex policy requirements:

```bash
pwsh -File tools/guards/run_all_guards.ps1
```

The PowerShell script runs pytest, generates `coverage_summary.txt`, and invokes all guards (`policy_guard`, `roadmap_guard`,
`commit_guard`, `secret_scan`, `readme_guard`, and `coverage_guard`). Refer to `docs/CI.md` for details on GitHub Actions jobs
and local setup tips.

## Operational docs

Codex operating guides live under `docs/codex/`.
Refer to `docs/codex/README.md` for automation rules and guard details.
