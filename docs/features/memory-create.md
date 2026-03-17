# Memory Create

## Purpose

Capture a new memory inside an explicit vault.

## Command

```text
python -m keepsake memory create --vault <vault_id>
```

## Runtime Boundary

- personal mode only
- uses the resolved personal runtime profile
- does not touch demo mode

## Behavior

- reads memory content from stdin
- uses the first non-empty line as the title
- calls `create_memory`
- creates the initial revision
- prints memory id, revision number, vault id, and vault name

## Notes

- memory content must not be empty
- the vault must exist and belong to `owner-self`

## Not Included

- templates
- advanced metadata capture
- auto-assignment to a default vault
- separate title prompt
