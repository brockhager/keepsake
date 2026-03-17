from __future__ import annotations

import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

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


class Phase1CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temp_home = Path(tempfile.mkdtemp(prefix="keepsake-cli-home-"))

    def tearDown(self) -> None:
        shutil.rmtree(self._temp_home, ignore_errors=True)

    def _prepare_personal_profile(self) -> Path:
        profile_root = self._temp_home / ".keepsake" / "personal"
        profile_root.mkdir(parents=True, exist_ok=True)
        (profile_root / "attachments").mkdir(parents=True, exist_ok=True)
        (profile_root / "exports").mkdir(parents=True, exist_ok=True)
        apply_migrations(profile_root / "keepsake.db")
        return profile_root

    def _run_cli(self, *args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(REPO_ROOT)
        env["HOME"] = str(self._temp_home)
        env["USERPROFILE"] = str(self._temp_home)

        drive, tail = os.path.splitdrive(str(self._temp_home))
        if drive:
            env["HOMEDRIVE"] = drive
            env["HOMEPATH"] = tail or "\\"

        return subprocess.run(
            [sys.executable, "-m", "keepsake", *args],
            input=input_text,
            text=True,
            capture_output=True,
            cwd=REPO_ROOT,
            env=env,
            check=False,
        )

    def test_phase_1_personal_cli_flow(self) -> None:
        self._prepare_personal_profile()

        first_vault = self._run_cli("vault", "create", "Family")
        self.assertEqual(first_vault.returncode, 0, msg=first_vault.stderr)
        first_vault_lines = first_vault.stdout.strip().splitlines()
        first_vault_id = first_vault_lines[0].split(": ", 1)[1]

        second_vault = self._run_cli("vault", "create", "Travel")
        self.assertEqual(second_vault.returncode, 0, msg=second_vault.stderr)
        second_vault_lines = second_vault.stdout.strip().splitlines()
        second_vault_id = second_vault_lines[0].split(": ", 1)[1]

        listed_vaults = self._run_cli("vault", "list")
        self.assertEqual(listed_vaults.returncode, 0, msg=listed_vaults.stderr)
        listed_vault_lines = listed_vaults.stdout.strip().splitlines()
        self.assertEqual(len(listed_vault_lines), 2)
        self.assertIn(f"vault_id: {first_vault_id} | name: Family", listed_vault_lines[0])
        self.assertIn(f"vault_id: {second_vault_id} | name: Travel", listed_vault_lines[1])

        created_memory = self._run_cli(
            "memory",
            "create",
            "--vault",
            first_vault_id,
            input_text="Morning walk\nI took a quiet walk and noticed the cold air.\n",
        )
        self.assertEqual(created_memory.returncode, 0, msg=created_memory.stderr)
        created_memory_lines = created_memory.stdout.strip().splitlines()
        memory_id = created_memory_lines[0].split(": ", 1)[1]
        self.assertIn("revision_number: 1", created_memory.stdout)
        self.assertIn(f"vault_id: {first_vault_id}", created_memory.stdout)
        self.assertIn("vault_name: Family", created_memory.stdout)

        revised_memory = self._run_cli(
            "memory",
            "revise",
            memory_id,
            input_text="Morning walk\nA month later, I remember the stillness more than the route.\n",
        )
        self.assertEqual(revised_memory.returncode, 0, msg=revised_memory.stderr)
        self.assertIn(f"memory_id: {memory_id}", revised_memory.stdout)
        self.assertIn("revision_number: 2", revised_memory.stdout)
        self.assertIn("created_at: ", revised_memory.stdout)

        shown_memory = self._run_cli("memory", "show", memory_id)
        self.assertEqual(shown_memory.returncode, 0, msg=shown_memory.stderr)
        self.assertIn(f"memory_id: {memory_id}", shown_memory.stdout)
        self.assertIn("vault_name: Family", shown_memory.stdout)
        self.assertIn("created_at: ", shown_memory.stdout)
        self.assertIn("last_revised_at: ", shown_memory.stdout)
        self.assertIn("A month later, I remember the stillness more than the route.", shown_memory.stdout)

        memory_history = self._run_cli("memory", "history", memory_id)
        self.assertEqual(memory_history.returncode, 0, msg=memory_history.stderr)
        self.assertEqual(len(memory_history.stdout.strip().splitlines()), 2)
        self.assertIn("revision_number: 1 | created_at: ", memory_history.stdout)
        self.assertIn("revision_number: 2 | created_at: ", memory_history.stdout)

        self.assertFalse((self._temp_home / ".keepsake" / "demo").exists())

    def test_cli_requires_initialized_personal_profile(self) -> None:
        result = self._run_cli("vault", "list")

        self.assertEqual(result.returncode, 1)
        self.assertIn("personal profile is not initialized", result.stderr)


if __name__ == "__main__":
    unittest.main()
