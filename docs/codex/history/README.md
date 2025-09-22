# Codex Step History

This folder stores immutable per-step snapshots generated after each Codex run.

- `reflections/step-<STEP>.md` — archived reflection for a given step.
- `todo/step-<STEP>.md` — copy of the TODO list that was produced at the end of a step.
- `last_output.jsonl` — JSON Lines ledger capturing summary/test metadata for each step.

Snapshots must never be overwritten. If you need to amend a past entry, add an errata
note in a new step rather than rewriting history.
