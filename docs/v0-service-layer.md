# Keepsake v0 Service Layer Scope

This document defines the intentionally narrow v0 execution surface.

## Scope boundary

The v0 service layer only supports this user outcome:

- create a vault
- store a memory
- revise it later
- retrieve history
- optionally share one memory revision with one person
- revoke that share

If a change does not directly support this flow, it is out of scope for v0.

## Implemented operations

Each operation accepts a resolved runtime profile and executes a local SQLite transaction.

1. `create_vault(profile, ...)`
2. `create_memory(profile, vault_id=..., ...)`
3. `add_revision(profile, ...)`
4. `request_share(profile, ...)`
5. `grant_share(profile, ...)`
6. `revoke_share(profile, ...)`

## Runtime boundary

- Domain operations do not decide runtime mode.
- Runtime mode is resolved before operations are called.
- The process-level guard blocks opening both personal and demo modes in one process.
- Memory creation requires an explicit vault.

## Explicitly out of scope for this phase

- Generic repository abstraction layers
- Event buses or CQRS
- Network APIs and sync
- AI orchestration
- Family/genealogy features
- Multi-user account systems

## Code locations

- Runtime profile resolver: `keepsake/runtime_profile.py`
- Runtime mode DB guard: `keepsake/sqlite_profile_connection.py`
- Operations: `keepsake/operations/`
- Flow/invariant tests: `tests/`
