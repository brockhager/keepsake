from __future__ import annotations

from ..runtime_profile import RuntimeProfile
from ..sqlite_profile_connection import transaction
from ._helpers import insert_audit_event, new_id, utc_now


def grant_share(
    profile: RuntimeProfile,
    *,
    granted_by: str,
    request_id: str,
    max_revision_id: str | None = None,
    accepted_at: str | None = None,
) -> dict[str, str | int]:
    grant_id = new_id("grant")

    with transaction(profile) as connection:
        request_row = connection.execute(
            """
            SELECT id, memory_id, person_id, status, decided_at
            FROM share_request
            WHERE id = ?
            """,
            (request_id,),
        ).fetchone()

        if request_row is None:
            raise ValueError(f"share request not found: {request_id}")

        memory_id = request_row["memory_id"]
        person_id = request_row["person_id"]
        request_status = request_row["status"]

        decided_at = accepted_at or request_row["decided_at"] or utc_now()

        if request_status == "pending":
            connection.execute(
                """
                UPDATE share_request
                SET status = 'accepted', decided_at = ?
                WHERE id = ?
                """,
                (decided_at, request_id),
            )
        elif request_status != "accepted":
            raise ValueError(
                f"share request cannot be granted from status '{request_status}': {request_id}"
            )

        if max_revision_id is None:
            revision_row = connection.execute(
                """
                SELECT mr.id AS revision_id, mr.revision_number
                FROM memory m
                JOIN memory_revision mr ON mr.id = m.current_revision_id
                WHERE m.id = ?
                """,
                (memory_id,),
            ).fetchone()
        else:
            revision_row = connection.execute(
                """
                SELECT mr.id AS revision_id, mr.revision_number
                FROM memory_revision mr
                WHERE mr.id = ?
                  AND mr.memory_id = ?
                """,
                (max_revision_id, memory_id),
            ).fetchone()

        if revision_row is None:
            raise ValueError(
                "unable to resolve grant revision bound for request "
                f"{request_id} on memory {memory_id}"
            )

        resolved_max_revision_id = revision_row["revision_id"]
        max_revision_number = int(revision_row["revision_number"])

        connection.execute(
            """
            INSERT INTO share_grant (
              id,
              memory_id,
              person_id,
              request_id,
              granted_at,
              revoked_at,
              max_revision_id,
              max_revision_number
            )
            VALUES (?, ?, ?, ?, ?, NULL, ?, ?)
            """,
            (
                grant_id,
                memory_id,
                person_id,
                request_id,
                decided_at,
                resolved_max_revision_id,
                max_revision_number,
            ),
        )

        insert_audit_event(
            connection,
            actor_type="owner",
            actor_id=granted_by,
            event_type="share.accepted",
            entity_type="share_request",
            entity_id=request_id,
            payload={
                "grant_id": grant_id,
                "memory_id": memory_id,
                "person_id": person_id,
                "max_revision_id": resolved_max_revision_id,
                "max_revision_number": max_revision_number,
            },
        )

    return {
        "grant_id": grant_id,
        "memory_id": memory_id,
        "person_id": person_id,
        "max_revision_id": resolved_max_revision_id,
        "max_revision_number": max_revision_number,
    }
