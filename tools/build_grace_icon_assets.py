#!/usr/bin/env python3
"""Build Grace Ashcroft icon assets for Civ VI.

Inputs live outside the mod in assets/GraceAshcroft/source/icons. The script
generates intermediate PNG/DDS files under assets/GraceAshcroft/generated/icons,
copies cooker DDS inputs into mods/GraceAshcroft/Images, writes TextureInstance
files, and refreshes GraceUITexture.xlp entries.
"""

from __future__ import annotations

import argparse
import shutil
import struct
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = ROOT / "assets" / "GraceAshcroft"
SOURCE_DIR = ASSET_ROOT / "source" / "icons"
LEADER_ART_DDS_DIR = ASSET_ROOT / "leader-art" / "dds"
GENERATED_PNG_DIR = ASSET_ROOT / "generated" / "icons" / "png"
GENERATED_DDS_DIR = ASSET_ROOT / "generated" / "icons" / "dds"
MOD_ROOT = ROOT / "mods" / "GraceAshcroft"
MOD_IMAGES = MOD_ROOT / "Images"
MOD_TEXTURES = MOD_IMAGES / "Textures"
GRACE_UI_XLP = MOD_ROOT / "XLPs" / "GraceUITexture.xlp"

ICON_SIZES = (22, 30, 32, 38, 50, 64, 80, 256)
CIVILIZATION_ICON_SIZES = (22, 30, 32, 36, 38, 44, 45, 48, 50, 64, 80, 128, 200, 256)

ICONS = {
    "GraceAshcroft_Icon_Civilization": "GraceAshcroft_Civilization.png",
    "GraceAshcroft_Icon_Hemolytic": "GraceAshcroft_Hemolytic.png",
    "GraceAshcroft_Icon_Stabilizer": "GraceAshcroft_Stabilizer.png",
    "GraceAshcroft_Icon_Steroid": "GraceAshcroft_Steroid.png",
    "GraceAshcroft_Icon_InfectedBlood": "GraceAshcroft_InfectedBlood.png",
    "GraceAshcroft_Icon_Leader": "GraceAshcroft_LeaderIcon.png",
}

ICON_SIZE_OVERRIDES = {
    "GraceAshcroft_Icon_Civilization": CIVILIZATION_ICON_SIZES,
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

DDSD_CAPS = 0x00000001
DDSD_HEIGHT = 0x00000002
DDSD_WIDTH = 0x00000004
DDSD_PITCH = 0x00000008
DDSD_PIXELFORMAT = 0x00001000
DDPF_ALPHAPIXELS = 0x00000001
DDPF_RGB = 0x00000040
DDSCAPS_TEXTURE = 0x00001000


def write_rgba_dds(image: Image.Image, target: Path) -> None:
    image = image.convert("RGBA")
    width, height = image.size
    pitch = width * 4

    header = bytearray()
    header += b"DDS "
    header += struct.pack(
        "<7I",
        124,
        DDSD_CAPS | DDSD_HEIGHT | DDSD_WIDTH | DDSD_PITCH | DDSD_PIXELFORMAT,
        height,
        width,
        pitch,
        0,
        0,
    )
    header += struct.pack("<11I", *([0] * 11))
    header += struct.pack(
        "<8I",
        32,
        DDPF_RGB | DDPF_ALPHAPIXELS,
        0,
        32,
        0x000000FF,
        0x0000FF00,
        0x00FF0000,
        0xFF000000,
    )
    header += struct.pack("<5I", DDSCAPS_TEXTURE, 0, 0, 0, 0)

    if len(header) != 128:
        raise RuntimeError(f"Unexpected DDS header size: {len(header)}")

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(bytes(header) + image.tobytes("raw", "RGBA"))


def alpha_bbox(image: Image.Image) -> tuple[int, int, int, int]:
    alpha = image.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        return (0, 0, image.width, image.height)
    return bbox


def expand_square(
    bbox: tuple[int, int, int, int],
    image_size: tuple[int, int],
    padding_ratio: float,
) -> tuple[int, int, int, int]:
    left, top, right, bottom = bbox
    width = right - left
    height = bottom - top
    size = int(max(width, height) * (1 + padding_ratio))
    size = min(size, image_size[0], image_size[1])
    cx = (left + right) // 2
    cy = (top + bottom) // 2
    left = max(0, min(cx - size // 2, image_size[0] - size))
    top = max(0, min(cy - size // 2, image_size[1] - size))
    return (left, top, left + size, top + size)


def prepare_icon(source: Path, entry_base: str) -> Image.Image:
    image = Image.open(source).convert("RGBA")
    if entry_base == "GraceAshcroft_Icon_Leader":
        # Focus the leader icon on Grace's face and shoulders rather than the
        # full bust; the UI supplies the circular frame.
        bbox = alpha_bbox(image)
        left, top, right, bottom = bbox
        width = right - left
        center_x = (left + right) // 2
        side = min(image.width, image.height, max(width + 96, 430))
        crop_left = max(0, min(center_x - side // 2, image.width - side))
        return image.crop((crop_left, 0, crop_left + side, side))

    bbox = expand_square(alpha_bbox(image), image.size, 0.18)
    return image.crop(bbox)


def resize_icon(image: Image.Image, size: int) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    target = int(size * 0.9)
    resized = image.copy()
    resized.thumbnail((target, target), Image.Resampling.LANCZOS)
    x = (size - resized.width) // 2
    y = (size - resized.height) // 2
    canvas.alpha_composite(resized, (x, y))
    return canvas


def icon_sizes_for(entry_base: str) -> tuple[int, ...]:
    return ICON_SIZE_OVERRIDES.get(entry_base, ICON_SIZES)


def icon_entry_names() -> list[str]:
    return [
        f"{entry_base}_{size}"
        for entry_base in ICONS
        for size in icon_sizes_for(entry_base)
    ]


def temporary_mod_dds_paths() -> list[Path]:
    paths = [MOD_IMAGES / dds_name for dds_name in LOADING_DDS_INPUTS]
    paths.extend(MOD_IMAGES / f"{entry_name}.dds" for entry_name in icon_entry_names())
    return paths


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


def texture_instance(entry_name: str, size: int) -> str:
    dds_name = f"{entry_name}.dds"
    return f'''<?xml version="1.0" encoding="UTF-8" ?>
<AssetObjects..TextureInstance>
\t<m_ExportSettings>
\t\t<ePixelformat>PF_R8G8B8A8_UNORM</ePixelformat>
\t\t<eFilterType>FT_LANCZOS6</eFilterType>
\t\t<bUseMips>false</bUseMips>
\t\t<iNumManualMips>0</iNumManualMips>
\t\t<bCompleteMipChain>false</bCompleteMipChain>
\t\t<fValueClampMin>0.000000</fValueClampMin>
\t\t<fValueClampMax>1.000000</fValueClampMax>
\t\t<fSupportScale>1.000000</fSupportScale>
\t\t<fGammaIn>2.200000</fGammaIn>
\t\t<fGammaOut>2.200000</fGammaOut>
\t\t<iSlabWidth>0</iSlabWidth>
\t\t<iSlabHeight>0</iSlabHeight>
\t\t<iColorKeyX>0</iColorKeyX>
\t\t<iColorKeyY>0</iColorKeyY>
\t\t<iColorKeyZ>0</iColorKeyZ>
\t\t<eExportMode>TEXTURE_2D</eExportMode>
\t\t<bSampleFromTopLayer>false</bSampleFromTopLayer>
\t</m_ExportSettings>
\t<m_CookParams>
\t\t<m_Values/>
\t</m_CookParams>
\t<m_Version>
\t\t<major>4</major>
\t\t<minor>0</minor>
\t\t<build>410</build>
\t\t<revision>536</revision>
\t</m_Version>
\t<m_Height>{size}</m_Height>
\t<m_Width>{size}</m_Width>
\t<m_Depth>1</m_Depth>
\t<m_NumMipMaps>0</m_NumMipMaps>
\t<m_SourceFilePath text="Images/{dds_name}"/>
\t<m_SourceObjectName text=""/>
\t<m_ImportedTime>0</m_ImportedTime>
\t<m_ExportedTime>0</m_ExportedTime>
\t<m_ClassName text="UserInterface"/>
\t<m_DataFiles>
\t\t<Element>
\t\t\t<m_ID text="DDS"/>
\t\t\t<m_RelativePath text="../{dds_name}"/>
\t\t</Element>
\t</m_DataFiles>
\t<m_Name text="{entry_name}"/>
\t<m_Description text=""/>
\t<m_Tags>
\t\t<Element text="UserInterface"/>
\t</m_Tags>
</AssetObjects..TextureInstance>
'''


def xlp_entry(entry_id: str, object_name: str) -> str:
    return f'''\t\t<Element>
\t\t\t<m_EntryID text="{entry_id}"/>
\t\t\t<m_ObjectName text="{object_name}"/>
\t\t</Element>'''


def write_grace_ui_xlp(icon_entries: list[str]) -> None:
    entries = [xlp_entry(entry_id, object_name) for entry_id, object_name in BASE_XLP_ENTRIES]
    entries.extend(xlp_entry(entry, entry) for entry in icon_entries)
    entry_block = "\n".join(entries)
    content = f'''<?xml version="1.0" encoding="UTF-8" ?>
<AssetObjects..XLP>
\t<m_Version>
\t\t<major>4</major>
\t\t<minor>0</minor>
\t\t<build>410</build>
\t\t<revision>536</revision>
\t</m_Version>
\t<m_ClassName text="UITexture"/>
\t<m_PackageName text="GraceUITexture"/>
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
    GRACE_UI_XLP.write_text(content, encoding="utf-8", newline="\n")


def build() -> None:
    GENERATED_PNG_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED_DDS_DIR.mkdir(parents=True, exist_ok=True)
    MOD_IMAGES.mkdir(parents=True, exist_ok=True)
    MOD_TEXTURES.mkdir(parents=True, exist_ok=True)
    copy_loading_cooker_inputs()

    icon_entries: list[str] = []
    for entry_base, source_name in ICONS.items():
        source = SOURCE_DIR / source_name
        if not source.exists():
            raise FileNotFoundError(f"Missing source icon: {source}")
        prepared = prepare_icon(source, entry_base)
        for size in icon_sizes_for(entry_base):
            entry_name = f"{entry_base}_{size}"
            icon_entries.append(entry_name)
            icon = resize_icon(prepared, size)
            png_target = GENERATED_PNG_DIR / f"{entry_name}.png"
            dds_target = GENERATED_DDS_DIR / f"{entry_name}.dds"
            cooker_dds_target = MOD_IMAGES / f"{entry_name}.dds"
            png_target.parent.mkdir(parents=True, exist_ok=True)
            icon.save(png_target)
            write_rgba_dds(icon, dds_target)
            write_rgba_dds(icon, cooker_dds_target)
            (MOD_TEXTURES / f"{entry_name}.tex").write_text(
                texture_instance(entry_name, size),
                encoding="utf-8",
                newline="\n",
            )

    write_grace_ui_xlp(icon_entries)
    print(f"Generated {len(icon_entries)} icon texture entries.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build Grace Ashcroft Civ VI icon assets.")
    parser.add_argument(
        "--cleanup-mod-dds",
        action="store_true",
        help="Remove temporary DDS cooker inputs from mods/GraceAshcroft/Images after cooking.",
    )
    args = parser.parse_args()

    if args.cleanup_mod_dds:
        cleanup_mod_dds()
    else:
        build()
