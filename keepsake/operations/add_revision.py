from __future__ import annotations

from ..runtime_profile import RuntimeProfile
from ..sqlite_profile_connection import transaction
from ._helpers import insert_audit_event, new_id


def add_revision(
    profile: RuntimeProfile,
    *,
    owner_id: str,
    memory_id: str,
    title: str,
    body: str,
    happened_at_start: str | None = None,
    happened_at_end: str | None = None,
    time_precision: str = "unknown",
    certainty: str = "uncertain",
    belief_context: str | None = None,
    edit_reason: str | None = None,
) -> dict[str, str | int]:
    revision_id = new_id("revision")

    with transaction(profile) as connection:
        memory_row = connection.execute(
            """
            SELECT current_revision_id
            FROM memory
            WHERE id = ?
            """,
            (memory_id,),
        ).fetchone()

        if memory_row is None:
            raise ValueError(f"memory not found: {memory_id}")

        previous_revision_id = memory_row["current_revision_id"]
        if previous_revision_id is None:
            raise ValueError(f"memory has no current revision: {memory_id}")

        revision_row = connection.execute(
            """
            SELECT revision_number
            FROM memory_revision
            WHERE id = ?
            """,
            (previous_revision_id,),
        ).fetchone()

        if revision_row is None:
            raise ValueError(
                f"current revision does not exist for memory {memory_id}: {previous_revision_id}"
            )

        revision_number = int(revision_row["revision_number"]) + 1

        connection.execute(
            """
            INSERT INTO memory_revision (
              id,
              memory_id,
              revision_number,
              author_type,
              title,
              body,
              happened_at_start,
              happened_at_end,
              time_precision,
              certainty,
              belief_context,
              edit_reason,
              supersedes_revision_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                revision_id,
                memory_id,
                revision_number,
                "owner",
                title,
                body,
                happened_at_start,
                happened_at_end,
                time_precision,
                certainty,
                belief_context,
                edit_reason,
                previous_revision_id,
            ),
        )

        connection.execute(
            """
            UPDATE memory
            SET current_revision_id = ?
            WHERE id = ?
            """,
            (revision_id, memory_id),
        )

        insert_audit_event(
            connection,
            actor_type="owner",
            actor_id=owner_id,
            event_type="memory.revised",
            entity_type="memory",
            entity_id=memory_id,
            payload={
                "revision_id": revision_id,
                "revision_number": revision_number,
                "supersedes_revision_id": previous_revision_id,
            },
        )

    return {
        "memory_id": memory_id,
        "revision_id": revision_id,
        "revision_number": revision_number,
    }
