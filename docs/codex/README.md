# Codex Docs

This folder contains all the operational docs for the Codex agent.
All files are ASCII-only to avoid encoding issues on Windows PowerShell.

Key files:
- AGENT.md: rules and operating loop
- PROMPT.master.md: the master prompt for running Codex step-by-step
- checklists/auto_review.md: the self-review checklist
- memory/: long-term memory files
- templates/: commit and PR templates
- runbooks/: incident and playbook documents
- last_output.json, reflections.md, todo_next.md: updated on each step
- history/: append-only archive of per-step reflections, TODOs, and last_output entries
- tools/codex/archive_step.py: helper script that snapshots the current step into history

## Archiving workflow

After completing a step, run `python tools/codex/archive_step.py --step <STEP>` from the
repository root. The script copies the current `reflections.md` and `todo_next.md` into
`docs/codex/history/reflections/` and `docs/codex/history/todo/` respectively and appends a
JSON line to `docs/codex/history/last_output.jsonl`. If any history file for the provided
step already exists, the script aborts instead of overwriting it. Use the `--timestamp`
flag to override the recorded timestamp when necessary.

