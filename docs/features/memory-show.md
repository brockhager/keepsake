# Memory Show

## Purpose

Read the current state of a memory.

## Command

```text
python -m keepsake memory show <memory_id>
```

## Runtime Boundary

- personal mode only
- reads from the resolved personal runtime profile
- does not touch demo mode

## Behavior

- shows current revision content
- shows vault name
- shows created timestamp and last revised timestamp
- reads from the current memory and revision state without changing history

## Not Included

- rich formatting
- AI summaries
- search from this command
