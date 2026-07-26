#!/usr/bin/env python3
"""Build Chuuni Society icon and leader-art inputs for the Civ6 Asset Cooker."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageOps


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.chuuni_society.prepare_logo import fit_square, prepare_logo  # noqa: E402
from tools.common.civ6_mod_config import load_mod_config  # noqa: E402
from tools.common.civ6_texture import (  # noqa: E402
    resize_icon,
    save_png_atomic,
    texture_instance_xml,
    write_bytes_atomic,
    write_rgba_dds,
)


CONFIG = load_mod_config(
    REPO_ROOT / "assets" / "ChuuniSociety" / "mod-build.toml",
    repo_root=REPO_ROOT,
)
ASSET_ROOT = CONFIG.asset_root
PROCESSED_DIR = ASSET_ROOT / "processed"
GENERATED_PNG_DIR = ASSET_ROOT / "generated" / "icons" / "png"
GENERATED_DDS_DIR = ASSET_ROOT / "generated" / "icons" / "dds"
LEADER_PNG_DIR = ASSET_ROOT / "leader-art" / "png"
LEADER_DDS_DIR = ASSET_ROOT / "leader-art" / "dds"
COOKER_IMAGES = ASSET_ROOT / "cooker" / "Images"
COOKER_TEXTURES = COOKER_IMAGES / "Textures"
COOKER_XLPS = ASSET_ROOT / "cooker" / "XLPs"

UI_PACKAGE = CONFIG.package("ui")
CIVILIZATION_PREFIX = f"ChuuniCivilization_V{CONFIG.asset_revision}"

STANDARD_ICON_SIZES = (22, 30, 32, 38, 50, 64, 80, 256)
LEADER_ICON_SIZES = (22, 30, 32, 38, 45, 48, 50, 55, 64, 80, 256)
CIVILIZATION_ICON_SIZES = (22, 30, 32, 36, 38, 44, 45, 48, 50, 64, 80, 128, 200, 256)
RESOURCE_ICON_SIZES = (22, 38, 50, 64, 256)
GOVERNOR_ICON_SIZES = (*STANDARD_ICON_SIZES, 512)

ICON_SPECS = {
    CIVILIZATION_PREFIX: ("processed/ChuuniSociety_Civilization_WhiteAlpha.png", CIVILIZATION_ICON_SIZES, "transparent"),
    "Chuuni_Icon_Rikka": ("六花领袖头像.png", LEADER_ICON_SIZES, "leader_circle"),
    "Chuuni_Icon_SocietyDistrict": ("极东魔术昼寝结社区域图标.png", STANDARD_ICON_SIZES, "transparent"),
    "Chuuni_Icon_MagicCircle": ("部室魔法阵建筑图标.png", STANDARD_ICON_SIZES, "leader_circle"),
    "Chuuni_Icon_ChuuniValue": ("中二值资源图标.png", RESOURCE_ICON_SIZES, "transparent"),
    "Chuuni_Icon_Chimera": ("奇美拉总督头像.png", GOVERNOR_ICON_SIZES, "square"),
    "Chuuni_Icon_InvisibleBoundary": ("不可视境界线改良设施图标.png", STANDARD_ICON_SIZES, "transparent"),
}

LOADING_ENTRIES = (
    ("IMG_LOADING_BACKGROUND_RIKKA_TAKANASHI", "Chuuni_Background_UI", "Chuuni_Background.dds", 2048, 1024),
    ("IMG_LOADING_FOREGROUND_RIKKA_TAKANASHI", "Chuuni_Foreground_UI", "Chuuni_Foreground.dds", 1024, 2048),
    ("IMG_LOADING_SCENE_RIKKA_TAKANASHI", "Chuuni_LoadingScene_UI", "Chuuni_LoadingScene.dds", 2048, 1024),
    ("IMG_LOADING_FOREGROUND_BLANK_RIKKA_TAKANASHI", "Chuuni_LoadingBlank_UI", "Chuuni_LoadingBlank.dds", 8, 8),
)


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
\t<m_Version><major>4</major><minor>0</minor><build>410</build><revision>536</revision></m_Version>
\t<m_ClassName text="{class_name}"/>
\t<m_PackageName text="{package_name}"/>
\t<m_Entries>
{entry_block}
\t</m_Entries>
\t<m_AllowedPlatforms><Element>WINDOWS</Element><Element>LINUX</Element><Element>MACOS</Element><Element>IOS</Element></m_AllowedPlatforms>
</AssetObjects..XLP>
'''


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


def apply_circular_alpha(image: Image.Image) -> Image.Image:
    """Mask a square icon to a smooth circle while preserving source alpha."""

    size = image.width
    scale = 4
    mask = Image.new("L", (size * scale, size * scale), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size * scale - 1, size * scale - 1), fill=255)
    mask = mask.resize((size, size), Image.Resampling.LANCZOS)
    result = image.copy()
    result.putalpha(ImageChops.multiply(result.getchannel("A"), mask))
    return result


def prepare_icon(source: Image.Image, *, mode: str) -> Image.Image:
    image = source.convert("RGBA")
    if mode in {"square", "leader_circle"}:
        prepared = ImageOps.fit(image, (max(image.size), max(image.size)), method=Image.Resampling.LANCZOS)
        if mode == "leader_circle":
            return apply_circular_alpha(prepared)
        return prepared
    return fit_square(image, size=max(image.size), padding_ratio=0.10, alpha_cutoff=4)


def write_texture(entry_name: str, image: Image.Image) -> None:
    png_target = GENERATED_PNG_DIR / f"{entry_name}.png"
    dds_target = GENERATED_DDS_DIR / f"{entry_name}.dds"
    cooker_dds_target = COOKER_IMAGES / f"{entry_name}.dds"
    tex_target = COOKER_TEXTURES / f"{entry_name}.tex"
    for directory in (png_target.parent, dds_target.parent, cooker_dds_target.parent, tex_target.parent):
        directory.mkdir(parents=True, exist_ok=True)
    save_png_atomic(image, png_target)
    write_rgba_dds(image, dds_target)
    write_rgba_dds(image, cooker_dds_target)
    tex_target.write_text(texture_xml(entry_name, f"{entry_name}.dds", image.width, image.height), encoding="utf-8", newline="\n")


def build_loading_art() -> list[tuple[str, str]]:
    COOKER_TEXTURES.mkdir(parents=True, exist_ok=True)
    with Image.open(ASSET_ROOT / "载入背景.png") as source:
        background = ImageOps.fit(source.convert("RGBA"), (2048, 1024), method=Image.Resampling.LANCZOS)
    with Image.open(ASSET_ROOT / "六花载入前景.png") as source:
        foreground = ImageOps.fit(source.convert("RGBA"), (1024, 2048), method=Image.Resampling.LANCZOS)

    loading_scene = background.copy()
    scene_foreground = foreground.resize((480, 960), Image.Resampling.LANCZOS)
    loading_scene.alpha_composite(scene_foreground, (1280, 32))
    blank = Image.new("RGBA", (8, 8), (0, 0, 0, 0))

    images = {
        "Chuuni_Background": background,
        "Chuuni_Foreground": foreground,
        "Chuuni_LoadingScene": loading_scene,
        "Chuuni_LoadingBlank": blank,
    }
    for stem, image in images.items():
        png_target = LEADER_PNG_DIR / f"{stem}.png"
        dds_target = LEADER_DDS_DIR / f"{stem}.dds"
        png_target.parent.mkdir(parents=True, exist_ok=True)
        dds_target.parent.mkdir(parents=True, exist_ok=True)
        save_png_atomic(image, png_target)
        write_rgba_dds(image, dds_target)

    entries: list[tuple[str, str]] = []
    for entry_id, object_name, dds_name, width, height in LOADING_ENTRIES:
        source_dds = LEADER_DDS_DIR / dds_name
        cooker_dds = COOKER_IMAGES / dds_name
        write_bytes_atomic(source_dds.read_bytes(), cooker_dds)
        (COOKER_TEXTURES / f"{object_name}.tex").write_text(
            texture_xml(object_name, dds_name, width, height), encoding="utf-8", newline="\n"
        )
        entries.append((entry_id, object_name))

    fallback_object = "Chuuni_Foreground_Fallback"
    (COOKER_TEXTURES / f"{fallback_object}.tex").write_text(
        fallback_texture_xml(fallback_object, "Chuuni_Foreground.dds", 1024, 2048),
        encoding="utf-8",
        newline="\n",
    )
    return entries


def build() -> None:
    prepare_logo(
        ASSET_ROOT / "文明 Logo.png",
        PROCESSED_DIR / "ChuuniSociety_Civilization_WhiteAlpha.png",
        size=512,
        padding_ratio=0.08,
    )

    ui_entries = build_loading_art()
    generated_count = 0
    for entry_base, (source_name, sizes, mode) in ICON_SPECS.items():
        with Image.open(ASSET_ROOT / source_name) as source:
            prepared = prepare_icon(source, mode=mode)
        for size in sizes:
            entry_name = f"{entry_base}_{size}"
            write_texture(entry_name, resize_icon(prepared, size, content_ratio=1.0))
            ui_entries.append((entry_name, entry_name))
            generated_count += 1

    COOKER_XLPS.mkdir(parents=True, exist_ok=True)
    (COOKER_XLPS / f"{UI_PACKAGE}.xlp").write_text(
        xlp_document(UI_PACKAGE, ui_entries), encoding="utf-8", newline="\n"
    )
    (COOKER_XLPS / "leaderfallbacks.xlp").write_text(
        xlp_document(
            CONFIG.package("leader_fallback"),
            [("FALLBACK_NEUTRAL_RIKKA_TAKANASHI", "Chuuni_Foreground_Fallback")],
            class_name="LeaderFallback",
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(f"Generated {generated_count} Chuuni icon textures and four loading textures.")


def main() -> int:
    build()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
