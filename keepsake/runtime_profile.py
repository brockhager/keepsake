from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

RuntimeMode = Literal["personal", "demo"]


@dataclass(frozen=True)
class RuntimeProfile:
    runtime_mode: RuntimeMode
    data_root: Path
    profile_root: Path
    database_path: Path
    attachments_path: Path
    exports_path: Path
    profile_metadata_path: Path


def resolve_runtime_profile(runtime_mode: RuntimeMode, data_root: str | Path | None = None) -> RuntimeProfile:
    if runtime_mode not in ("personal", "demo"):
        raise ValueError("runtime_mode must be 'personal' or 'demo'")

    root = Path(data_root).expanduser() if data_root is not None else Path.home() / ".keepsake"
    profile_root = root / runtime_mode

    return RuntimeProfile(
        runtime_mode=runtime_mode,
        data_root=root,
        profile_root=profile_root,
        database_path=profile_root / "keepsake.db",
        attachments_path=profile_root / "attachments",
        exports_path=profile_root / "exports",
        profile_metadata_path=profile_root / "profile.json",
    )
