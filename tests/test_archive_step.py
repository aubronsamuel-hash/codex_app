import json
import subprocess
import sys
from pathlib import Path


def prepare_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    codex_dir = repo / "docs" / "codex"
    codex_dir.mkdir(parents=True)

    (codex_dir / "reflections.md").write_text("Reflection snapshot\n", encoding="utf-8")
    (codex_dir / "todo_next.md").write_text("1. Item\n", encoding="utf-8")
    last_output_payload = {
        "generated_at": "2025-01-01T00:00:00Z",
        "summary": "Did important work",
        "tests": {"command": "pytest", "passed": 10, "failed": 0},
        "duration_seconds": 42,
    }
    (codex_dir / "last_output.json").write_text(
        json.dumps(last_output_payload), encoding="utf-8"
    )
    return repo


def run_archive(repo: Path, step: str) -> subprocess.CompletedProcess[str]:
    script_path = Path(__file__).resolve().parents[1] / "tools" / "codex" / "archive_step.py"
    return subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--repo-root",
            str(repo),
            "--step",
            step,
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def test_archive_step_creates_history(tmp_path):
    repo = prepare_repo(tmp_path)
    result = run_archive(repo, "001")
    assert result.returncode == 0, result.stderr

    history_root = repo / "docs" / "codex" / "history"
    reflection_copy = history_root / "reflections" / "step-001.md"
    todo_copy = history_root / "todo" / "step-001.md"
    history_log = history_root / "last_output.jsonl"

    assert reflection_copy.read_text(encoding="utf-8") == "Reflection snapshot\n"
    assert todo_copy.read_text(encoding="utf-8") == "1. Item\n"

    lines = history_log.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["timestamp"] == "2025-01-01T00:00:00Z"
    assert entry["step"] == "001"
    assert entry["summary"] == "Did important work"
    assert entry["tests"] == {"command": "pytest", "passed": 10, "failed": 0}
    assert entry["duration_seconds"] == 42


def test_archive_step_refuses_to_overwrite(tmp_path):
    repo = prepare_repo(tmp_path)
    first = run_archive(repo, "002")
    assert first.returncode == 0, first.stderr

    second = run_archive(repo, "002")
    assert second.returncode == 1
    assert "already exists" in second.stderr
