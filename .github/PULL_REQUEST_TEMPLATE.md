# Pull Request Template

Ref: docs/roadmap/step-XX.md

## Checklist
- [ ] Tests pass in CI
- [ ] Lint and type checks pass
- [ ] Documentation updated if needed
- [ ] Commit message follows Conventional Commits
- [ ] PR description includes Ref: docs/roadmap/step-XX.md
- [ ] docs/codex/last_output.json present with a non-empty "summary"

## Description
Clearly explain the problem and the proposed solution.

## Why
Describe why this change is necessary.

## What changed
List the files, workflows, or guards that were updated.

### Quick command to generate last_output.json
```
pwsh -File tools/codex/ensure_last_output.ps1 -Step "XX" -Title "Step XX - Snapshot" -Summary "Short human summary." -Status "success"
```
