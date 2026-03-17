from __future__ import annotations

from ..runtime_profile import RuntimeProfile
from ..sqlite_profile_connection import transaction
from ._helpers import insert_audit_event, new_id


def request_share(
    profile: RuntimeProfile,
    *,
    requested_by: str,
    memory_id: str,
    person_id: str,
    source_revision_id: str | None = None,
    message: str | None = None,
) -> dict[str, str]:
    intent_id = new_id("intent")
    request_id = new_id("request")

    with transaction(profile) as connection:
        if source_revision_id is None:
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

            source_revision_id = memory_row["current_revision_id"]

        if source_revision_id is None:
            raise ValueError(f"memory has no current revision to request sharing: {memory_id}")

        connection.execute(
            """
            INSERT INTO memory_visibility_intent (
              id,
              memory_id,
              person_id,
              source_revision_id,
              intent_type
            )
            VALUES (?, ?, ?, ?, 'request_view')
            """,
            (intent_id, memory_id, person_id, source_revision_id),
        )

        connection.execute(
            """
            INSERT INTO share_request (
              id,
              memory_id,
              person_id,
              direction,
              requested_by,
              message,
              status,
              decided_at
            )
            VALUES (?, ?, ?, 'owner_to_person', ?, ?, 'pending', NULL)
            """,
            (request_id, memory_id, person_id, requested_by, message),
        )

        insert_audit_event(
            connection,
            actor_type="owner",
            actor_id=requested_by,
            event_type="share.requested",
            entity_type="share_request",
            entity_id=request_id,
            payload={
                "memory_id": memory_id,
                "person_id": person_id,
                "source_revision_id": source_revision_id,
                "visibility_intent_id": intent_id,
            },
        )

    return {
        "request_id": request_id,
        "visibility_intent_id": intent_id,
        "source_revision_id": source_revision_id,
    }
