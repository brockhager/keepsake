from __future__ import annotations

from ..runtime_profile import RuntimeProfile
from ..sqlite_profile_connection import transaction
from ._helpers import insert_audit_event, new_id


def create_vault(
    profile: RuntimeProfile,
    *,
    owner_id: str,
    name: str,
    is_default: bool = False,
) -> dict[str, str | bool]:
    normalized_name = name.strip()
    if not normalized_name:
        raise ValueError("vault name cannot be empty")

    vault_id = new_id("vault")

    with transaction(profile) as connection:
        connection.execute(
            """
            INSERT INTO vault (id, owner_id, name, is_default)
            VALUES (?, ?, ?, ?)
            """,
            (vault_id, owner_id, normalized_name, 1 if is_default else 0),
        )

        insert_audit_event(
            connection,
            actor_type="owner",
            actor_id=owner_id,
            event_type="vault.created",
            entity_type="vault",
            entity_id=vault_id,
            payload={"name": normalized_name, "is_default": is_default},
        )

    return {"vault_id": vault_id, "name": normalized_name, "is_default": is_default}
