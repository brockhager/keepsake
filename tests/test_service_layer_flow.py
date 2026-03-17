from __future__ import annotations

import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from keepsake.operations import add_revision, create_memory, create_vault, grant_share, request_share, revoke_share
from keepsake.runtime_profile import RuntimeProfile, resolve_runtime_profile
from keepsake.sqlite_profile_connection import _reset_runtime_mode_guard_for_tests

REPO_ROOT = Path(__file__).resolve().parents[1]
MIGRATION_FILES = [
    REPO_ROOT / "db" / "migrations" / "0001_initial_schema.up.sql",
    REPO_ROOT / "db" / "migrations" / "0002_invariants_and_views.up.sql",
    REPO_ROOT / "db" / "migrations" / "0003_vault_foundation.up.sql",
]


def apply_migrations(database_path: Path) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(database_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON;")
        for migration_file in MIGRATION_FILES:
            connection.executescript(migration_file.read_text(encoding="utf-8"))
        connection.commit()


def insert_person(database_path: Path, *, owner_id: str, person_id: str, display_name: str) -> None:
    with sqlite3.connect(database_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON;")
        connection.execute(
            """
            INSERT INTO person (id, owner_id, display_name)
            VALUES (?, ?, ?)
            """,
            (person_id, owner_id, display_name),
        )
        connection.commit()


class ServiceLayerFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        _reset_runtime_mode_guard_for_tests()
        self._temp_dir = Path(tempfile.mkdtemp(prefix="keepsake-flow-"))

    def tearDown(self) -> None:
        _reset_runtime_mode_guard_for_tests()
        shutil.rmtree(self._temp_dir, ignore_errors=True)

    def _prepare_profile(self, runtime_mode: str) -> RuntimeProfile:
        profile = resolve_runtime_profile(runtime_mode=runtime_mode, data_root=self._temp_dir)
        profile.profile_root.mkdir(parents=True, exist_ok=True)
        profile.attachments_path.mkdir(parents=True, exist_ok=True)
        profile.exports_path.mkdir(parents=True, exist_ok=True)
        apply_migrations(profile.database_path)
        return profile

    def _run_full_flow(self, runtime_mode: str) -> None:
        profile = self._prepare_profile(runtime_mode)

        owner_id = "owner-self"
        person_id = "person-1"
        insert_person(profile.database_path, owner_id=owner_id, person_id=person_id, display_name="Pat Demo")

        vault = create_vault(
            profile,
            owner_id=owner_id,
            name=f"{runtime_mode.title()} Vault",
            is_default=True,
        )

        created = create_memory(
            profile,
            owner_id=owner_id,
            vault_id=vault["vault_id"],
            title="Morning walk memory",
            body="I took a quiet walk and noticed how calm it felt.",
            time_precision="day",
            certainty="uncertain",
        )

        revised = add_revision(
            profile,
            owner_id=owner_id,
            memory_id=created["memory_id"],
            title="Morning walk memory",
            body="One month later, I remember this as the day I slowed down.",
            time_precision="day",
            certainty="uncertain",
            edit_reason="Added context after reflection",
        )

        share_request = request_share(
            profile,
            requested_by=owner_id,
            memory_id=created["memory_id"],
            person_id=person_id,
            message="Sharing this one memory intentionally.",
        )

        granted = grant_share(
            profile,
            granted_by=owner_id,
            request_id=share_request["request_id"],
        )

        revoked = revoke_share(
            profile,
            revoked_by=owner_id,
            grant_id=granted["grant_id"],
        )

        self.assertEqual(revised["revision_number"], 2)
        self.assertEqual(granted["max_revision_number"], 2)
        self.assertEqual(revoked["grant_id"], granted["grant_id"])

        with sqlite3.connect(profile.database_path) as connection:
            connection.row_factory = sqlite3.Row

            memory_row = connection.execute(
                """
                SELECT id, vault_id, current_revision_id
                FROM memory
                WHERE id = ?
                """,
                (created["memory_id"],),
            ).fetchone()
            self.assertIsNotNone(memory_row)
            self.assertEqual(memory_row["vault_id"], vault["vault_id"])
            self.assertEqual(memory_row["current_revision_id"], revised["revision_id"])

            revision_count = connection.execute(
                """
                SELECT COUNT(*)
                FROM memory_revision
                WHERE memory_id = ?
                """,
                (created["memory_id"],),
            ).fetchone()[0]
            self.assertEqual(revision_count, 2)

            request_status = connection.execute(
                """
                SELECT status, decided_at
                FROM share_request
                WHERE id = ?
                """,
                (share_request["request_id"],),
            ).fetchone()
            self.assertEqual(request_status["status"], "accepted")
            self.assertIsNotNone(request_status["decided_at"])

            grant_row = connection.execute(
                """
                SELECT max_revision_number, revoked_at
                FROM share_grant
                WHERE id = ?
                """,
                (granted["grant_id"],),
            ).fetchone()
            self.assertEqual(grant_row["max_revision_number"], 2)
            self.assertIsNotNone(grant_row["revoked_at"])

            audit_events = connection.execute(
                """
                SELECT COUNT(*)
                FROM audit_event
                """
            ).fetchone()[0]
            self.assertEqual(audit_events, 6)

    def test_create_revise_request_grant_revoke_flow_personal(self) -> None:
        self._run_full_flow("personal")

    def test_create_revise_request_grant_revoke_flow_demo(self) -> None:
        self._run_full_flow("demo")


if __name__ == "__main__":
    unittest.main()
