# Keepsake

Keepsake is a personal memory archive.

It exists to help an individual store, revisit, and understand their own memories over time — without relying on social sharing, feeds, or external validation.

## What Keepsake Is

- A private-first archive for memory
- Built for future-you
- Designed to last decades
- Calm, intentional, and non-performative
- Useful even if no one else ever joins

Keepsake treats memory as something that evolves, not something that needs to be optimized or shared.

## What Keepsake Is Not

- Not a social network
- Not a feed
- Not a genealogy platform
- Not a productivity system
- Not optimized for engagement or growth

Sharing, if it exists at all, is explicit, object-level, and optional.

## Core Principles

- Nothing is shared by default
- No data is captured without consent
- History is preserved; nothing is silently overwritten
- Context matters more than correctness
- The system must remain useful even in complete isolation

## Status

Keepsake is in early development.
The initial focus is on a minimal, trustworthy foundation.

Features will be added slowly and intentionally.

## Design Notes

- [v0 Core Data Model](docs/v0-core-data-model.md)
- [Phased Build Plan](docs/phased-build-plan.md)
- [Runtime Mode Contract (v0)](docs/runtime-mode-spec.md)
- [v0 Service Layer Scope](docs/v0-service-layer.md)
- [v0 Vault Scope](docs/v0-vaults.md)
- [v0 SQLite Migrations](db/migrations/README.md)
- [Demo Seed Data](db/seeds/README.md)

## Phase 1 CLI

Initialize the personal profile before using the CLI:

```powershell
pwsh .\scripts\init-runtime-profile.ps1 -RuntimeMode personal
```

The implemented Phase 1 command tree is:

```text
keepsake vault create <name>
keepsake vault list
keepsake memory create --vault <vault_id>
keepsake memory revise <memory_id>
keepsake memory show <memory_id>
keepsake memory history <memory_id>
```

Within this repository, invoke it as `python -m keepsake ...`.

For the two write commands, memory content is read from stdin. The first non-empty line is stored as the revision title so Phase 1 can stay inside the existing service-layer shape without adding separate metadata prompts.

## License

Apache License 2.0
