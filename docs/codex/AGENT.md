# CODEX AGENT OPERATING GUIDE (ASCII ONLY)

GOAL
-----
Ship production-ready code for the app while obeying policies and learning from mistakes.

GOLDEN LOOP
-----------
PLAN -> CODE -> TEST -> REVIEW -> REFLECT -> MEMORIZE

HARD CONSTRAINTS
----------------
- Never edit production directly. Work in sandbox branch or ephemeral branch.
- Respect tools/guards/policy.toml, denylist patterns, and coverage gates.
- Every modified file must have a matching test or a short written justification.
- If any guard fails: perform Retry-1, then Retry-2. If still failing, stop and create TODO items.

REQUIRED OUTPUTS EACH STEP
--------------------------
- docs/codex/last_output.json
- docs/codex/reflections.md (<=200 words)
- docs/codex/todo_next.md (ordered list)

ARCHIVE SNAPSHOT
----------------
- Run `python tools/codex/archive_step.py --step <STEP>` to copy the current
  reflections and TODO list into `docs/codex/history/` and append a JSON line to
  `docs/codex/history/last_output.jsonl`.
- Never overwrite an existing history file. If a mistake slips in, correct it in a
  later step instead of rewriting past records.

MEMORY
------
- docs/codex/memory/decisions.jsonl (append-only; never rewrite past entries)
- docs/codex/memory/anti_patterns.json (append-only when recurring mistakes are found)

CHECKLIST BEFORE OPENING PR
---------------------------
Use docs/codex/checklists/auto_review.md and ensure all critical items are satisfied.

BRANCH AND COMMITS
------------------
- Branch name: feat/step-XX-codex or fix/issue-YY-codex
- Conventional Commits. Prefix subject with [codex] when authored by this agent.

POLICY VIOLATIONS
-----------------
- If policy_guard reports a violation, fix the root cause in code or configuration.
- Do not bypass guards. If the guard is wrong, propose a patch to the guard with rationale.

