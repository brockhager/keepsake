# Keepsake Demo Seeds

Seed files in this folder are synthetic-only and intended for demo mode profiles.

## Files

- demo_seed_v0.sql

## Requirements

- Apply schema migrations before running seed files.
- Never run demo seeds against a personal profile database.
- Demo seeds are deterministic and disposable.

## Apply seed manually

```powershell
sqlite3 .\keepsake.db ".read .\db\seeds\demo_seed_v0.sql"
```

Use `scripts/init-runtime-profile.ps1` for safer mode-aware initialization.
