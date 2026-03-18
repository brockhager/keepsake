from __future__ import annotations

import argparse
import sqlite3
import sys

from .operations import add_revision, create_memory, create_vault
from .runtime_profile import resolve_runtime_profile
from .sqlite_profile_connection import connect_for_profile

PERSONAL_OWNER_ID = "owner-self"
PROFILE_INIT_MESSAGE = (
    "personal profile is not initialized. "
    "Run pwsh .\\scripts\\init-runtime-profile.ps1 -RuntimeMode personal"
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="keepsake", add_help=False, allow_abbrev=False)
    command_parser = parser.add_subparsers(dest="command_group", required=True)

    vault_parser = command_parser.add_parser("vault", add_help=False, allow_abbrev=False)
    vault_command_parser = vault_parser.add_subparsers(dest="command_name", required=True)

    vault_create_parser = vault_command_parser.add_parser(
        "create",
        add_help=False,
        allow_abbrev=False,
    )
    vault_create_parser.add_argument("name")

    vault_command_parser.add_parser("list", add_help=False, allow_abbrev=False)

    memory_parser = command_parser.add_parser("memory", add_help=False, allow_abbrev=False)
    memory_command_parser = memory_parser.add_subparsers(dest="command_name", required=True)

    memory_create_parser = memory_command_parser.add_parser(
        "create",
        add_help=False,
        allow_abbrev=False,
    )
    memory_create_parser.add_argument("--vault", dest="vault_id", required=True)

    memory_revise_parser = memory_command_parser.add_parser(
        "revise",
        add_help=False,
        allow_abbrev=False,
    )
    memory_revise_parser.add_argument("memory_id")

    memory_show_parser = memory_command_parser.add_parser(
        "show",
        add_help=False,
        allow_abbrev=False,
    )
    memory_show_parser.add_argument("memory_id")

    memory_history_parser = memory_command_parser.add_parser(
        "history",
        add_help=False,
        allow_abbrev=False,
    )
    memory_history_parser.add_argument("memory_id")

    memory_list_parser = memory_command_parser.add_parser(
        "list",
        add_help=False,
        allow_abbrev=False,
    )
    memory_list_parser.add_argument("--vault", dest="vault_id")

    args = parser.parse_args(argv)
    profile = resolve_runtime_profile("personal")

    if not profile.database_path.exists():
        print(PROFILE_INIT_MESSAGE, file=sys.stderr)
        return 1

    try:
        if args.command_group == "vault" and args.command_name == "create":
            created = create_vault(profile, owner_id=PERSONAL_OWNER_ID, name=args.name)

            connection = connect_for_profile(profile)
            try:
                row = connection.execute(
                    """
                    SELECT id, name, created_at
                    FROM vault
                    WHERE id = ?
                    """,
                    (created["vault_id"],),
                ).fetchone()
            finally:
                connection.close()

            print(f"vault_id: {row['id']}")
            print(f"name: {row['name']}")
            print(f"created_at: {row['created_at']}")
            return 0

        if args.command_group == "vault" and args.command_name == "list":
            connection = connect_for_profile(profile)
            try:
                rows = connection.execute(
                    """
                    SELECT id, name, created_at
                    FROM vault
                    WHERE owner_id = ?
                    ORDER BY name ASC, id ASC
                    """,
                    (PERSONAL_OWNER_ID,),
                ).fetchall()
            finally:
                connection.close()

            for row in rows:
                print(
                    f"vault_id: {row['id']} | name: {row['name']} | created_at: {row['created_at']}"
                )
            return 0

        if args.command_group == "memory" and args.command_name == "create":
            if sys.stdin.isatty():
                print("Enter memory content. Finish with Ctrl+Z then Enter.", file=sys.stderr)

            body = sys.stdin.read().strip()
            title_lines = [line.strip() for line in body.splitlines() if line.strip()]
            if not title_lines:
                raise ValueError("memory content cannot be empty")

            created = create_memory(
                profile,
                owner_id=PERSONAL_OWNER_ID,
                vault_id=args.vault_id,
                title=title_lines[0],
                body=body,
            )

            connection = connect_for_profile(profile)
            try:
                row = connection.execute(
                    """
                    SELECT memory_id, vault_id, vault_name, current_revision_number
                    FROM memory_current_view
                    WHERE memory_id = ?
                    """,
                    (created["memory_id"],),
                ).fetchone()
            finally:
                connection.close()

            print(f"memory_id: {row['memory_id']}")
            print(f"revision_number: {row['current_revision_number']}")
            print(f"vault_id: {row['vault_id']}")
            print(f"vault_name: {row['vault_name']}")
            return 0

        if args.command_group == "memory" and args.command_name == "revise":
            if sys.stdin.isatty():
                print("Enter memory content. Finish with Ctrl+Z then Enter.", file=sys.stderr)

            body = sys.stdin.read().strip()
            title_lines = [line.strip() for line in body.splitlines() if line.strip()]
            if not title_lines:
                raise ValueError("memory content cannot be empty")

            revised = add_revision(
                profile,
                owner_id=PERSONAL_OWNER_ID,
                memory_id=args.memory_id,
                title=title_lines[0],
                body=body,
            )

            connection = connect_for_profile(profile)
            try:
                row = connection.execute(
                    """
                    SELECT created_at
                    FROM memory_revision
                    WHERE id = ?
                    """,
                    (revised["revision_id"],),
                ).fetchone()
            finally:
                connection.close()

            print(f"memory_id: {revised['memory_id']}")
            print(f"revision_number: {revised['revision_number']}")
            print(f"created_at: {row['created_at']}")
            return 0

        if args.command_group == "memory" and args.command_name == "list":
            connection = connect_for_profile(profile)
            try:
                if args.vault_id is not None:
                    vault_row = connection.execute(
                        """
                        SELECT id, name
                        FROM vault
                        WHERE id = ? AND owner_id = ?
                        """,
                        (args.vault_id, PERSONAL_OWNER_ID),
                    ).fetchone()

                    if vault_row is None:
                        raise ValueError(f"vault not found: {args.vault_id}")

                    rows = connection.execute(
                        """
                        SELECT
                          memory_id,
                          current_title,
                          vault_id,
                          vault_name,
                          current_revision_number,
                          current_revision_created_at
                        FROM memory_current_view
                        WHERE owner_id = ? AND vault_id = ?
                        ORDER BY current_revision_created_at DESC, memory_created_at DESC, memory_id ASC
                        """,
                        (PERSONAL_OWNER_ID, args.vault_id),
                    ).fetchall()

                    if not rows:
                        print(f"no memories found in vault: {vault_row['name']}")
                        return 0
                else:
                    rows = connection.execute(
                        """
                        SELECT
                          memory_id,
                          current_title,
                          vault_id,
                          vault_name,
                          current_revision_number,
                          current_revision_created_at
                        FROM memory_current_view
                        WHERE owner_id = ?
                        ORDER BY current_revision_created_at DESC, memory_created_at DESC, memory_id ASC
                        """,
                        (PERSONAL_OWNER_ID,),
                    ).fetchall()

                    if not rows:
                        print("no memories found")
                        return 0
            finally:
                connection.close()

            for row in rows:
                print(
                    " | ".join(
                        [
                            f"memory_id: {row['memory_id']}",
                            f"title: {row['current_title']}",
                            f"vault_id: {row['vault_id']}",
                            f"vault_name: {row['vault_name']}",
                            f"revision_number: {row['current_revision_number']}",
                            f"last_revised_at: {row['current_revision_created_at']}",
                        ]
                    )
                )
            return 0

        if args.command_group == "memory" and args.command_name == "show":
            connection = connect_for_profile(profile)
            try:
                row = connection.execute(
                    """
                    SELECT
                      mcv.memory_id,
                      mcv.vault_name,
                      mcv.memory_created_at,
                      mcv.current_revision_created_at,
                      mr.body
                    FROM memory_current_view mcv
                    JOIN memory_revision mr ON mr.id = mcv.current_revision_id
                    WHERE mcv.memory_id = ?
                    """,
                    (args.memory_id,),
                ).fetchone()
            finally:
                connection.close()

            if row is None:
                raise ValueError(f"memory not found: {args.memory_id}")

            print(f"memory_id: {row['memory_id']}")
            print(f"vault_name: {row['vault_name']}")
            print(f"created_at: {row['memory_created_at']}")
            print(f"last_revised_at: {row['current_revision_created_at']}")
            print("content:")
            print(row["body"])
            return 0

        if args.command_group == "memory" and args.command_name == "history":
            connection = connect_for_profile(profile)
            try:
                rows = connection.execute(
                    """
                    SELECT revision_number, created_at
                    FROM memory_history_view
                    WHERE memory_id = ?
                    ORDER BY revision_number ASC
                    """,
                    (args.memory_id,),
                ).fetchall()
            finally:
                connection.close()

            if not rows:
                raise ValueError(f"memory not found: {args.memory_id}")

            for row in rows:
                print(f"revision_number: {row['revision_number']} | created_at: {row['created_at']}")
            return 0

        raise ValueError("unsupported command")
    except sqlite3.OperationalError as exc:
        if "no such table" in str(exc):
            print(PROFILE_INIT_MESSAGE, file=sys.stderr)
        else:
            print(str(exc), file=sys.stderr)
        return 1
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
