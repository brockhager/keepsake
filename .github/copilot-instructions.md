# Keepsake Project Guidelines

## Product Intent

- Keepsake is a private-first personal memory archive built for future-you.
- Optimize for trust, calm, longevity, and reversibility over feature breadth.
- Prefer explicit user control over automation.
- Do not add feeds, discovery, public visibility, growth mechanics, engagement loops, or speculative "AI magic" unless explicitly requested.

## Architecture

- Treat these docs as the source of truth for architectural decisions:
  - `docs/v0-core-data-model.md`
  - `docs/runtime-mode-spec.md`
  - `docs/v0-service-layer.md`
  - `docs/v0-vaults.md`
- Preserve append-only history. Memory content lives in immutable `memory_revision` rows; do not silently overwrite or collapse history.
- Every memory must belong to a vault. Vaults are isolation boundaries, not a second permission system.
- Sharing remains object-level, one-to-one, and revision-bounded. Reuse existing `share_request` and `share_grant` semantics instead of inventing parallel access models.
- Runtime mode is resolved at the application boundary. Domain operations must consume a resolved `RuntimeProfile` and must not infer or switch runtime mode internally.
- Personal and demo modes must remain physically separated. Never add code paths that can open both databases in the same process.

## Implementation Conventions

- Keep v0 scope tight. Build only what directly supports: create a vault, create a memory, revise it, retrieve it, request share, grant share, and revoke share.
- Prefer direct, inspectable code over speculative abstractions. Avoid adding generic repository layers, event buses, CQRS, policy engines, sync engines, or multi-user ownership models unless explicitly requested.
- For service-layer work, prefer one operation per file under `keepsake/operations/`.
- State-changing domain operations should use a local SQLite transaction and write an `audit_event`.
- Keep migrations explicit and reversible. Validate both up and down migrations against populated data when changing the schema.

## Build And Test

- Run `python -m unittest discover -s tests -v` after Python changes.
- Use `pwsh .\scripts\init-runtime-profile.ps1 -RuntimeMode personal` and `pwsh .\scripts\init-runtime-profile.ps1 -RuntimeMode demo` when validating profile initialization behavior.
- Apply SQLite migrations in numeric order from `db/migrations/`.

## Out Of Scope By Default

- Vault sharing workflows beyond the current vault foundation
- Network APIs, sync, or background services
- AI orchestration layers
- Family tree or genealogy features
- Role systems, ACL matrices, or collaborative editing

## Documentation

- Update the relevant design docs when domain invariants, runtime boundaries, or service-layer scope changes.
- Prefer linking to design docs instead of duplicating long architectural rationale in code comments.