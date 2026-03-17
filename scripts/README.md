# Keepsake Scripts

## init-runtime-profile.ps1

Initializes a profile-specific SQLite database and folder layout.

Usage:

```powershell
pwsh .\scripts\init-runtime-profile.ps1 -RuntimeMode personal
pwsh .\scripts\init-runtime-profile.ps1 -RuntimeMode demo
```

Optional parameters:

- `-DataRoot <path>`: override default root (`$HOME/.keepsake`).
- `-Reset`: recreate the target profile database.

Safety behavior:

- Personal and demo profiles always use separate folders.
- Demo mode applies synthetic seed data.
- Personal mode never applies demo seed data.
- Existing profile DB is left untouched unless `-Reset` is provided.
