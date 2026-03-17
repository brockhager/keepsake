from __future__ import annotations

from ..runtime_profile import RuntimeProfile
from ..sqlite_profile_connection import transaction
from ._helpers import insert_audit_event, new_id


def create_memory(
    profile: RuntimeProfile,
    *,
    owner_id: str,
    vault_id: str,
    title: str,
    body: str,
    happened_at_start: str | None = None,
    happened_at_end: str | None = None,
    time_precision: str = "unknown",
    certainty: str = "uncertain",
    belief_context: str | None = None,
    edit_reason: str | None = "Initial capture",
) -> dict[str, str]:
    memory_id = new_id("memory")
    revision_id = new_id("revision")

    with transaction(profile) as connection:
        vault_row = connection.execute(
            """
            SELECT owner_id
            FROM vault
            WHERE id = ?
            """,
            (vault_id,),
        ).fetchone()

        if vault_row is None:
            raise ValueError(f"vault not found: {vault_id}")

        if vault_row["owner_id"] != owner_id:
            raise ValueError(f"vault does not belong to owner {owner_id}: {vault_id}")

        connection.execute(
            """
            INSERT INTO memory (id, owner_id, vault_id, current_revision_id)
            VALUES (?, ?, ?, NULL)
            """,
            (memory_id, owner_id, vault_id),
        )

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
                1,
                "owner",
                title,
                body,
                happened_at_start,
                happened_at_end,
                time_precision,
                certainty,
                belief_context,
                edit_reason,
                None,
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
            event_type="memory.created",
            entity_type="memory",
            entity_id=memory_id,
            payload={"initial_revision_id": revision_id, "vault_id": vault_id},
        )

    return {"memory_id": memory_id, "revision_id": revision_id, "vault_id": vault_id}
