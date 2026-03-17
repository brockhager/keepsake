# Phase 1 CLI Checklist

## Purpose

Make Keepsake usable by a single individual through a minimal CLI, without adding new domain concepts or expanding the product surface.

## Hard Constraints

- No UI
- No networking
- No AI
- No sharing expansion
- No vault sharing
- No new domain concepts
- Must work entirely in personal runtime mode
- Demo mode remains untouched

## Exact Command Surface

Only the following commands are in scope for Phase 1.

### 1. `keepsake vault create <name>`

Purpose:

- create a new vault for organizing memories

Behavior:

- calls `create_vault`
- prints vault id, vault name, and created timestamp

Out of scope here:

- default behavior beyond explicit creation
- auto-sharing
- rename or delete

### 2. `keepsake vault list`

Purpose:

- list existing vaults

Behavior:

- shows vault id, name, and created timestamp
- choose one stable sort order and keep it consistent

Out of scope here:

- delete
- rename
- filtering or search

### 3. `keepsake memory create --vault <vault_id>`

Purpose:

- capture a new memory inside an explicit vault

Behavior:

- prompts for memory content through stdin or a simple editor flow
- calls `create_memory`
- creates the initial revision
- prints memory id, revision number, and vault information

Out of scope here:

- templates
- advanced metadata capture
- auto-assignment to a default vault

### 4. `keepsake memory revise <memory_id>`

Purpose:

- append a new revision to an existing memory

Behavior:

- prompts for new content
- calls `add_revision`
- prints memory id, new revision number, and timestamp

Out of scope here:

- edit in place
- overwrite
- revision deletion

### 5. `keepsake memory show <memory_id>`

Purpose:

- read the current state of a memory

Behavior:

- shows current revision content
- shows vault name
- shows created and last revised timestamps

Out of scope here:

- rich formatting
- AI summaries
- search from this command

### 6. `keepsake memory history <memory_id>`

Purpose:

- understand how a memory changed over time

Behavior:

- lists revision numbers and timestamps
- may optionally support `--rev <n>` for showing a specific revision

Out of scope here:

- diff views
- bulk exports
- timeline-wide analytics

## Explicitly Out Of Scope For Phase 1 CLI

- Search
- Tags
- Sharing commands
- Vault switching defaults
- Bulk operations
- Config files
- Background processes
- Interactive TUI
- Editor plugins

If a proposed command feels merely convenient, it is out of scope.

## Done Criteria

Phase 1 is complete when all of the following are true:

- a vault can be created
- vaults can be listed
- a real memory can be added to a vault
- that memory can be revised later
- the current version can be read
- revision history can be viewed
- real personal use has happened in personal mode
- no new domain concepts were introduced

At that point, stop coding and evaluate actual usage friction before adding more.