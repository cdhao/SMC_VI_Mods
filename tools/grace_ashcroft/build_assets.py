#!/usr/bin/env python3
"""Build Grace Ashcroft UI and resource icon assets for Civilization VI."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.common.civ6_texture import (  # noqa: E402
    alpha_bbox,
    crop_alpha_square,
    resize_icon,
    save_png_atomic,
    texture_instance_xml,
    write_bytes_atomic,
    write_rgba_dds,
)
from tools.common.civ6_mod_config import load_mod_config  # noqa: E402

CONFIG = load_mod_config(ROOT / "assets" / "GraceAshcroft" / "mod-build.toml", repo_root=ROOT)
ASSET_ROOT = CONFIG.asset_root
SOURCE_DIR = ASSET_ROOT / "source" / "icons"
LEADER_ART_DDS_DIR = ASSET_ROOT / "leader-art" / "dds"
LEADER_ART_PNG_DIR = ASSET_ROOT / "leader-art" / "png"
GENERATED_PNG_DIR = ASSET_ROOT / "generated" / "icons" / "png"
GENERATED_DDS_DIR = ASSET_ROOT / "generated" / "icons" / "dds"
MOD_ROOT = CONFIG.runtime_root
COOKER_ROOT = ASSET_ROOT / "cooker"
COOKER_IMAGES = COOKER_ROOT / "Images"
COOKER_TEXTURES = COOKER_IMAGES / "Textures"
COOKER_XLPS = COOKER_ROOT / "XLPs"
RUNTIME_BLP_DIR = MOD_ROOT / "Platforms" / "Windows" / "BLPs"
GRACE_UI_PACKAGE_NAME = CONFIG.package("ui")
GRACE_UI_XLP = COOKER_XLPS / f"{GRACE_UI_PACKAGE_NAME}.xlp"

CIVILIZATION_ASSET_VERSION = CONFIG.asset_revision
CIVILIZATION_ENTRY_PREFIX = (
    f"GraceCivilization_ElpisProtocol_V{CIVILIZATION_ASSET_VERSION}"
)
INFECTED_BLOOD_ASSET_VERSION = CONFIG.asset_revision
INFECTED_BLOOD_PACKAGE_NAME = CONFIG.package("resource")
INFECTED_BLOOD_ENTRY_PREFIX = (
    f"GraceResource_InfectedBlood_V{INFECTED_BLOOD_ASSET_VERSION}"
)
GRACE_RESOURCE_XLP = COOKER_XLPS / f"{INFECTED_BLOOD_PACKAGE_NAME}.xlp"

ICON_SIZES = (22, 30, 32, 38, 50, 64, 80, 256)
LEADER_ICON_SIZES = (22, 30, 32, 38, 45, 48, 50, 55, 64, 80, 256)
CIVILIZATION_ICON_SIZES = (22, 30, 32, 36, 38, 44, 45, 48, 50, 64, 80, 128, 200, 256)
INFECTED_BLOOD_ICON_SIZES = (22, 38, 50, 64, 256)
CIVILIZATION_ICON_SOURCE = "GraceAshcroft_Civilization.png"
INFECTED_BLOOD_SOURCE = "GraceAshcroft_InfectedBlood.png"

ICONS = {
    "GraceAshcroft_Icon_Hemolytic": "GraceAshcroft_Hemolytic.png",
    "GraceAshcroft_Icon_Stabilizer": "GraceAshcroft_Stabilizer.png",
    "GraceAshcroft_Icon_Steroid": "GraceAshcroft_Steroid.png",
    "GraceAshcroft_Icon_Leader": "GraceAshcroft_LeaderIcon.png",
}

ICON_SIZE_OVERRIDES = {
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

LOADING_ENTRIES = (
    ("IMG_LOADING_BACKGROUND_GRACE_ASHCROFT", "GraceAshcroft_Background_UI", "GraceAshcroft_Background.dds", 2048, 1024),
    ("IMG_LOADING_FOREGROUND_GRACE_ASHCROFT", "GraceAshcroft_Foreground_UI", "GraceAshcroft_Foreground.dds", 1024, 2048),
    ("IMG_LOADING_SCENE_GRACE_ASHCROFT", "GraceAshcroft_LoadingScene_UI", "GraceAshcroft_LoadingScene.dds", 2048, 1024),
    ("IMG_LOADING_FOREGROUND_BLANK_GRACE_ASHCROFT", "GraceAshcroft_LoadingBlank_UI", "GraceAshcroft_LoadingBlank.dds", 8, 8),
)

LEGACY_INFECTED_BLOOD_PREFIX = "GraceAshcroft_Icon_InfectedBlood_"
VERSIONED_INFECTED_BLOOD_PATTERN = re.compile(r"^GraceResource_InfectedBlood_V\d+_\d+$")
VERSIONED_PACKAGE_PATTERN = re.compile(r"^GraceResourceIconsV\d+$")
LEGACY_CIVILIZATION_PREFIX = "GraceAshcroft_Icon_Civilization_"
VERSIONED_CIVILIZATION_PATTERN = re.compile(r"^GraceCivilization_ElpisProtocol_V\d+_\d+$")
VERSIONED_CIVILIZATION_PACKAGE_PATTERN = re.compile(r"^GraceCivilizationIconsV\d+$")


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


def civilization_entry_name(size: int) -> str:
    return f"{CIVILIZATION_ENTRY_PREFIX}_{size}"


def ui_icon_entry_names() -> list[str]:
    return [
        f"{entry_base}_{size}"
        for entry_base in ICONS
        for size in icon_sizes_for(entry_base)
    ]


def infected_blood_entry_names() -> list[str]:
    return [infected_blood_entry_name(size) for size in INFECTED_BLOOD_ICON_SIZES]


def civilization_entry_names() -> list[str]:
    return [civilization_entry_name(size) for size in CIVILIZATION_ICON_SIZES]


def temporary_cooker_dds_paths() -> list[Path]:
    paths = [COOKER_IMAGES / dds_name for dds_name in LOADING_DDS_INPUTS]
    paths.extend(COOKER_IMAGES / f"{entry}.dds" for entry in ui_icon_entry_names())
    paths.extend(COOKER_IMAGES / f"{entry}.dds" for entry in civilization_entry_names())
    paths.extend(COOKER_IMAGES / f"{entry}.dds" for entry in infected_blood_entry_names())
    return paths


def _is_infected_blood_stem(stem: str) -> bool:
    return stem.startswith(LEGACY_INFECTED_BLOOD_PREFIX) or bool(
        VERSIONED_INFECTED_BLOOD_PATTERN.fullmatch(stem)
    )


def _is_civilization_stem(stem: str) -> bool:
    return stem.startswith(LEGACY_CIVILIZATION_PREFIX) or bool(
        VERSIONED_CIVILIZATION_PATTERN.fullmatch(stem)
    )


def cleanup_obsolete_civilization_assets() -> int:
    """Remove stale civilization emblem files before generating current assets."""
    expected_entries = set(civilization_entry_names())
    removed = 0

    for directory, suffixes in (
        (GENERATED_PNG_DIR, {".png"}),
        (GENERATED_DDS_DIR, {".dds"}),
        (COOKER_TEXTURES, {".tex"}),
        (COOKER_IMAGES, {".dds"}),
    ):
        if not directory.exists():
            continue
        for path in directory.iterdir():
            if not path.is_file() or path.suffix.lower() not in suffixes:
                continue
            if _is_civilization_stem(path.stem) and path.stem not in expected_entries:
                path.unlink()
                removed += 1

    xlp_dir = COOKER_XLPS
    if xlp_dir.exists():
        for path in xlp_dir.glob("GraceCivilizationIconsV*.xlp"):
            if VERSIONED_CIVILIZATION_PACKAGE_PATTERN.fullmatch(path.stem):
                path.unlink()
                removed += 1

    blp_dir = RUNTIME_BLP_DIR
    if blp_dir.exists():
        for path in blp_dir.glob("GraceCivilizationIconsV*.blp"):
            if VERSIONED_CIVILIZATION_PACKAGE_PATTERN.fullmatch(path.stem):
                path.unlink()
                removed += 1

    if removed:
        print(f"Removed {removed} obsolete civilization emblem asset files.")
    return removed


def cleanup_obsolete_infected_blood_assets() -> int:
    """Remove stale V1/V2/Vn infected-blood files before generating current assets."""
    expected_entries = set(infected_blood_entry_names())
    removed = 0

    for directory, suffixes in (
        (GENERATED_PNG_DIR, {".png"}),
        (GENERATED_DDS_DIR, {".dds"}),
        (COOKER_TEXTURES, {".tex"}),
        (COOKER_IMAGES, {".dds"}),
    ):
        if not directory.exists():
            continue
        for path in directory.iterdir():
            if not path.is_file() or path.suffix.lower() not in suffixes:
                continue
            if _is_infected_blood_stem(path.stem) and path.stem not in expected_entries:
                path.unlink()
                removed += 1

    xlp_dir = COOKER_XLPS
    if xlp_dir.exists():
        for path in xlp_dir.glob("GraceResourceIconsV*.xlp"):
            if (
                VERSIONED_PACKAGE_PATTERN.fullmatch(path.stem)
                and path.stem != INFECTED_BLOOD_PACKAGE_NAME
            ):
                path.unlink()
                removed += 1

    blp_dir = RUNTIME_BLP_DIR
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
        write_bytes_atomic(source.read_bytes(), COOKER_IMAGES / dds_name)


def texture_xml(entry_name: str, dds_name: str, width: int, height: int) -> str:
    document = texture_instance_xml(entry_name, max(width, height), dds_name)
    document = document.replace(f"<m_Height>{max(width, height)}</m_Height>", f"<m_Height>{height}</m_Height>")
    document = document.replace(f"<m_Width>{max(width, height)}</m_Width>", f"<m_Width>{width}</m_Width>")
    return document


def fallback_texture_xml(entry_name: str, dds_name: str, width: int, height: int) -> str:
    document = texture_xml(entry_name, dds_name, width, height)
    document = document.replace('<m_ClassName text="UserInterface"/>', '<m_ClassName text="Leader_Fallback"/>')
    document = document.replace(
        '<Element text="UserInterface"/>',
        '<Element text="Leader_Fallback"/>\n\t\t<Element text="Leader"/>\n\t\t<Element text="Fallback"/>',
    )
    return document


def generate_loading_art(source_dir: Path, png_dir: Path, dds_dir: Path) -> None:
    with Image.open(source_dir / "GraceAshcroft_Background.png") as source:
        background = ImageOps.fit(source.convert("RGBA"), (2048, 1024), method=Image.Resampling.LANCZOS)
    with Image.open(source_dir / "GraceAshcroft_Foreground.png") as source:
        foreground = ImageOps.fit(source.convert("RGBA"), (1024, 2048), method=Image.Resampling.LANCZOS)

    loading_scene = background.copy()
    loading_scene.alpha_composite(foreground, (1024, 0))

    images = {
        "GraceAshcroft_Background": background,
        "GraceAshcroft_Foreground": foreground,
        "GraceAshcroft_LoadingScene": loading_scene,
        "GraceAshcroft_LoadingBlank": Image.new("RGBA", (8, 8), (0, 0, 0, 0)),
    }
    for stem, image in images.items():
        save_png_atomic(image, png_dir / f"{stem}.png")
        write_rgba_dds(image, dds_dir / f"{stem}.dds")


def write_loading_texture_inputs() -> None:
    for _, object_name, dds_name, width, height in LOADING_ENTRIES:
        (COOKER_TEXTURES / f"{object_name}.tex").write_text(
            texture_xml(object_name, dds_name, width, height),
            encoding="utf-8",
            newline="\n",
        )
    fallback_object = "GraceAshcroft_Foreground_Fallback"
    (COOKER_TEXTURES / f"{fallback_object}.tex").write_text(
        fallback_texture_xml(fallback_object, "GraceAshcroft_Foreground.dds", 1024, 2048),
        encoding="utf-8",
        newline="\n",
    )


def cleanup_cooker_dds() -> None:
    removed = 0
    for target in temporary_cooker_dds_paths():
        if target.exists():
            target.unlink()
            removed += 1
    print(f"Removed {removed} temporary cooker DDS files from {COOKER_IMAGES}.")


def xlp_entry(entry_id: str, object_name: str) -> str:
    return f'''\t\t<Element>
\t\t\t<m_EntryID text="{entry_id}"/>
\t\t\t<m_ObjectName text="{object_name}"/>
\t\t</Element>'''


def xlp_document(
    package_name: str,
    entries: list[tuple[str, str]],
    *,
    class_name: str = "UITexture",
) -> str:
    entry_block = "\n".join(xlp_entry(entry_id, object_name) for entry_id, object_name in entries)
    return f'''<?xml version="1.0" encoding="UTF-8" ?>
<AssetObjects..XLP>
\t<m_Version>
\t\t<major>4</major>
\t\t<minor>0</minor>
\t\t<build>410</build>
\t\t<revision>536</revision>
\t</m_Version>
\t<m_ClassName text="{class_name}"/>
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
    cooker_dds_target = COOKER_IMAGES / f"{entry_name}.dds"
    tex_target = COOKER_TEXTURES / f"{entry_name}.tex"

    png_target.parent.mkdir(parents=True, exist_ok=True)
    save_png_atomic(icon, png_target)
    write_rgba_dds(icon, dds_target)
    write_rgba_dds(icon, cooker_dds_target)
    tex_target.write_text(texture_instance_xml(entry_name, size), encoding="utf-8", newline="\n")


def build() -> None:
    cleanup_obsolete_civilization_assets()
    cleanup_obsolete_infected_blood_assets()
    GENERATED_PNG_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED_DDS_DIR.mkdir(parents=True, exist_ok=True)
    COOKER_IMAGES.mkdir(parents=True, exist_ok=True)
    COOKER_TEXTURES.mkdir(parents=True, exist_ok=True)
    COOKER_XLPS.mkdir(parents=True, exist_ok=True)
    generate_loading_art(SOURCE_DIR, LEADER_ART_PNG_DIR, LEADER_ART_DDS_DIR)
    copy_loading_cooker_inputs()
    write_loading_texture_inputs()

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

    civilization_source = SOURCE_DIR / CIVILIZATION_ICON_SOURCE
    if not civilization_source.exists():
        raise FileNotFoundError(f"Missing source icon: {civilization_source}")
    civilization_prepared = prepare_icon(civilization_source, "GraceCivilization_ElpisProtocol")
    civilization_entries: list[str] = []
    for size in CIVILIZATION_ICON_SIZES:
        entry_name = civilization_entry_name(size)
        civilization_entries.append(entry_name)
        write_texture_files(entry_name, size, resize_icon(civilization_prepared, size))

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
    ui_xlp_entries.extend((entry, entry) for entry in civilization_entries)
    GRACE_UI_XLP.write_text(
        xlp_document(GRACE_UI_PACKAGE_NAME, ui_xlp_entries), encoding="utf-8", newline="\n"
    )
    GRACE_RESOURCE_XLP.write_text(
        xlp_document(INFECTED_BLOOD_PACKAGE_NAME, [(entry, entry) for entry in resource_entries]),
        encoding="utf-8",
        newline="\n",
    )
    (COOKER_XLPS / "leaderfallbacks.xlp").write_text(
        xlp_document(
            CONFIG.package("leader_fallback"),
            [("FALLBACK_NEUTRAL_GRACE_ASHCROFT", "GraceAshcroft_Foreground_Fallback")],
            class_name="LeaderFallback",
        ),
        encoding="utf-8",
        newline="\n",
    )

    print(
        f"Generated {len(ui_entries)} UI icon entries and "
        f"{len(civilization_entries)} civilization emblem entries in {GRACE_UI_PACKAGE_NAME}, and "
        f"{len(resource_entries)} infected-blood entries in {INFECTED_BLOOD_PACKAGE_NAME}."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cleanup-cooker-dds",
        action="store_true",
        help="Remove temporary DDS inputs from assets/GraceAshcroft/cooker/Images.",
    )
    parser.add_argument(
        "--cleanup-obsolete",
        action="store_true",
        help="Only remove obsolete versioned assets and exit.",
    )
    args = parser.parse_args(argv)

    if args.cleanup_cooker_dds:
        cleanup_cooker_dds()
    elif args.cleanup_obsolete:
        cleanup_obsolete_civilization_assets()
        cleanup_obsolete_infected_blood_assets()
    else:
        build()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
