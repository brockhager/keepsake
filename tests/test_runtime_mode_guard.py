from __future__ import annotations

import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from keepsake.operations import create_vault
from keepsake.runtime_profile import resolve_runtime_profile
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


class RuntimeModeGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        _reset_runtime_mode_guard_for_tests()
        self._temp_dir = Path(tempfile.mkdtemp(prefix="keepsake-guard-"))

    def tearDown(self) -> None:
        _reset_runtime_mode_guard_for_tests()
        shutil.rmtree(self._temp_dir, ignore_errors=True)

    def test_cannot_open_personal_and_demo_databases_in_same_process(self) -> None:
        personal_profile = resolve_runtime_profile("personal", data_root=self._temp_dir)
        demo_profile = resolve_runtime_profile("demo", data_root=self._temp_dir)

        apply_migrations(personal_profile.database_path)
        apply_migrations(demo_profile.database_path)

        create_vault(
            personal_profile,
            owner_id="owner-self",
            name="Personal Vault",
            is_default=True,
        )

        with self.assertRaisesRegex(RuntimeError, "already bound to runtime mode"):
            create_vault(
                demo_profile,
                owner_id="demo-owner",
                name="Demo Vault",
            )


if __name__ == "__main__":
    unittest.main()
