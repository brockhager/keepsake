# Keepsake Runtime Mode Contract (v0)

## Purpose

Keepsake runs in two modes using one codebase and one schema:

- personal
- demo

This is a runtime boundary, not a product fork.

## Non-negotiable guarantee

The demo mode must be incapable of reading personal data by construction.

This guarantee is implemented through separate storage roots, separate database files, and separate mode metadata.

## Mode definition

Runtime mode is selected at startup and is immutable for that process.

Allowed values:

- personal
- demo

Invalid values must fail closed (startup error).

## Storage separation

Default data root:

- `~/.keepsake`

Resolved profile roots:

- personal: `~/.keepsake/personal`
- demo: `~/.keepsake/demo`

Per-profile paths:

- database: `<profile-root>/keepsake.db`
- attachments: `<profile-root>/attachments`
- exports: `<profile-root>/exports`
- mode metadata: `<profile-root>/profile.json`

No mode may read or write another mode's profile root.

## Behavior contract

### Personal mode

- No demo seed data.
- Network calls disabled by default.
- Analytics/telemetry disabled by default.
- All operations local-first.

### Demo mode

- Deterministic synthetic seed data is allowed.
- Demo profile can be reset safely.
- Same schema and invariants as personal mode.

## Composition rule

Mode affects application composition only.

Mode-specific adapters are allowed for:

- storage path resolution
- seeding
- export destination
- outbound networking policy

Domain behavior is shared across modes.

Do not scatter mode conditionals through domain logic.

## Forbidden patterns

- Shared database path between modes.
- Runtime toggle from personal to demo inside one process.
- Demo seeding in personal mode.
- Any fallback that auto-opens personal storage when demo storage is missing.

## Testable acceptance checks

1. Personal and demo database files are different absolute paths.
2. Initializing demo mode creates synthetic data; personal mode does not.
3. Resetting demo mode cannot modify personal database files.
4. Existing schema invariants (append-only revisions, bounded sharing) hold in both modes.

## Current implementation artifacts

- Profile initialization script: `scripts/init-runtime-profile.ps1`
- Demo seed SQL: `db/seeds/demo_seed_v0.sql`
- Schema migrations: `db/migrations/*`
- Runtime profile resolver: `keepsake/runtime_profile.py`
- Runtime mode process guard: `keepsake/sqlite_profile_connection.py`
- Flow and guard tests: `tests/test_service_layer_flow.py`, `tests/test_runtime_mode_guard.py`
