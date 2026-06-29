#!/usr/bin/env python3
"""Build Grace Ashcroft UI and resource icon assets for Civilization VI."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.common.civ6_texture import (  # noqa: E402
    alpha_bbox,
    crop_alpha_square,
    resize_icon,
    texture_instance_xml,
    write_rgba_dds,
)

ASSET_ROOT = ROOT / "assets" / "GraceAshcroft"
SOURCE_DIR = ASSET_ROOT / "source" / "icons"
LEADER_ART_DDS_DIR = ASSET_ROOT / "leader-art" / "dds"
GENERATED_PNG_DIR = ASSET_ROOT / "generated" / "icons" / "png"
GENERATED_DDS_DIR = ASSET_ROOT / "generated" / "icons" / "dds"
MOD_ROOT = ROOT / "mods" / "GraceAshcroft"
MOD_IMAGES = MOD_ROOT / "Images"
MOD_TEXTURES = MOD_IMAGES / "Textures"
GRACE_UI_XLP = MOD_ROOT / "XLPs" / "GraceUITexture.xlp"

INFECTED_BLOOD_ASSET_VERSION = 2
INFECTED_BLOOD_PACKAGE_NAME = f"GraceResourceIconsV{INFECTED_BLOOD_ASSET_VERSION}"
INFECTED_BLOOD_ENTRY_PREFIX = (
    f"GraceResource_InfectedBlood_V{INFECTED_BLOOD_ASSET_VERSION}"
)
GRACE_RESOURCE_XLP = MOD_ROOT / "XLPs" / f"{INFECTED_BLOOD_PACKAGE_NAME}.xlp"
GRACE_RESOURCE_BLP = (
    MOD_ROOT / "Platforms" / "Windows" / "BLPs" / f"{INFECTED_BLOOD_PACKAGE_NAME}.blp"
)

ICON_SIZES = (22, 30, 32, 38, 50, 64, 80, 256)
LEADER_ICON_SIZES = (22, 30, 32, 38, 45, 48, 50, 55, 64, 80, 256)
CIVILIZATION_ICON_SIZES = (22, 30, 32, 36, 38, 44, 45, 48, 50, 64, 80, 128, 200, 256)
INFECTED_BLOOD_ICON_SIZES = (22, 38, 50, 64, 256)
INFECTED_BLOOD_SOURCE = "GraceAshcroft_InfectedBlood.png"

ICONS = {
    "GraceAshcroft_Icon_Civilization": "GraceAshcroft_Civilization.png",
    "GraceAshcroft_Icon_Hemolytic": "GraceAshcroft_Hemolytic.png",
    "GraceAshcroft_Icon_Stabilizer": "GraceAshcroft_Stabilizer.png",
    "GraceAshcroft_Icon_Steroid": "GraceAshcroft_Steroid.png",
    "GraceAshcroft_Icon_Leader": "GraceAshcroft_LeaderIcon.png",
}

ICON_SIZE_OVERRIDES = {
    "GraceAshcroft_Icon_Civilization": CIVILIZATION_ICON_SIZES,
    "GraceAshcroft_Icon_Leader": LEADER_ICON_SIZES,
}

LOADING_DDS_INPUTS = (
    "GraceAshcroft_Background.dds",
    "GraceAshcroft_Foreground.dds",
    "GraceAshcroft_LoadingScene.dds",
    "GraceAshcroft_LoadingBlank.dds",
)

BASE_XLP_ENTRIES = (
    ("IMG_LOADING_BACKGROUND_GRACE_ASHCROFT", "GraceAshcroft_Background_UI"),
    ("IMG_LOADING_FOREGROUND_GRACE_ASHCROFT", "GraceAshcroft_Foreground_UI"),
    ("IMG_LOADING_SCENE_GRACE_ASHCROFT", "GraceAshcroft_LoadingScene_UI"),
    ("IMG_LOADING_FOREGROUND_BLANK_GRACE_ASHCROFT", "GraceAshcroft_LoadingBlank_UI"),
)

LEGACY_INFECTED_BLOOD_PREFIX = "GraceAshcroft_Icon_InfectedBlood_"
VERSIONED_INFECTED_BLOOD_PATTERN = re.compile(r"^GraceResource_InfectedBlood_V\d+_\d+$")
VERSIONED_PACKAGE_PATTERN = re.compile(r"^GraceResourceIconsV\d+$")


def prepare_icon(source: Path, entry_base: str) -> Image.Image:
    image = Image.open(source).convert("RGBA")
    if entry_base == "GraceAshcroft_Icon_Leader":
        left, _, right, _ = alpha_bbox(image)
        width = right - left
        center_x = (left + right) // 2
        side = min(image.width, image.height, max(width + 96, 430))
        crop_left = max(0, min(center_x - side // 2, image.width - side))
        return image.crop((crop_left, 0, crop_left + side, side))
    return crop_alpha_square(image, padding_ratio=0.18)


def icon_sizes_for(entry_base: str) -> tuple[int, ...]:
    return ICON_SIZE_OVERRIDES.get(entry_base, ICON_SIZES)


def infected_blood_entry_name(size: int) -> str:
    return f"{INFECTED_BLOOD_ENTRY_PREFIX}_{size}"


def ui_icon_entry_names() -> list[str]:
    return [
        f"{entry_base}_{size}"
        for entry_base in ICONS
        for size in icon_sizes_for(entry_base)
    ]


def infected_blood_entry_names() -> list[str]:
    return [infected_blood_entry_name(size) for size in INFECTED_BLOOD_ICON_SIZES]


def temporary_mod_dds_paths() -> list[Path]:
    paths = [MOD_IMAGES / dds_name for dds_name in LOADING_DDS_INPUTS]
    paths.extend(MOD_IMAGES / f"{entry}.dds" for entry in ui_icon_entry_names())
    paths.extend(MOD_IMAGES / f"{entry}.dds" for entry in infected_blood_entry_names())
    return paths


def _is_infected_blood_stem(stem: str) -> bool:
    return stem.startswith(LEGACY_INFECTED_BLOOD_PREFIX) or bool(
        VERSIONED_INFECTED_BLOOD_PATTERN.fullmatch(stem)
    )


def cleanup_obsolete_infected_blood_assets() -> int:
    """Remove stale V1/V2/Vn infected-blood files before generating current assets."""
    expected_entries = set(infected_blood_entry_names())
    removed = 0

    for directory, suffixes in (
        (GENERATED_PNG_DIR, {".png"}),
        (GENERATED_DDS_DIR, {".dds"}),
        (MOD_TEXTURES, {".tex"}),
        (MOD_IMAGES, {".dds"}),
    ):
        if not directory.exists():
            continue
        for path in directory.iterdir():
            if not path.is_file() or path.suffix.lower() not in suffixes:
                continue
            if _is_infected_blood_stem(path.stem) and path.stem not in expected_entries:
                path.unlink()
                removed += 1

    xlp_dir = MOD_ROOT / "XLPs"
    if xlp_dir.exists():
        for path in xlp_dir.glob("GraceResourceIconsV*.xlp"):
            if (
                VERSIONED_PACKAGE_PATTERN.fullmatch(path.stem)
                and path.stem != INFECTED_BLOOD_PACKAGE_NAME
            ):
                path.unlink()
                removed += 1

    blp_dir = MOD_ROOT / "Platforms" / "Windows" / "BLPs"
    if blp_dir.exists():
        for path in blp_dir.glob("GraceResourceIconsV*.blp"):
            if (
                VERSIONED_PACKAGE_PATTERN.fullmatch(path.stem)
                and path.stem != INFECTED_BLOOD_PACKAGE_NAME
            ):
                path.unlink()
                removed += 1

    if removed:
        print(f"Removed {removed} obsolete infected-blood asset files.")
    return removed


def copy_loading_cooker_inputs() -> None:
    for dds_name in LOADING_DDS_INPUTS:
        source = LEADER_ART_DDS_DIR / dds_name
        if not source.exists():
            raise FileNotFoundError(f"Missing loading DDS source: {source}")
        shutil.copyfile(source, MOD_IMAGES / dds_name)


def cleanup_mod_dds() -> None:
    removed = 0
    for target in temporary_mod_dds_paths():
        if target.exists():
            target.unlink()
            removed += 1
    print(f"Removed {removed} temporary cooker DDS files from {MOD_IMAGES}.")


def xlp_entry(entry_id: str, object_name: str) -> str:
    return f'''\t\t<Element>
\t\t\t<m_EntryID text="{entry_id}"/>
\t\t\t<m_ObjectName text="{object_name}"/>
\t\t</Element>'''


def xlp_document(package_name: str, entries: list[tuple[str, str]]) -> str:
    entry_block = "\n".join(xlp_entry(entry_id, object_name) for entry_id, object_name in entries)
    return f'''<?xml version="1.0" encoding="UTF-8" ?>
<AssetObjects..XLP>
\t<m_Version>
\t\t<major>4</major>
\t\t<minor>0</minor>
\t\t<build>410</build>
\t\t<revision>536</revision>
\t</m_Version>
\t<m_ClassName text="UITexture"/>
\t<m_PackageName text="{package_name}"/>
\t<m_Entries>
{entry_block}
\t</m_Entries>
\t<m_AllowedPlatforms>
\t\t<Element>WINDOWS</Element>
\t\t<Element>LINUX</Element>
\t\t<Element>MACOS</Element>
\t\t<Element>IOS</Element>
\t</m_AllowedPlatforms>
</AssetObjects..XLP>
'''


def write_texture_files(entry_name: str, size: int, icon: Image.Image) -> None:
    png_target = GENERATED_PNG_DIR / f"{entry_name}.png"
    dds_target = GENERATED_DDS_DIR / f"{entry_name}.dds"
    cooker_dds_target = MOD_IMAGES / f"{entry_name}.dds"
    tex_target = MOD_TEXTURES / f"{entry_name}.tex"

    png_target.parent.mkdir(parents=True, exist_ok=True)
    icon.save(png_target)
    write_rgba_dds(icon, dds_target)
    write_rgba_dds(icon, cooker_dds_target)
    tex_target.write_text(texture_instance_xml(entry_name, size), encoding="utf-8", newline="\n")


def build() -> None:
    cleanup_obsolete_infected_blood_assets()
    GENERATED_PNG_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED_DDS_DIR.mkdir(parents=True, exist_ok=True)
    MOD_IMAGES.mkdir(parents=True, exist_ok=True)
    MOD_TEXTURES.mkdir(parents=True, exist_ok=True)
    copy_loading_cooker_inputs()

    ui_entries: list[str] = []
    for entry_base, source_name in ICONS.items():
        source = SOURCE_DIR / source_name
        if not source.exists():
            raise FileNotFoundError(f"Missing source icon: {source}")
        prepared = prepare_icon(source, entry_base)
        for size in icon_sizes_for(entry_base):
            entry_name = f"{entry_base}_{size}"
            ui_entries.append(entry_name)
            write_texture_files(entry_name, size, resize_icon(prepared, size))

    resource_source = SOURCE_DIR / INFECTED_BLOOD_SOURCE
    if not resource_source.exists():
        raise FileNotFoundError(f"Missing source icon: {resource_source}")
    resource_prepared = prepare_icon(resource_source, "GraceResource_InfectedBlood")
    resource_entries: list[str] = []
    for size in INFECTED_BLOOD_ICON_SIZES:
        entry_name = infected_blood_entry_name(size)
        resource_entries.append(entry_name)
        write_texture_files(entry_name, size, resize_icon(resource_prepared, size))

    ui_xlp_entries = list(BASE_XLP_ENTRIES)
    ui_xlp_entries.extend((entry, entry) for entry in ui_entries)
    GRACE_UI_XLP.write_text(
        xlp_document("GraceUITexture", ui_xlp_entries), encoding="utf-8", newline="\n"
    )
    GRACE_RESOURCE_XLP.write_text(
        xlp_document(INFECTED_BLOOD_PACKAGE_NAME, [(entry, entry) for entry in resource_entries]),
        encoding="utf-8",
        newline="\n",
    )

    print(
        f"Generated {len(ui_entries)} UI icon entries and "
        f"{len(resource_entries)} infected-blood entries in {INFECTED_BLOOD_PACKAGE_NAME}."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cleanup-mod-dds",
        action="store_true",
        help="Remove temporary DDS cooker inputs from mods/GraceAshcroft/Images.",
    )
    parser.add_argument(
        "--cleanup-obsolete",
        action="store_true",
        help="Only remove obsolete infected-blood assets and exit.",
    )
    args = parser.parse_args(argv)

    if args.cleanup_mod_dds:
        cleanup_mod_dds()
    elif args.cleanup_obsolete:
        cleanup_obsolete_infected_blood_assets()
    else:
        build()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
