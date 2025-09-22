#!/usr/bin/env python3
"""Archive Codex step outputs without losing historical data."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import shutil
import sys
from typing import Any, Dict


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Archive the current Codex step snapshot into the immutable history "
            "folders."
        )
    )
    parser.add_argument(
        "--step",
        required=True,
        help="Step identifier, e.g. '07' or '2025-09-22'.",
    )
    parser.add_argument(
        "--timestamp",
        help=(
            "ISO timestamp to use for the history entry. Defaults to the "
            "value from last_output.json or the current UTC time."
        ),
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Optional path to the repository root. Defaults to the script's parent directory.",
    )
    return parser.parse_args()


def repo_root_from_args(args: argparse.Namespace) -> Path:
    if args.repo_root:
        return Path(args.repo_root).expanduser().resolve()
    return Path(__file__).resolve().parents[2]


def load_json(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as fp:
            return json.load(fp)
    except FileNotFoundError as exc:
        raise SystemExit(f"Missing required file: {path}") from exc


def iso_timestamp(args_timestamp: str | None, last_output: Dict[str, Any]) -> str:
    if args_timestamp:
        return args_timestamp
    generated = last_output.get("generated_at")
    if generated:
        return generated
    return datetime.now(timezone.utc).isoformat()


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def copy_snapshot(src: Path, dest: Path, label: str) -> None:
    if not src.exists():
        raise SystemExit(f"Cannot archive {label}: {src} does not exist.")
    if dest.exists():
        raise SystemExit(
            f"Refusing to overwrite existing {label} history: {dest} already exists."
        )
    ensure_parent(dest)
    shutil.copy2(src, dest)


def append_last_output(
    history_log_path: Path,
    step: str,
    timestamp_value: str,
    last_output: Dict[str, Any],
) -> None:
    ensure_parent(history_log_path)

    entry = {
        "timestamp": timestamp_value,
        "step": step,
        "summary": last_output.get("summary"),
        "tests": last_output.get("tests"),
    }

    optional_keys = ["duration_seconds", "token_cost", "diff"]
    for key in optional_keys:
        if key in last_output:
            entry[key] = last_output[key]

    if history_log_path.exists():
        with history_log_path.open("r", encoding="utf-8") as fp:
            for line_number, line in enumerate(fp, start=1):
                if not line.strip():
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise SystemExit(
                        f"Invalid JSON on line {line_number} of {history_log_path}: {exc}"
                    )
                if payload.get("step") == step:
                    raise SystemExit(
                        f"History already contains an entry for step {step} at line {line_number}."
                    )

    with history_log_path.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main() -> None:
    args = parse_args()
    repo_root = repo_root_from_args(args)

    codex_dir = repo_root / "docs" / "codex"
    reflections_src = codex_dir / "reflections.md"
    todo_src = codex_dir / "todo_next.md"
    last_output_path = codex_dir / "last_output.json"
    last_output_data = load_json(last_output_path)

    history_dir = codex_dir / "history"
    reflections_dest = history_dir / "reflections" / f"step-{args.step}.md"
    todo_dest = history_dir / "todo" / f"step-{args.step}.md"
    history_log = history_dir / "last_output.jsonl"

    timestamp_value = iso_timestamp(args.timestamp, last_output_data)

    copy_snapshot(reflections_src, reflections_dest, "reflection")
    copy_snapshot(todo_src, todo_dest, "TODO list")
    append_last_output(history_log, args.step, timestamp_value, last_output_data)

    print(f"Archived step {args.step} to {history_dir}.")


if __name__ == "__main__":
    try:
        main()
    except SystemExit as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
