# Vault List

## Purpose

List existing vaults in personal mode.

## Command

```text
python -m keepsake vault list
```

## Runtime Boundary

- personal mode only
- reads from the resolved personal runtime profile
- does not touch demo mode

## Behavior

- shows vault id, name, and created timestamp
- uses a stable sort order: name ascending, then id ascending
- lists only vaults owned by `owner-self`

## Not Included

- rename
- delete
- filtering
- search
