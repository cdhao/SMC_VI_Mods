#!/usr/bin/env python3
"""Validate the complete Chuuni Society Civilization VI asset chain."""

from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.common.civ6_mod_config import load_mod_config  # noqa: E402
from tools.common.civ6_static_checks import (  # noqa: E402
    TextContract,
    ValidationError,
    apply_text_contracts,
    require_binary_contains,
    require_dds_rgba,
    require_file,
)


SOURCE_NAMES = (
    "文明 Logo.png", "六花领袖头像.png", "六花载入前景.png", "载入背景.png",
    "极东魔术昼寝结社区域图标.png", "部室魔法阵建筑图标.png", "中二值资源图标.png",
    "奇美拉总督头像.png", "不可视境界线改良设施图标.png", "魔法阵传送按钮图标.png",
)


def read_xlp_inventory(
    xlp_path: Path,
    *,
    expected_package: str,
    expected_class: str,
) -> dict[str, str]:
    require_file(xlp_path)
    root = ET.parse(xlp_path).getroot()
    package = root.find("m_PackageName")
    class_name = root.find("m_ClassName")
    if package is None or package.get("text") != expected_package:
        raise ValidationError(f"Unexpected package name in {xlp_path}: {None if package is None else package.get('text')}")
    if class_name is None or class_name.get("text") != expected_class:
        raise ValidationError(f"Unexpected XLP class in {xlp_path}: {None if class_name is None else class_name.get('text')}")

    inventory: dict[str, str] = {}
    object_names: set[str] = set()
    for element in root.findall("./m_Entries/Element"):
        entry = element.find("m_EntryID")
        object_name = element.find("m_ObjectName")
        entry_id = None if entry is None else entry.get("text")
        object_id = None if object_name is None else object_name.get("text")
        if not entry_id or not object_id:
            raise ValidationError(f"Incomplete XLP entry in {xlp_path}")
        if entry_id in inventory or object_id in object_names:
            raise ValidationError(f"Duplicate XLP entry or object in {xlp_path}: {entry_id}/{object_id}")
        inventory[entry_id] = object_id
        object_names.add(object_id)
    return inventory


def validate_package_inventory(
    *,
    xlp_path: Path,
    tex_root: Path,
    dds_roots: tuple[Path, ...],
    blp_path: Path,
    expected_package: str,
    expected_class: str,
    expected_entries: int,
) -> dict[str, str]:
    inventory = read_xlp_inventory(
        xlp_path,
        expected_package=expected_package,
        expected_class=expected_class,
    )
    if len(inventory) != expected_entries:
        raise ValidationError(f"Expected {expected_entries} entries in {xlp_path}, found {len(inventory)}")

    for entry_id, object_name in inventory.items():
        tex_path = tex_root / f"{object_name}.tex"
        require_file(tex_path)
        tex_root_node = ET.parse(tex_path).getroot()
        tex_name = tex_root_node.find("m_Name")
        relative = tex_root_node.find("./m_DataFiles/Element/m_RelativePath")
        if tex_name is None or tex_name.get("text") != object_name or relative is None or not relative.get("text"):
            raise ValidationError(f"Invalid TEX inventory record: {tex_path}")
        dds_name = Path(relative.get("text", "")).name
        matches = [root / dds_name for root in dds_roots if (root / dds_name).is_file()]
        if len(matches) != 1:
            raise ValidationError(f"Expected exactly one source DDS for {object_name}: {dds_name}")
        require_binary_contains(blp_path, entry_id)
    return inventory


def validate_runtime_files(mod_root: Path) -> None:
    modinfo = mod_root / "ChuuniSociety.modinfo"
    root = ET.parse(modinfo).getroot()
    declared = {element.text for element in root.findall("./Files/File") if element.text}
    for relative in declared:
        require_file(mod_root / relative)
    expected_blps = {"ChuuniUITextureV1.blp", "ChuuniLeaderFallbacks.blp"}
    actual_blps = {path.name for path in (mod_root / "Platforms/Windows/BLPs").glob("*.blp")}
    if actual_blps != expected_blps:
        raise ValidationError(f"Runtime BLP inventory mismatch: expected {sorted(expected_blps)}, found {sorted(actual_blps)}")


def validate_leader_icon_alpha(asset_root: Path) -> None:
    icon_path = asset_root / "generated/icons/png/Chuuni_Icon_Rikka_256.png"
    require_file(icon_path)
    with Image.open(icon_path) as image:
        alpha = image.convert("RGBA").getchannel("A")
        corners = (
            alpha.getpixel((0, 0)),
            alpha.getpixel((alpha.width - 1, 0)),
            alpha.getpixel((0, alpha.height - 1)),
            alpha.getpixel((alpha.width - 1, alpha.height - 1)),
        )
        if corners != (0, 0, 0, 0):
            raise ValidationError(f"Leader icon must have transparent circular corners: {icon_path}")
        if sum(alpha.histogram()[1:255]) == 0:
            raise ValidationError(f"Leader icon must have an antialiased alpha edge: {icon_path}")


def run(root: Path) -> None:
    config = load_mod_config(root / "assets/ChuuniSociety/mod-build.toml", repo_root=root)
    asset_root = config.asset_root
    mod_root = config.runtime_root
    for name in SOURCE_NAMES:
        require_file(asset_root / name)
    for relative in (
        "leader-art/png/Chuuni_LoadingScene.png",
        "generated/icons/png/ChuuniCivilization_V1_22.png",
    ):
        require_file(asset_root / relative)
    for name, width, height in (
        ("Chuuni_Background.dds", 2048, 1024),
        ("Chuuni_Foreground.dds", 1024, 2048),
        ("Chuuni_LoadingScene.dds", 2048, 1024),
        ("Chuuni_LoadingBlank.dds", 8, 8),
    ):
        require_dds_rgba(asset_root / "leader-art/dds" / name, width, height)

    tex_root = asset_root / "cooker/Images/Textures"
    dds_roots = (asset_root / "generated/icons/dds", asset_root / "leader-art/dds")
    ui_inventory = validate_package_inventory(
        xlp_path=asset_root / "cooker/XLPs" / f"{config.package('ui')}.xlp",
        tex_root=tex_root,
        dds_roots=dds_roots,
        blp_path=mod_root / "Platforms/Windows/BLPs" / f"{config.package('ui')}.blp",
        expected_package=config.package("ui"),
        expected_class="UITexture",
        expected_entries=67,
    )
    fallback_inventory = validate_package_inventory(
        xlp_path=asset_root / "cooker/XLPs/leaderfallbacks.xlp",
        tex_root=tex_root,
        dds_roots=dds_roots,
        blp_path=mod_root / "Platforms/Windows/BLPs" / f"{config.package('leader_fallback')}.blp",
        expected_package=config.package("leader_fallback"),
        expected_class="LeaderFallback",
        expected_entries=1,
    )
    expected_tex = {f"{name}.tex" for name in (*ui_inventory.values(), *fallback_inventory.values())}
    actual_tex = {path.name for path in tex_root.glob("*.tex")}
    if actual_tex != expected_tex:
        raise ValidationError(f"TEX inventory mismatch: expected {len(expected_tex)}, found {len(actual_tex)}")
    expected_dds = set()
    for tex_name in expected_tex:
        tex_root_node = ET.parse(tex_root / tex_name).getroot()
        relative = tex_root_node.find("./m_DataFiles/Element/m_RelativePath")
        expected_dds.add(Path(relative.get("text", "")).name)
    actual_dds = {path.name for dds_root in dds_roots for path in dds_root.glob("*.dds")}
    if actual_dds != expected_dds:
        raise ValidationError(f"DDS inventory mismatch: expected {len(expected_dds)}, found {len(actual_dds)}")
    validate_leader_icon_alpha(asset_root)
    validate_runtime_files(mod_root)

    apply_text_contracts((
        TextContract(
            mod_root / "ChuuniSociety.dep",
            required=(
                "ChuuniUITextureV1.blp",
                "ChuuniLeaderFallbacks.blp",
                "FallbackLeaders.artdef",
                "Districts.artdef",
                "StrategicView_Translate",
                "WorldView_Translate",
                "Audio",
            ),
            forbidden=("Grace",),
        ),
        TextContract(
            root / "projects/ChuuniSociety/ChuuniSociety.Art.xml",
            required=("Districts.artdef", "StrategicView_Translate", "WorldView_Translate", "Audio"),
        ),
        TextContract(
            mod_root / "ArtDefs/Districts.artdef",
            required=(
                "DISTRICT_CHUUNI_SOCIETY",
                "DISTRICT_HOLY_SITE",
                "HolySite",
                "HolySite_Pillaged",
                "HolySite_UnderConstruction",
            ),
        ),
        TextContract(mod_root / "ArtDefs/FallbackLeaders.artdef", required=("LEADER_RIKKA_TAKANASHI", "FALLBACK_NEUTRAL_RIKKA_TAKANASHI", "ChuuniLeaderFallbacks")),
        TextContract(mod_root / "Icons/ChuuniIcons.sql", required=("ICON_ATLAS_CHUUNI_CIVILIZATION_V1", "ICON_ATLAS_CHUUNI_LEADER", "ICON_ATLAS_CHUUNI_GAMEPLAY", "ICON_ATLAS_CHUUNI_VALUE")),
        TextContract(mod_root / "ChuuniSociety.modinfo", required=("ChuuniSociety.dep", "ArtDefs/Districts.artdef", "ChuuniUITextureV1.blp", "ChuuniLeaderFallbacks.blp", "UpdateArt")),
    ))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    try:
        run(args.root.resolve())
    except (ValidationError, ValueError) as error:
        print(f"[ChuuniSociety assets] validation failed: {error}", file=sys.stderr)
        return 1
    print("[ChuuniSociety assets] static checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
