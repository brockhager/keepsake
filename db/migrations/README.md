# Keepsake v0 SQLite Migrations

These migrations are intentionally small and explicit.
They establish a trust-first local schema with append-only history and bounded sharing.

## Files

- 0001_initial_schema.up.sql
- 0001_initial_schema.down.sql
- 0002_invariants_and_views.up.sql
- 0002_invariants_and_views.down.sql
- 0003_vault_foundation.up.sql
- 0003_vault_foundation.down.sql

## Apply migrations

From the repository root:

```powershell
sqlite3 .\keepsake.db ".read .\db\migrations\0001_initial_schema.up.sql"
sqlite3 .\keepsake.db ".read .\db\migrations\0002_invariants_and_views.up.sql"
sqlite3 .\keepsake.db ".read .\db\migrations\0003_vault_foundation.up.sql"
```

## Roll back migrations

Roll back in reverse order:

```powershell
sqlite3 .\keepsake.db ".read .\db\migrations\0003_vault_foundation.down.sql"
sqlite3 .\keepsake.db ".read .\db\migrations\0002_invariants_and_views.down.sql"
sqlite3 .\keepsake.db ".read .\db\migrations\0001_initial_schema.down.sql"
```

## Notes

- Timestamps are stored as UTC ISO-8601 TEXT.
- IDs are TEXT to support UUID or ULID.
- `memory_revision` and `audit_event` are append-only via triggers.
- `share_grant` requires an accepted `share_request` and is bound to a specific maximum revision ID and number.
- `memory` rows are required to belong to a `vault` after the vault foundation migration.

## Mode-aware initialization

Use the runtime profile script to enforce separated personal and demo paths:

```powershell
pwsh .\scripts\init-runtime-profile.ps1 -RuntimeMode personal
pwsh .\scripts\init-runtime-profile.ps1 -RuntimeMode demo
```

Use `-Reset` only when recreating a profile intentionally.
