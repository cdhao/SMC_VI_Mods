#!/usr/bin/env python3
"""Static contracts for the deployable Grace Ashcroft Civilization VI mod.

PowerShell remains responsible for Windows-only orchestration (Asset Cooker,
deployment, and workspace cleanup).  This module owns deterministic repository
validation so its rules can be imported, unit-tested, and reused by future mods.
"""

from __future__ import annotations

import argparse
import re
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


class ValidationError(RuntimeError):
    """Raised when one or more repository contracts are not satisfied."""


@dataclass(frozen=True)
class TextContract:
    path: Path
    required: tuple[str, ...] = ()
    forbidden: tuple[str, ...] = ()
    required_patterns: tuple[str, ...] = ()
    forbidden_patterns: tuple[str, ...] = ()


REPO_ROOT = Path(__file__).resolve().parents[2]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require_file(path: Path) -> None:
    if not path.is_file():
        raise ValidationError(f"Missing required file: {path}")


def require_contains(path: Path, value: str) -> None:
    if value not in read_text(path):
        raise ValidationError(f"Expected {value!r} in {path}")


def require_not_contains(path: Path, value: str) -> None:
    if value in read_text(path):
        raise ValidationError(f"Did not expect {value!r} in {path}")


def require_matches(path: Path, pattern: str) -> None:
    if re.search(pattern, read_text(path), flags=re.MULTILINE | re.DOTALL) is None:
        raise ValidationError(f"Expected pattern {pattern!r} in {path}")


def require_not_matches(path: Path, pattern: str) -> None:
    if re.search(pattern, read_text(path), flags=re.MULTILINE | re.DOTALL) is not None:
        raise ValidationError(f"Did not expect pattern {pattern!r} in {path}")


def require_binary_contains(path: Path, value: str) -> None:
    require_file(path)
    if value.encode("ascii") not in path.read_bytes():
        raise ValidationError(f"Expected binary entry {value!r} in {path}")


def require_binary_not_contains(path: Path, value: str) -> None:
    require_file(path)
    if value.encode("ascii") in path.read_bytes():
        raise ValidationError(f"Did not expect binary entry {value!r} in {path}")


def require_dds_rgba(path: Path, width: int, height: int) -> None:
    require_file(path)
    payload = path.read_bytes()
    if len(payload) < 128 or payload[:4] != b"DDS ":
        raise ValidationError(f"Not a DDS texture: {path}")

    actual_height, actual_width = struct.unpack_from("<II", payload, 12)
    bits_per_pixel = struct.unpack_from("<I", payload, 88)[0]
    fourcc = payload[84:88]
    masks = struct.unpack_from("<IIII", payload, 92)
    legacy_rgba = fourcc == b"\x00\x00\x00\x00" and masks == (
        0x000000FF,
        0x0000FF00,
        0x00FF0000,
        0xFF000000,
    )
    dx10_rgba = (
        fourcc == b"DX10"
        and len(payload) >= 148
        and struct.unpack_from("<I", payload, 128)[0] == 28
    )
    if (actual_width, actual_height, bits_per_pixel) != (width, height, 32):
        raise ValidationError(
            f"Unexpected DDS dimensions for {path}: "
            f"expected {width}x{height}x32, got "
            f"{actual_width}x{actual_height}x{bits_per_pixel}"
        )
    if not (legacy_rgba or dx10_rgba):
        raise ValidationError(f"DDS is not RGBA-compatible with its TEX file: {path}")


def runtime_mod_paths(mod_root: Path) -> list[Path]:
    """Return build-only files and directories incorrectly present in a runtime mod."""

    forbidden_roots = ("Images", "XLPs", "Logs")
    forbidden_names = {
        "GraceAshcroft.Art.xml",
        "GraceAshcroft.civ6proj",
        "GraceAshcroft.civ6sln",
    }
    forbidden_suffixes = {".tex", ".xlp", ".civ6suo"}
    found: list[Path] = []
    for path in mod_root.rglob("*"):
        relative = path.relative_to(mod_root)
        if relative.parts[0] in forbidden_roots:
            found.append(relative)
        elif path.name in forbidden_names or path.suffix.lower() in forbidden_suffixes:
            found.append(relative)
    return sorted(set(found))


def apply_text_contracts(contracts: Iterable[TextContract]) -> None:
    for contract in contracts:
        require_file(contract.path)
        for value in contract.required:
            require_contains(contract.path, value)
        for value in contract.forbidden:
            require_not_contains(contract.path, value)
        for pattern in contract.required_patterns:
            require_matches(contract.path, pattern)
        for pattern in contract.forbidden_patterns:
            require_not_matches(contract.path, pattern)


def check_runtime_layout(root: Path) -> None:
    mod_root = root / "mods" / "GraceAshcroft"
    forbidden = runtime_mod_paths(mod_root)
    if forbidden:
        listed = ", ".join(str(path) for path in forbidden)
        raise ValidationError(f"Runtime mod contains build-only paths: {listed}")

    for relative in (
        "GraceAshcroft.modinfo",
        "GraceAshcroft.dep",
        "Data/Config.sql",
        "Data/Gameplay.sql",
        "Data/GraceColors.xml",
        "Icons/GraceIcons.sql",
        "Scripts/GraceGameplay.lua",
        "Text/GraceAshcroft_zh_Hans_CN.sql",
        "ArtDefs/Civilizations.artdef",
        "ArtDefs/Districts.artdef",
        "ArtDefs/FallbackLeaders.artdef",
        "Platforms/Windows/BLPs/GraceUITexture.blp",
        "Platforms/Windows/BLPs/GraceResourceIconsV2.blp",
        "Platforms/Windows/BLPs/LeaderFallbacks.blp",
    ):
        require_file(mod_root / relative)


def check_asset_workspace(root: Path) -> None:
    asset_root = root / "assets" / "GraceAshcroft"
    project_root = root / "projects" / "GraceAshcroft"
    required = (
        asset_root / "source/icons/GraceAshcroft_Civilization.png",
        asset_root / "source/icons/GraceAshcroft_InfectedBlood.png",
        asset_root / "source/icons/GraceAshcroft_LeaderIcon.png",
        asset_root / "leader-art/png/GraceAshcroft_Background.png",
        asset_root / "leader-art/png/GraceAshcroft_Foreground.png",
        asset_root / "leader-art/png/GraceAshcroft_LoadingScene.png",
        asset_root / "leader-art/png/GraceAshcroft_LoadingBlank.png",
        asset_root / "cooker/XLPs/GraceUITexture.xlp",
        asset_root / "cooker/XLPs/GraceResourceIconsV2.xlp",
        asset_root / "cooker/XLPs/leaderfallbacks.xlp",
        project_root / "GraceAshcroft.Art.xml",
        project_root / "GraceAshcroft.civ6proj",
        project_root / "GraceAshcroft.civ6sln",
    )
    for path in required:
        require_file(path)

    require_dds_rgba(asset_root / "leader-art/dds/GraceAshcroft_Background.dds", 2048, 1024)
    require_dds_rgba(asset_root / "leader-art/dds/GraceAshcroft_Foreground.dds", 1024, 2048)
    require_dds_rgba(asset_root / "leader-art/dds/GraceAshcroft_LoadingScene.dds", 2048, 1024)
    require_dds_rgba(asset_root / "leader-art/dds/GraceAshcroft_LoadingBlank.dds", 8, 8)


def check_build_scripts(root: Path) -> None:
    tools_root = root / "tools"
    legacy_checker = tools_root / "_check_grace_mod_static_impl.ps1"
    if legacy_checker.exists():
        raise ValidationError(f"Obsolete PowerShell checker must be removed: {legacy_checker}")
    apply_text_contracts(
        (
            TextContract(
                tools_root / "grace_ashcroft/build_assets.py",
                required=(
                    "CIVILIZATION_ASSET_VERSION = 2",
                    "INFECTED_BLOOD_ASSET_VERSION = 2",
                    "def cleanup_obsolete_civilization_assets",
                    "def cleanup_obsolete_infected_blood_assets",
                    "from tools.common.civ6_texture import",
                    'COOKER_ROOT = ASSET_ROOT / "cooker"',
                ),
                forbidden=("MOD_IMAGES =", "MOD_TEXTURES =", "MOD_VERSION ="),
            ),
            TextContract(
                tools_root / "grace_ashcroft/cook_assets.ps1",
                required=(
                    '$cookerRoot = Join-Path $repoRoot "assets\\GraceAshcroft\\cooker"',
                    '$runtimeBlpDir = Join-Path $modRoot "Platforms\\Windows\\BLPs"',
                    "Copy-Item -LiteralPath $cookedBlp",
                    "--cleanup-cooker-dds",
                ),
            ),
            TextContract(
                tools_root / "grace_ashcroft/deploy.ps1",
                required=("[System.IO.Path]::GetFullPath", "StartsWith", "Refusing"),
            ),
            TextContract(
                tools_root / "cleanup_workspace.ps1",
                required=("SupportsShouldProcess", "__pycache__", ".tmp", "Refusing"),
                forbidden=("assets\\GraceAshcroft\\generated",),
            ),
            TextContract(
                tools_root / "grace_ashcroft/check_static.ps1",
                required=("check_static.py", "python"),
                forbidden=("Assert-ContainsText", "_check_grace_mod_static_impl.ps1"),
            ),
            TextContract(
                tools_root / "check_grace_mod_static.ps1",
                required=("grace_ashcroft\\check_static.ps1",),
            ),
        )
    )


def check_mod_contract(root: Path) -> None:
    mod_root = root / "mods" / "GraceAshcroft"
    apply_text_contracts(
        (
            TextContract(
                mod_root / "GraceAshcroft.modinfo",
                required=(
                    'version="2"',
                    "Data/Config.sql",
                    "Data/Gameplay.sql",
                    "Icons/GraceIcons.sql",
                    "GraceAshcroft.dep",
                    "Platforms/Windows/BLPs/GraceUITexture.blp",
                    "Platforms/Windows/BLPs/GraceResourceIconsV2.blp",
                    "Platforms/Windows/BLPs/LeaderFallbacks.blp",
                ),
                forbidden=("Images/", "XLPs/", ".tex", "UI/GraceBloodPanel"),
            ),
            TextContract(
                mod_root / "Data/Config.sql",
                required=(
                    "CIVILIZATION_ELPIS_PROTOCOL",
                    "LEADER_GRACE_ASHCROFT",
                    "DISTRICT_GRACE_ARK",
                    "ICON_CIVILIZATION_ELPIS_PROTOCOL",
                    "ICON_LEADER_GRACE_ASHCROFT",
                    "ICON_RESOURCE_INFECTED_BLOOD",
                ),
                forbidden=("BUILDING_RHODES_HILL_SANATORIUM", "ICON_CIVILIZATION_UNKNOWN"),
            ),
            TextContract(
                mod_root / "Data/Gameplay.sql",
                required=(
                    "RESOURCE_INFECTED_BLOOD",
                    "RESOURCECLASS_STRATEGIC",
                    "DISTRICT_GRACE_ARK', 'DISTRICT_CAMPUS",
                    "StartBiasRivers",
                    "StartBiasTerrains",
                    "Project_ResourceCosts",
                    "GRACE_ARK_SCIENCE_ADJACENCY_PRODUCTION",
                    "MODIFIER_ALL_DISTRICTS_ADJUST_YIELD_BASED_ON_ADJACENCY_BONUS",
                    "GRACE_ARK_GARRISON_RANGE",
                    "GRACE_ARK_GARRISON_SIGHT",
                    "MODIFIER_PLAYER_ADJUST_UNIT_UPGRADE_DISCOUNT_PERCENT",
                ),
                forbidden=(
                    "BUILDING_RHODES_HILL_SANATORIUM",
                    "GRACE_ARK_PROD_",
                    "GRACE_ARK_CITY_CENTER_PRODUCTION",
                    "GRACE_ARK_IMPROVEMENT_PRODUCTION_",
                ),
            ),
            TextContract(
                mod_root / "Scripts/GraceGameplay.lua",
                required=(
                    "RESOURCE_INFECTED_BLOOD",
                    "ChangeResourceAmount",
                    "Events.UnitUpgraded.Add",
                    "ForceHealUnit",
                    "unit:ChangeDamage(-actualHeal)",
                    "Events.UnitKilledInCombat.Add",
                    "IsGracePlayer(playerID)",
                    "LEADER_GRACE_ASHCROFT",
                    "HandleStrategicMaterialSynthesis",
                    "HandlePathologyFunding",
                ),
                forbidden=(
                    "UnitManager.ChangeDamage",
                    "LuaEvents.GraceBloodChanged",
                    "GetProperty(INFECTED_BLOOD",
                    "SetProperty(INFECTED_BLOOD",
                    "unitTypeCache",
                ),
            ),
            TextContract(
                mod_root / "Icons/GraceIcons.sql",
                required=(
                    "DELETE FROM IconTextureAtlases",
                    "DELETE FROM IconDefinitions",
                    "ICON_ATLAS_GRACE_CIVILIZATION_V2",
                    "ICON_ATLAS_GRACE_CIVILIZATION_FONT_V2",
                    "ICON_ATLAS_GRACE_INFECTED_BLOOD_V2",
                    "ICON_ATLAS_GRACE_INFECTED_BLOOD_FONT_V2",
                    "ICON_CIVILIZATION_ELPIS_PROTOCOL",
                    "ICON_LEADER_GRACE_ASHCROFT",
                    "ICON_RESOURCE_INFECTED_BLOOD",
                ),
                forbidden=("INSERT OR REPLACE INTO IconTextureAtlases", "GraceAshcroft_Icon_Civilization_"),
            ),
            TextContract(
                mod_root / "Text/GraceAshcroft_zh_Hans_CN.sql",
                required=(
                    "LOC_CIVILIZATION_ELPIS_PROTOCOL_NAME",
                    "LOC_LEADER_GRACE_ASHCROFT_NAME",
                    "LOC_DISTRICT_GRACE_ARK_NAME",
                    "LOC_RESOURCE_INFECTED_BLOOD_NAME",
                    "溶血剂 III",
                    "稳定剂 III",
                    "类固醇 III",
                    "我始终无法忘记那一天",
                    "研究“货币”后",
                    "战略物资合成",
                    "病理人才资助",
                ),
                forbidden=("罗兹山疗养院", "隔离协议复盘", "消耗 3 感染者血液"),
            ),
        )
    )


def check_blp_entries(root: Path) -> None:
    blp_root = root / "mods" / "GraceAshcroft" / "Platforms" / "Windows" / "BLPs"
    ui_texture = blp_root / "GraceUITexture.blp"
    resource_texture = blp_root / "GraceResourceIconsV2.blp"
    leader_fallbacks = blp_root / "LeaderFallbacks.blp"
    for value in (
        "GraceAshcroft_Icon_Leader_50",
        "GraceAshcroft_Icon_Hemolytic_50",
        "GraceCivilization_ElpisProtocol_V2_50",
    ):
        require_binary_contains(ui_texture, value)
    require_binary_not_contains(ui_texture, "GraceAshcroft_Icon_InfectedBlood_")

    for size in (22, 38, 50, 64, 256):
        require_binary_contains(resource_texture, f"GraceResource_InfectedBlood_V2_{size}")
    require_binary_not_contains(resource_texture, "GraceResource_InfectedBlood_V1_")
    require_binary_contains(leader_fallbacks, "GraceAshcroft_Foreground_Fallback")


def check_docs(root: Path) -> None:
    apply_text_contracts(
        (
            TextContract(
                root / "docs/civ6-mod-workflow.md",
                required=("tools/<mod>/", "check_static.py", "runtime mod"),
            ),
            TextContract(
                root / "docs/mods/grace-ashcroft-assets.md",
                required=("check_static.py", "GraceResourceIconsV2.blp", "V2"),
            ),
            TextContract(
                root / "docs/mods/grace-ashcroft-troubleshooting.md",
                required=("Old saves", "FireTuner", "ApplyFileQuery", "IconManager"),
            ),
        )
    )


def run(root: Path) -> None:
    check_runtime_layout(root)
    check_asset_workspace(root)
    check_build_scripts(root)
    check_mod_contract(root)
    check_blp_entries(root)
    check_docs(root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="repository root")
    args = parser.parse_args(argv)
    try:
        run(args.root.resolve())
    except ValidationError as error:
        print(f"Grace Ashcroft static validation failed: {error}", file=sys.stderr)
        return 1
    print("Grace Ashcroft mod static validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
