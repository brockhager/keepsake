from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from threading import Lock
from typing import Iterator

from .runtime_profile import RuntimeProfile

_active_runtime_mode: str | None = None
_guard_lock = Lock()


def _bind_process_runtime_mode(runtime_mode: str) -> None:
    global _active_runtime_mode

    with _guard_lock:
        if _active_runtime_mode is None:
            _active_runtime_mode = runtime_mode
            return

        if _active_runtime_mode != runtime_mode:
            raise RuntimeError(
                "This process is already bound to runtime mode "
                f"'{_active_runtime_mode}' and cannot open '{runtime_mode}'."
            )


def connect_for_profile(profile: RuntimeProfile) -> sqlite3.Connection:
    _bind_process_runtime_mode(profile.runtime_mode)
    profile.database_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(profile.database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


@contextmanager
def transaction(profile: RuntimeProfile) -> Iterator[sqlite3.Connection]:
    connection = connect_for_profile(profile)
    try:
        connection.execute("BEGIN;")
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _reset_runtime_mode_guard_for_tests() -> None:
    global _active_runtime_mode

    with _guard_lock:
        _active_runtime_mode = None
