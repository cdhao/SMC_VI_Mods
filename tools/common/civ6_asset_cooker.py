"""Small wrapper around the official Civilization VI Asset Cooker."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path


class AssetCookerError(RuntimeError):
    """Raised when the local SDK Asset Cooker cannot be located or run."""


DEFAULT_SDK_ROOT = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization VI SDK"
)


@dataclass(frozen=True)
class AssetCookerPaths:
    executable: Path
    config: Path


def resolve_asset_cooker(
    *, sdk_root: Path | None = None, cooker_path: Path | None = None
) -> AssetCookerPaths:
    """Resolve the SDK paths, preferring explicit arguments over environment."""

    configured_sdk_root = sdk_root or (
        Path(os.environ["CIV6_SDK_ROOT"]) if os.environ.get("CIV6_SDK_ROOT") else DEFAULT_SDK_ROOT
    )
    executable = cooker_path or (
        Path(os.environ["CIV6_ASSET_COOKER"])
        if os.environ.get("CIV6_ASSET_COOKER")
        else configured_sdk_root / "AssetModTools" / "Cooker" / "Civ6AssetCooker_FinalRelease.exe"
    )
    config = configured_sdk_root / "AssetModTools" / "Cooker" / "Civ6.cfg"
    if not executable.is_file():
        raise AssetCookerError(f"Civ6 Asset Cooker not found: {executable}")
    if not config.is_file():
        raise AssetCookerError(f"Civ6 cooker config not found: {config}")
    return AssetCookerPaths(executable=executable, config=config)


def cook_xlp(
    paths: AssetCookerPaths,
    *,
    cooker_root: Path,
    xlp_name: str,
) -> None:
    """Cook one XLP from the mod's isolated cooker workspace."""

    command = [
        str(paths.executable),
        "--mode",
        "XLP",
        "--platform",
        "Windows",
        "--config",
        str(paths.config),
        "--pantry",
        "Images",
        "--stewpot",
        r"Platforms\Windows\BLPs",
        "--log_path",
        "Logs",
        str(Path("XLPs") / xlp_name),
    ]
    creationflags = subprocess.BELOW_NORMAL_PRIORITY_CLASS if os.name == "nt" else 0
    subprocess.run(
        command,
        cwd=cooker_root,
        check=True,
        creationflags=creationflags,
    )
