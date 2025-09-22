# Continuous Integration Guide

This project relies on GitHub Actions to validate code changes. The automation runs three jobs on every push and pull request:

- **backend-tests** executes the FastAPI unit tests with coverage.
- **frontend-tests** is a placeholder that documents the absence of a frontend suite.
- **guards** runs the Codex policy guard suite to enforce repository standards.

## Local verification

Follow these steps before opening a pull request:

1. Install dependencies (once per environment):
   ```bash
   python -m pip install --upgrade pip
   pip install -e .[dev]
   ```
2. Run the combined guard harness. This command executes the pytest suite, generates a coverage summary, and then chains all guard scripts:
   ```bash
   pwsh -File tools/guards/run_all_guards.ps1
   ```

The PowerShell script requires PowerShell 7 or later. On macOS or Linux install `powershell` via your package manager; on Windows use the latest release from the Microsoft Store. The script stops at the first failure so you can iterate quickly.

## Coverage expectations

- Pytest enforces a minimum coverage of 85% (configured in `pyproject.toml`).
- The guard pipeline separately verifies that the generated summary reports at least 70% global coverage.

If coverage falls below the threshold, add or update tests before retrying. Keep the workspace clean by committing only relevant files; the guard script removes transient artifacts such as `coverage_summary.txt` automatically.
