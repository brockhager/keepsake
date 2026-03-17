# Keepsake Phased Build Plan

## Guiding Rule

Each phase must be independently useful to future-you, even if no later phase is ever built.

## Phase 0 - Foundation

Status: complete and closed.

This phase established:

- append-only memory and revision history
- audit trail
- personal and demo runtime separation
- vault isolation boundaries
- minimal service-layer operations
- seeded demo data and invariant tests

Stop condition: reached.
Do not add more foundation features in this phase.

## Phase 1 - Personal Use Loop

Goal: make Keepsake usable by the owner without UI ambition.

Execution checklist:

- See `docs/phase-1-cli-checklist.md` for the exact Phase 1 CLI boundary.

Allowed work:

- tiny CLI or script interface only
- create vault
- list vaults
- create memory in a vault
- add revision
- view memory history

Not in phase:

- sharing UI
- AI behavior
- networking or sync
- broader retrieval features
- UI polish

Stop condition:

- real memories have been added in personal mode for a few weeks
- at least one recall win happened
- at least one concrete friction point has been observed
- the CLI has not expanded beyond the checklist

## Phase 2 - Retrieval And Recall

Goal: help future-you re-enter past-you's thinking.

Allowed work:

- search by text
- list memories by vault
- clearer revision timeline display
- narrow read-only recall workflows

Not in phase:

- AI generation
- sharing expansion
- complex UI branching

Stop condition:

- a real question about the past can be answered from Keepsake alone

## Phase 3 - Gentle AI As Index

Goal: surface memories without changing trust boundaries.

Allowed work:

- find related memories
- surface contradictions or stale beliefs
- ask clarifying questions

Not in phase:

- writing memories automatically
- collapsing uncertainty into certainty
- expanding sharing
- crossing vault boundaries

Stop condition:

- AI output is clearly helpful without changing why the result appeared or what remains private

## Phase 4 - Selective Sharing

Goal: enable intentional sharing without changing the system's nature.

Allowed work:

- explicit, one-to-one, auditable, revocable sharing built on existing memory-level semantics

Not in phase:

- making sharing central to the product
- group sharing
- role systems

Stop condition:

- sharing remains optional and the product is still fully useful without it

## Phase 5 - Long-Term Durability

Goal: make Keepsake survive decades of use.

Examples:

- export formats
- migration guarantees
- encryption key rotation
- cold storage strategies

## Current Do-Not-Cross Line

For current work, do not add:

- vault sharing
- vault roles
- default vault auto-sharing
- UI flows for switching vaults
- smart vault behavior
- network APIs or sync
- AI authoring or orchestration

If the work does not directly support the current phase goal, stop.