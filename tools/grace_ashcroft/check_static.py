#!/usr/bin/env python3
"""Static contracts for the deployable Grace Ashcroft Civilization VI mod.

PowerShell remains responsible for Windows-only orchestration (Asset Cooker,
deployment, and workspace cleanup).  This module owns deterministic repository
validation so its rules can be imported, unit-tested, and reused by future mods.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.common.civ6_static_checks import (
    TextContract,
    ValidationError,
    apply_text_contracts,
    require_binary_contains,
    require_binary_not_contains,
    require_dds_rgba,
    require_file,
    runtime_mod_paths,
)
from tools.common.civ6_mod_config import ModBuildConfig, load_mod_config


def grace_config(root: Path) -> ModBuildConfig:
    return load_mod_config(root / "assets" / "GraceAshcroft" / "mod-build.toml", repo_root=root)


def check_runtime_layout(root: Path) -> None:
    config = grace_config(root)
    mod_root = config.runtime_root
    forbidden = runtime_mod_paths(
        mod_root,
        project_file_names={
            f"{config.slug}.Art.xml",
            f"{config.slug}.civ6proj",
            f"{config.slug}.civ6sln",
        },
    )
    if forbidden:
        listed = ", ".join(str(path) for path in forbidden)
        raise ValidationError(f"Runtime mod contains build-only paths: {listed}")

    for relative in (
        f"{config.slug}.modinfo",
        f"{config.slug}.dep",
        "Data/Config.sql",
        "Data/Gameplay.sql",
        "Data/GraceColors.xml",
        "Icons/GraceIcons.sql",
        "Scripts/GraceGameplay.lua",
        "Text/GraceAshcroft_zh_Hans_CN.sql",
        "ArtDefs/Civilizations.artdef",
        "ArtDefs/Districts.artdef",
        "ArtDefs/FallbackLeaders.artdef",
        f"Platforms/Windows/BLPs/{config.package('ui')}.blp",
        f"Platforms/Windows/BLPs/{config.package('resource')}.blp",
        f"Platforms/Windows/BLPs/{config.package('leader_fallback')}.blp",
    ):
        require_file(mod_root / relative)


def check_asset_workspace(root: Path) -> None:
    config = grace_config(root)
    asset_root = config.asset_root
    project_root = config.project_root
    required = (
        asset_root / "source/icons/GraceAshcroft_Civilization.png",
        asset_root / "source/icons/GraceAshcroft_InfectedBlood.png",
        asset_root / "source/icons/GraceAshcroft_LeaderIcon.png",
        asset_root / "leader-art/png/GraceAshcroft_Background.png",
        asset_root / "leader-art/png/GraceAshcroft_Foreground.png",
        asset_root / "leader-art/png/GraceAshcroft_LoadingScene.png",
        asset_root / "leader-art/png/GraceAshcroft_LoadingBlank.png",
        asset_root / f"cooker/XLPs/{config.package('ui')}.xlp",
        asset_root / f"cooker/XLPs/{config.package('resource')}.xlp",
        asset_root / "cooker/XLPs/leaderfallbacks.xlp",
        project_root / f"{config.slug}.Art.xml",
        project_root / f"{config.slug}.civ6proj",
        project_root / f"{config.slug}.civ6sln",
    )
    for path in required:
        require_file(path)

    require_dds_rgba(asset_root / "leader-art/dds/GraceAshcroft_Background.dds", 2048, 1024)
    require_dds_rgba(asset_root / "leader-art/dds/GraceAshcroft_Foreground.dds", 1024, 2048)
    require_dds_rgba(asset_root / "leader-art/dds/GraceAshcroft_LoadingScene.dds", 2048, 1024)
    require_dds_rgba(asset_root / "leader-art/dds/GraceAshcroft_LoadingBlank.dds", 8, 8)


def check_build_scripts(root: Path) -> None:
    config = grace_config(root)
    tools_root = root / "tools"
    legacy_checker = tools_root / "_check_grace_mod_static_impl.ps1"
    if legacy_checker.exists():
        raise ValidationError(f"Obsolete PowerShell checker must be removed: {legacy_checker}")
    apply_text_contracts(
        (
            TextContract(
                tools_root / "grace_ashcroft/build_assets.py",
                required=(
                    "from tools.common.civ6_mod_config import load_mod_config",
                    "CONFIG = load_mod_config",
                    "CIVILIZATION_ASSET_VERSION = CONFIG.asset_revision",
                    "INFECTED_BLOOD_ASSET_VERSION = CONFIG.asset_revision",
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
                    "cook_assets.py",
                    "--sdk-root",
                    "--cooker-path",
                    "--dry-run",
                ),
                forbidden=("$infectedBloodAssetVersion", "$resourcePackage"),
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
    config = grace_config(root)
    mod_root = config.runtime_root
    apply_text_contracts(
        (
            TextContract(
                mod_root / f"{config.slug}.modinfo",
                required=(
                    f'version="{config.release_version}"',
                    "Data/Config.sql",
                    "Data/Gameplay.sql",
                    "Icons/GraceIcons.sql",
                    f"{config.slug}.dep",
                    f"Platforms/Windows/BLPs/{config.package('ui')}.blp",
                    f"Platforms/Windows/BLPs/{config.package('resource')}.blp",
                    f"Platforms/Windows/BLPs/{config.package('leader_fallback')}.blp",
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
                    f"ICON_ATLAS_GRACE_CIVILIZATION_V{config.asset_revision}",
                    f"ICON_ATLAS_GRACE_CIVILIZATION_FONT_V{config.asset_revision}",
                    f"ICON_ATLAS_GRACE_INFECTED_BLOOD_V{config.asset_revision}",
                    f"ICON_ATLAS_GRACE_INFECTED_BLOOD_FONT_V{config.asset_revision}",
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
    config = grace_config(root)
    blp_root = config.runtime_root / "Platforms" / "Windows" / "BLPs"
    ui_texture = blp_root / f"{config.package('ui')}.blp"
    resource_texture = blp_root / f"{config.package('resource')}.blp"
    leader_fallbacks = blp_root / f"{config.package('leader_fallback')}.blp"
    for value in (
        "GraceAshcroft_Icon_Leader_50",
        "GraceAshcroft_Icon_Hemolytic_50",
        f"GraceCivilization_ElpisProtocol_V{config.asset_revision}_50",
    ):
        require_binary_contains(ui_texture, value)
    require_binary_not_contains(ui_texture, "GraceAshcroft_Icon_InfectedBlood_")

    for size in (22, 38, 50, 64, 256):
        require_binary_contains(
            resource_texture, f"GraceResource_InfectedBlood_V{config.asset_revision}_{size}"
        )
    require_binary_not_contains(resource_texture, "GraceResource_InfectedBlood_V1_")
    require_binary_contains(leader_fallbacks, "GraceAshcroft_Foreground_Fallback")


def check_docs(root: Path) -> None:
    config = grace_config(root)
    apply_text_contracts(
        (
            TextContract(
                root / "docs/civ6-mod-workflow.md",
                required=("tools/<mod>/", "check_static.py", "runtime mod", "mod-build.toml"),
            ),
            TextContract(
                root / "docs/civ6/README.md",
                required=("Asset pipeline", "Runtime patterns", "scaffold_civ6_leader_mod.py"),
            ),
            TextContract(
                root / "docs/civ6/asset-pipeline.md",
                required=("PF_R8G8B8A8_UNORM", "FindIconAtlasNearestSize", "CIV6_SDK_ROOT"),
            ),
            TextContract(
                root / "docs/civ6/runtime-patterns.md",
                required=("PlayerProperty", "unit:ChangeDamage", "civilization and leader"),
            ),
            TextContract(
                root / "docs/mods/grace-ashcroft-assets.md",
                required=("check_static.py", f"{config.package('resource')}.blp", "V2"),
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
