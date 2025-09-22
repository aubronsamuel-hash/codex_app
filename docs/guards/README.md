# Guards README

This repo enforces a strict roadmap reference policy on every PR.

## Why it fails
- `roadmap_guard.ps1` scans the PR body and last commit message.
- If neither contains a line exactly like: `Ref: docs/roadmap/step-XX.md`, the guard fails.

## Quick fix (local)
1) Decide the step file you are implementing, e.g. `docs/roadmap/step-04.md`.
2) Run:

   pwsh -File tools/codex/ensure_roadmap_ref.ps1 -StepRef "docs/roadmap/step-04.md"

3) Push the branch and re-run CI.

## Quick fix (on GitHub UI)
- Edit the PR description and add a line at the end:

  Ref: docs/roadmap/step-04.md

## Prevention
- Use the PR template; keep the `Ref:` line updated when you change steps.
- Commit messages for roadmap work should include the `Ref:` line.

## Runner notes
- We run guards on `ubuntu-latest` with PowerShell Core using `shell: pwsh`.
- Do not use `powershell/powershell@v1` or `actions/setup-powershell`.
