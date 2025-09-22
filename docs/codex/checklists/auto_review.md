AUTO-REVIEW CHECKLIST (critical items must be YES)

[ ] Tests: global coverage >= threshold and changed files >= delta threshold
[ ] History updated (reflections/todo/jsonl) for current step
[ ] No secrets or tokens in the diff
[ ] Sensitive endpoints require auth and RBAC
[ ] Database model changes have migrations and tests
[ ] Lint and typecheck pass (ruff/mypy or eslint/tsc)
[ ] Obvious N+1 or heavy loops avoided or justified
[ ] Logs are meaningful for new code paths
[ ] README or module docs updated if public surface changed
