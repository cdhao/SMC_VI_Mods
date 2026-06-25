#!/usr/bin/env python3
"""Write uncompressed legacy DDS files with RGBA channel masks.

Pillow's DDS writer emits BGRA masks for these images, while the Grace
Ashcroft texture instances declare PF_R8G8B8A8_UNORM. This helper keeps the
source PNG colors unchanged and writes a DDS header whose masks match RGBA.
"""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

from PIL import Image


DDSD_CAPS = 0x00000001
DDSD_HEIGHT = 0x00000002
DDSD_WIDTH = 0x00000004
DDSD_PITCH = 0x00000008
DDSD_PIXELFORMAT = 0x00001000

DDPF_ALPHAPIXELS = 0x00000001
DDPF_RGB = 0x00000040

DDSCAPS_TEXTURE = 0x00001000


def write_rgba_dds(source: Path, target: Path) -> None:
    image = Image.open(source).convert("RGBA")
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


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Write uncompressed legacy RGBA DDS files from PNG inputs."
    )
    parser.add_argument("sources", metavar="source.png", nargs="+")
    parser.add_argument("--out-dir", type=Path, default=None)
    args = parser.parse_args(argv[1:])

    for arg in args.sources:
        source = Path(arg)
        if source.suffix.lower() != ".png":
            print(f"Skipping non-PNG input: {source}", file=sys.stderr)
            continue
        target = (args.out_dir / source.with_suffix(".dds").name) if args.out_dir else source.with_suffix(".dds")
        write_rgba_dds(source, target)
        print(f"Wrote {target}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
