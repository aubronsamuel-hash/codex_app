# Step 01 - Enable guards and CI

Objectives:
- Ensure policy_guard, roadmap_guard, commit_guard, secret_scan in CI.
- Add coverage thresholds and fail if unmet.
- Produce a green baseline with no app code changes yet.

Acceptance:
- All CI jobs run and pass in an empty change with example tests.
- README updated to document how to run guards locally.
