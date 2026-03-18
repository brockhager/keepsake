# Memory List

## Purpose

Reduce recall friction by listing current memories globally or within one explicit vault.

## Command

```text
python -m keepsake memory list [--vault <vault_id>]
```

## Runtime Boundary

- personal mode only
- reads from the resolved personal runtime profile
- does not touch demo mode

## Behavior

- lists memories without changing any state
- supports a global list across all vaults
- supports narrowing the list to one explicit vault with `--vault <vault_id>`
- shows memory id, current title, vault id, vault name, current revision number, and last revised timestamp
- orders results by most recently revised first, then by original memory creation time, then by memory id

## Notes

- an unknown vault id fails instead of returning a silent empty result
- an empty result set prints a simple no-memories message

## Not Included

- full-text search
- filters beyond one explicit vault
- content previews
- AI recall or summarization
