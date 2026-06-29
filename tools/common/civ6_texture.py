"""Small, reusable Civ VI texture helpers.

This module intentionally contains no mod-specific names or paths. Individual
mod build scripts decide which assets exist and how packages are organized.
"""

from __future__ import annotations

import struct
from pathlib import Path
from typing import Union

from PIL import Image

ImageSource = Union[Image.Image, Path, str]

DDSD_CAPS = 0x00000001
DDSD_HEIGHT = 0x00000002
DDSD_WIDTH = 0x00000004
DDSD_PITCH = 0x00000008
DDSD_PIXELFORMAT = 0x00001000
DDPF_ALPHAPIXELS = 0x00000001
DDPF_RGB = 0x00000040
DDSCAPS_TEXTURE = 0x00001000


def _as_rgba_image(source: ImageSource) -> Image.Image:
    if isinstance(source, Image.Image):
        return source.convert("RGBA")
    return Image.open(source).convert("RGBA")


def write_rgba_dds(source: ImageSource, target: Path) -> None:
    """Write an uncompressed legacy DDS using RGBA channel masks."""
    image = _as_rgba_image(source)
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
    bbox = image.convert("RGBA").getchannel("A").getbbox()
    return bbox or (0, 0, image.width, image.height)


def crop_alpha_square(image: Image.Image, padding_ratio: float = 0.18) -> Image.Image:
    """Crop around non-transparent pixels while keeping a square canvas."""
    image = image.convert("RGBA")
    left, top, right, bottom = alpha_bbox(image)
    width = right - left
    height = bottom - top
    side = int(max(width, height) * (1 + padding_ratio))
    side = max(1, min(side, image.width, image.height))
    center_x = (left + right) // 2
    center_y = (top + bottom) // 2
    crop_left = max(0, min(center_x - side // 2, image.width - side))
    crop_top = max(0, min(center_y - side // 2, image.height - side))
    return image.crop((crop_left, crop_top, crop_left + side, crop_top + side))


def resize_icon(image: Image.Image, size: int, content_ratio: float = 0.9) -> Image.Image:
    """Fit an icon into a transparent square canvas."""
    if size <= 0:
        raise ValueError("size must be positive")
    if not 0 < content_ratio <= 1:
        raise ValueError("content_ratio must be in (0, 1]")

    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    target = max(1, int(size * content_ratio))
    resized = image.convert("RGBA").copy()
    resized.thumbnail((target, target), Image.Resampling.LANCZOS)
    x = (size - resized.width) // 2
    y = (size - resized.height) // 2
    canvas.alpha_composite(resized, (x, y))
    return canvas


def texture_instance_xml(entry_name: str, size: int, dds_name: str | None = None) -> str:
    """Build a standard UI TextureInstance document for a square DDS."""
    dds_name = dds_name or f"{entry_name}.dds"
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
