# Keepsake v0 Core Data Model

## Why this focus

The data model is the highest leverage v0 decision.
If identity, history, and sharing semantics are right, UI and stack can change later without losing trust.

## Design targets

This model is designed to enforce these constraints in storage, not just in UI:

- Private by default.
- No feed, discovery, or public visibility.
- Sharing is explicit, object-level, one-to-one, and request-based.
- "Tag person" means "request visibility," not "person appears in memory."
- No silent overwrite; history is preserved.
- AI can assist retrieval and indexing, but cannot assert truth or expand sharing.

## Modeling strategy

Use two layers:

1. Stable objects:
- Vault
- Memory
- Person
- Share grant

2. Immutable records:
- Memory revisions
- Share requests
- Audit events

This keeps identity stable while preserving evolution over time.

## Core entities

### 1) vault

Represents a user-owned isolation boundary for memories.

Fields:
- id (ULID or UUID)
- owner_id
- name
- created_at
- is_default

Rules:
- A vault belongs to exactly one owner.
- Memories never exist outside a vault.
- Vaults do not create a second permission system.

### 2) memory

Represents one memory as a stable identity.

Fields:
- id (ULID or UUID)
- owner_id
- vault_id
- created_at
- archived_at (nullable)
- current_revision_id (pointer for fast reads)

Notes:
- No content fields here.
- Content lives in immutable revisions.
- `vault_id` defines the memory's isolation boundary.

### 3) memory_revision

Immutable snapshot of a memory at a point in time.

Fields:
- id
- memory_id
- revision_number (monotonic per memory)
- created_at
- author_type ("owner" | "ai_suggestion" | "import")
- title
- body
- happened_at_start (nullable)
- happened_at_end (nullable)
- time_precision ("exact" | "day" | "month" | "year" | "unknown")
- certainty ("certain" | "uncertain" | "speculative")
- belief_context (what past-me believed at the time)
- edit_reason (nullable)
- supersedes_revision_id (nullable)

Rules:
- Never update existing rows.
- Any edit creates a new revision.
- Old revisions remain addressable forever.

### 4) person

A private contact identity used for optional one-to-one sharing.

Fields:
- id
- owner_id
- display_name
- contact_hint (nullable: email, username, etc.)
- notes_private (nullable)
- created_at
- archived_at (nullable)

Notes:
- A person can exist without any sharing relationship.

### 5) memory_visibility_intent

Represents the meaning of "tagging" a person.

Fields:
- id
- memory_id
- person_id
- source_revision_id
- intent_type ("request_view")
- created_at
- canceled_at (nullable)

Rule:
- This table does not grant access.
- It records owner intent to request access for a person.

### 6) share_request

Explicit request workflow for one memory and one person.

Fields:
- id
- memory_id
- person_id
- direction ("owner_to_person" | "person_to_owner")
- requested_by
- requested_at
- message (nullable)
- status ("pending" | "accepted" | "declined" | "canceled" | "expired")
- decided_at (nullable)

Rules:
- Object-level only: one request references exactly one memory.
- One-to-one only: one request references exactly one person.

### 7) share_grant

Actual permission created only from an accepted request.

Fields:
- id
- memory_id
- person_id
- request_id
- granted_at
- revoked_at (nullable)
- max_revision_id
- max_revision_number

Key trust rule:
- Grants are revision-bounded and anchored to a specific revision ID.
- If memory gets a new revision later, it is not auto-shared.
- Owner must explicitly create a new request/grant for expanded scope.

### 8) attachment

Optional file attached to a specific revision.

Fields:
- id
- memory_revision_id
- media_type
- file_path (or blob_key)
- sha256
- captured_at (nullable)
- created_at

Rule:
- Attachments are revision-scoped to preserve historical context.

### 9) audit_event

Append-only ledger for trust and recoverability.

Fields:
- id
- occurred_at
- actor_type ("owner" | "person" | "system" | "ai")
- actor_id (nullable)
- event_type
- entity_type
- entity_id
- payload_json

Use for:
- memory.created
- memory.revised
- share.requested
- share.accepted
- share.revoked
- ai.index.updated

## Invariants (must always hold)

1. Private default:
- No row in share_grant means no access, regardless of tags or requests.

2. Vault containment:
- Every memory must have a vault_id.
- A memory's vault must belong to the same owner as the memory.

3. History preservation:
- memory_revision rows are immutable.
- "Delete" is modeled as archive/tombstone, not destructive overwrite.

4. Tagging semantics:
- memory_visibility_intent cannot be interpreted as appearance, identity, or consent.
- It only means: owner wants this person to be able to view this memory.

5. Sharing boundaries:
- share_grant scope is one memory, one person, and a bounded revision ceiling.
- No automatic expansion to other memories or future revisions.

6. AI limits:
- AI-produced text is stored as suggestion/provenance metadata.
- AI cannot directly mutate canonical memory content without explicit owner action.
- AI cannot create or expand share_grant.

## Minimal query model

For fast UI reads in a local-first client:

- memory_current_view:
  - memory + vault summary + latest revision summary + share state count
- memory_history_view:
  - full ordered revisions for one memory
- person_shares_view:
  - memories shared with one person and revision bounds

These can be SQL views or app-level projections.

## Recommended local-first persistence for v0

Keep this simple and reversible:

- SQLite for relational data.
- Flat files for attachment blobs (content-addressed by sha256).
- Optional encryption at rest via OS keychain-managed key.
- Export format: newline-delimited JSON events + attachment manifest.

This supports a single-user default while keeping migration paths open.

## Example lifecycle

1. Owner creates vault V1.
2. Owner creates memory M1 inside V1 -> memory + revision 1.
3. Owner edits context later -> revision 2 (revision 1 remains).
4. Owner tags person P1 -> memory_visibility_intent row only.
5. Owner sends request for M1 to P1 -> share_request pending.
6. P1 accepts -> share_grant created with max_revision_id = R2 and max_revision_number = 2.
7. Owner writes revision 3 later -> P1 does not see revision 3 by default.

This sequence preserves trust and avoids silent sharing drift.

## What this unlocks next

With this model in place, the team can safely build:

- v0 three-pane UI over memory_current_view and memory_history_view.
- explicit share-request screens without social surface area.
- AI recall features that read from history without rewriting it.

All while preserving your core promise: future-me can understand past-me without performance pressure or accidental exposure.
