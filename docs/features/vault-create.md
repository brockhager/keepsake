# Vault Create

## Purpose

Create a new vault for organizing memories.

## Command

```text
python -m keepsake vault create <name>
```

## Runtime Boundary

- personal mode only
- uses the resolved personal runtime profile
- does not touch demo mode

## Behavior

- calls `create_vault`
- creates one explicit vault owned by `owner-self`
- prints vault id, vault name, and created timestamp

## Notes

- vault names are trimmed before creation
- a blank name fails

## Not Included

- rename
- delete
- default-vault behavior beyond explicit creation
- auto-sharing
