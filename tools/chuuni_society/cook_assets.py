#!/usr/bin/env python3
"""Cook Chuuni Society UI assets with the official Civilization VI SDK."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.common.civ6_asset_cooker import cook_xlp, resolve_asset_cooker  # noqa: E402
from tools.common.civ6_mod_config import ModBuildConfig, load_mod_config  # noqa: E402


@dataclass(frozen=True)
class CookPackage:
    name: str
    xlp_name: str
    runtime_blp: Path


def build_cook_plan(config: ModBuildConfig) -> tuple[CookPackage, ...]:
    blp_root = config.runtime_root / "Platforms" / "Windows" / "BLPs"
    return (
        CookPackage(config.package("ui"), f"{config.package('ui')}.xlp", blp_root / f"{config.package('ui')}.blp"),
        CookPackage(config.package("leader_fallback"), "leaderfallbacks.xlp", blp_root / f"{config.package('leader_fallback')}.blp"),
    )


def cleanup_cooker_dds(cooker_root: Path) -> None:
    """Remove the temporary DDS copies consumed by the official cooker."""

    images_root = cooker_root / "Images"
    removed = 0
    if images_root.is_dir():
        for target in images_root.glob("*.dds"):
            target.unlink()
            removed += 1
    print(f"Removed {removed} temporary cooker DDS files from {images_root}.")


def run(config: ModBuildConfig, *, sdk_root: Path | None, cooker_path: Path | None) -> None:
    packages = build_cook_plan(config)
    cooker_root = config.asset_root / "cooker"
    cooked_root = cooker_root / "Platforms" / "Windows" / "BLPs"
    try:
        subprocess.run([sys.executable, "-B", str(REPO_ROOT / "tools/chuuni_society/build_assets.py")], check=True)
        paths = resolve_asset_cooker(sdk_root=sdk_root, cooker_path=cooker_path)
        cooked_root.mkdir(parents=True, exist_ok=True)

        for package in packages:
            cooked = cooked_root / f"{package.name}.blp"
            if cooked.exists():
                cooked.unlink()
            cook_xlp(paths, cooker_root=cooker_root, xlp_name=package.xlp_name)
            if not cooked.is_file():
                raise RuntimeError(f"Expected cooked package was not created: {cooked}")
            package.runtime_blp.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(cooked, package.runtime_blp)
        subprocess.run([sys.executable, "-B", str(REPO_ROOT / "tools/chuuni_society/check_static.py")], check=True)
        print("Chuuni Society assets cooked and validated.")
    finally:
        cleanup_cooker_dds(cooker_root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sdk-root", type=Path)
    parser.add_argument("--cooker-path", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    config = load_mod_config(REPO_ROOT / "assets/ChuuniSociety/mod-build.toml", repo_root=REPO_ROOT)
    packages = build_cook_plan(config)
    if args.dry_run:
        for package in packages:
            print(f"Cook {package.xlp_name} -> {package.runtime_blp}")
        return 0
    run(config, sdk_root=args.sdk_root, cooker_path=args.cooker_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
