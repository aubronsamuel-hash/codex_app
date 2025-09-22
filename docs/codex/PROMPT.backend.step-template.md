SYSTEM:
You are Codex. Implement backend step {STEP}. Follow the operating loop.

CONTEXT:
- FastAPI + SQLAlchemy + Alembic + Pydantic v2
- Coverage threshold as defined in policy.toml
- Use repository/service layers when relevant
- Provide migrations and tests

TASK:
- Implement the feature(s) specified in docs/roadmap/step-{STEP}.md
- Update or add tests under tests/
- Update docs if needed

OUTPUTS:
- Update docs/codex/last_output.json, reflections.md, todo_next.md

