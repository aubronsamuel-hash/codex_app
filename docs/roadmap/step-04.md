# Roadmap - Step 04

Context

* Operations need a way to plan and monitor missions. The backend only persists auth data today, so we must introduce a first-class
  mission record with scheduling metadata and status tracking.
* Step 04 focuses on the domain model only. API handlers and background automation will arrive in later steps once we stabilise
  the schema.

Goals

* [ ] Introduce a `Mission` SQLAlchemy model that stores business identifiers, scheduling windows, audit timestamps, and status.
* [ ] Enforce controlled status transitions via domain helpers so that missions can only progress forward.
* [ ] Provide Pydantic schemas to validate create/update payloads for future API work.
* [ ] Generate an Alembic migration that creates the `missions` table with integrity constraints.

Deliverables

* `src/app/models/mission.py` exporting `Mission` and `MissionStatus` plus helper methods.
* `src/app/models/__init__.py` re-export updated domain objects.
* `src/app/schemas/mission.py` with create/update/read contracts and status validation helpers.
* Alembic migration adding the `missions` table and schedule check constraint.
* Tests covering mission persistence, uniqueness, scheduling guards, and status transitions.

Validation

* CI: all guards, lints, tests green.
* Include the exact line below in the PR that completes this step:
  Ref: docs/roadmap/step-04.md
* New tests prove the transition matrix and constraint behaviour.

Notes

* Keep scripts Windows-friendly; prefer PowerShell for developer utilities when scripting is required.
