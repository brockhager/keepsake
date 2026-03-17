# Keepsake v0 Vault Scope

Vaults are the unit of isolation in Keepsake v0.

## Core rule

A vault is a user-owned container that groups memories and defines a sharing boundary.
Memories never exist outside a vault.

## v0 model

- One owner per vault.
- Many memories per vault.
- No nested vaults.
- No roles or ACL system.
- No new permission model.

## v0 implementation boundary

The current vault foundation adds:

1. `vault` table.
2. `memory.vault_id` foreign key.
3. `create_vault(profile, ...)` operation.
4. `create_memory(profile, vault_id=..., ...)` requirement.

## Guardrails

- Vaults do not nest.
- Vaults do not change revision semantics.
- Vaults do not create group sharing.
- Vault sharing, if added later, must compose from existing memory-level share requests and grants.

## Not in scope yet

- Vault sharing workflows.
- Vault roles or policies.
- Cross-vault search behavior.
- UI for switching or managing vaults.
