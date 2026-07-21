#!/usr/bin/env python3
"""Cook the generated Grace Ashcroft UI assets with the official Civ6 SDK."""

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
    """Return the explicit package plan without requiring the Civ6 SDK."""

    blp_root = config.runtime_root / "Platforms" / "Windows" / "BLPs"
    return (
        CookPackage(config.package("ui"), f"{config.package('ui')}.xlp", blp_root / f"{config.package('ui')}.blp"),
        CookPackage(
            config.package("resource"),
            f"{config.package('resource')}.xlp",
            blp_root / f"{config.package('resource')}.blp",
        ),
        CookPackage(
            config.package("leader_fallback"),
            "leaderfallbacks.xlp",
            blp_root / f"{config.package('leader_fallback')}.blp",
        ),
    )


def print_plan(config: ModBuildConfig, packages: tuple[CookPackage, ...]) -> None:
    print(f"Grace asset manifest: {config.manifest_path}")
    print(f"Asset revision: {config.asset_revision}; release version: {config.release_version}")
    for package in packages:
        print(f"Cook {package.xlp_name} -> {package.runtime_blp}")


def run(config: ModBuildConfig, *, sdk_root: Path | None, cooker_path: Path | None) -> None:
    packages = build_cook_plan(config)
    build_script = REPO_ROOT / "tools" / "grace_ashcroft" / "build_assets.py"
    check_script = REPO_ROOT / "tools" / "grace_ashcroft" / "check_static.py"
    cooker_root = config.asset_root / "cooker"
    cooker_blp_dir = cooker_root / "Platforms" / "Windows" / "BLPs"

    subprocess.run([sys.executable, "-B", str(build_script)], check=True)
    paths = resolve_asset_cooker(sdk_root=sdk_root, cooker_path=cooker_path)
    cooker_blp_dir.mkdir(parents=True, exist_ok=True)
    for package in packages:
        cooked_blp = cooker_blp_dir / f"{package.name}.blp"
        if cooked_blp.exists():
            cooked_blp.unlink()

    for package in packages:
        cook_xlp(paths, cooker_root=cooker_root, xlp_name=package.xlp_name)

    for package in packages:
        cooked_blp = cooker_blp_dir / f"{package.name}.blp"
        if not cooked_blp.is_file():
            raise RuntimeError(f"Expected cooked package was not created: {cooked_blp}")
        package.runtime_blp.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(cooked_blp, package.runtime_blp)

    subprocess.run([sys.executable, "-B", str(build_script), "--cleanup-cooker-dds"], check=True)
    subprocess.run([sys.executable, "-B", str(check_script)], check=True)
    print("Grace Ashcroft assets cooked and validated.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sdk-root", type=Path, help="Civ6 SDK root; defaults to CIV6_SDK_ROOT")
    parser.add_argument("--cooker-path", type=Path, help="Asset Cooker executable; defaults to CIV6_ASSET_COOKER")
    parser.add_argument("--dry-run", action="store_true", help="Print the manifest package plan and exit")
    args = parser.parse_args(argv)

    config = load_mod_config(REPO_ROOT / "assets" / "GraceAshcroft" / "mod-build.toml", repo_root=REPO_ROOT)
    packages = build_cook_plan(config)
    if args.dry_run:
        print_plan(config, packages)
        return 0
    run(config, sdk_root=args.sdk_root, cooker_path=args.cooker_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
