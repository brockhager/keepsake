from __future__ import annotations

from ..runtime_profile import RuntimeProfile
from ..sqlite_profile_connection import transaction
from ._helpers import insert_audit_event, utc_now


def revoke_share(
    profile: RuntimeProfile,
    *,
    revoked_by: str,
    grant_id: str,
    revoked_at: str | None = None,
) -> dict[str, str]:
    resolved_revoked_at = revoked_at or utc_now()

    with transaction(profile) as connection:
        grant_row = connection.execute(
            """
            SELECT memory_id, person_id, revoked_at
            FROM share_grant
            WHERE id = ?
            """,
            (grant_id,),
        ).fetchone()

        if grant_row is None:
            raise ValueError(f"share grant not found: {grant_id}")

        if grant_row["revoked_at"] is not None:
            raise ValueError(f"share grant is already revoked: {grant_id}")

        connection.execute(
            """
            UPDATE share_grant
            SET revoked_at = ?
            WHERE id = ?
            """,
            (resolved_revoked_at, grant_id),
        )

        insert_audit_event(
            connection,
            actor_type="owner",
            actor_id=revoked_by,
            event_type="share.revoked",
            entity_type="share_grant",
            entity_id=grant_id,
            payload={
                "memory_id": grant_row["memory_id"],
                "person_id": grant_row["person_id"],
                "revoked_at": resolved_revoked_at,
            },
        )

    return {"grant_id": grant_id, "revoked_at": resolved_revoked_at}
