# Memory History

## Purpose

Understand how a memory changed over time.

## Command

```text
python -m keepsake memory history <memory_id>
```

## Runtime Boundary

- personal mode only
- reads from the resolved personal runtime profile
- does not touch demo mode

## Behavior

- lists revision numbers and timestamps in ascending revision order
- reads append-only history without changing any memory state

## Notes

- the current implementation lists the full revision timeline only
- specific revision lookup is not implemented in Phase 1

## Not Included

- diff views
- bulk exports
- timeline-wide analytics
- `--rev <n>` support
