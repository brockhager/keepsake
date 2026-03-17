from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex}"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def insert_audit_event(
    connection: Any,
    *,
    actor_type: str,
    actor_id: str,
    event_type: str,
    entity_type: str,
    entity_id: str,
    payload: dict[str, Any] | None = None,
) -> str:
    audit_event_id = new_id("audit")
    payload_json = json.dumps(payload or {}, separators=(",", ":"), sort_keys=True)

    connection.execute(
        """
        INSERT INTO audit_event (
          id,
          actor_type,
          actor_id,
          event_type,
          entity_type,
          entity_id,
          payload_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            audit_event_id,
            actor_type,
            actor_id,
            event_type,
            entity_type,
            entity_id,
            payload_json,
        ),
    )

    return audit_event_id
