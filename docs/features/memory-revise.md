# Memory Revise

## Purpose

Append a new revision to an existing memory.

## Command

```text
python -m keepsake memory revise <memory_id>
```

## Runtime Boundary

- personal mode only
- uses the resolved personal runtime profile
- does not touch demo mode

## Behavior

- reads revision content from stdin
- uses the first non-empty line as the title
- calls `add_revision`
- appends a new revision without overwriting prior history
- prints memory id, new revision number, and revision timestamp

## Notes

- revision content must not be empty
- the target memory must already exist

## Not Included

- edit in place
- overwrite
- revision deletion
