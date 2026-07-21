#!/usr/bin/env python3
"""Extract a white Civilization VI emblem from a black-background source."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageOps


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = REPO_ROOT / "assets" / "ChuuniSociety" / "文明 Logo.png"
DEFAULT_OUTPUT = (
    REPO_ROOT
    / "assets"
    / "ChuuniSociety"
    / "processed"
    / "ChuuniSociety_Civilization_WhiteAlpha.png"
)


def extract_white_emblem(
    source: Image.Image,
    black_point: int = 10,
    white_point: int = 245,
    gamma: float = 1.05,
) -> Image.Image:
    """Turn source luminance into alpha while making every visible pixel white."""
    if not 0 <= black_point < white_point <= 255:
        raise ValueError("black_point must be below white_point within 0..255")
    if gamma <= 0:
        raise ValueError("gamma must be positive")

    luminance = ImageOps.grayscale(source.convert("RGB"))
    span = white_point - black_point
    alpha_lut = []
    for value in range(256):
        normalized = min(1.0, max(0.0, (value - black_point) / span))
        alpha_lut.append(round(255 * normalized**gamma))
    alpha = luminance.point(alpha_lut)

    result = Image.new("RGBA", source.size, (255, 255, 255, 0))
    result.putalpha(alpha)
    return result


def fit_square(
    image: Image.Image,
    size: int = 512,
    padding_ratio: float = 0.08,
    alpha_cutoff: int = 4,
) -> Image.Image:
    """Crop insignificant transparent pixels, add safe padding, and resize."""
    if size <= 0:
        raise ValueError("size must be positive")
    if not 0 <= padding_ratio < 0.5:
        raise ValueError("padding_ratio must be between 0 and 0.5")

    alpha = image.getchannel("A")
    significant = alpha.point(lambda value: 255 if value > alpha_cutoff else 0)
    bbox = significant.getbbox()
    if bbox is None:
        raise ValueError("source contains no visible emblem after extraction")

    cropped = image.crop(bbox)
    content_side = max(cropped.size)
    canvas_side = max(1, round(content_side / (1 - 2 * padding_ratio)))
    canvas = Image.new("RGBA", (canvas_side, canvas_side), (255, 255, 255, 0))
    offset = ((canvas_side - cropped.width) // 2, (canvas_side - cropped.height) // 2)
    canvas.alpha_composite(cropped, offset)
    return canvas.resize((size, size), Image.Resampling.LANCZOS)


def prepare_logo(
    source_path: Path,
    output_path: Path,
    *,
    size: int = 512,
    black_point: int = 10,
    white_point: int = 245,
    gamma: float = 1.05,
    padding_ratio: float = 0.08,
) -> Path:
    with Image.open(source_path) as source:
        extracted = extract_white_emblem(source, black_point, white_point, gamma)
    prepared = fit_square(extracted, size=size, padding_ratio=padding_ratio)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    prepared.save(output_path)
    return output_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("output", nargs="?", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--size", type=int, default=512)
    parser.add_argument("--black-point", type=int, default=10)
    parser.add_argument("--white-point", type=int, default=245)
    parser.add_argument("--gamma", type=float, default=1.05)
    parser.add_argument("--padding", type=float, default=0.08)
    args = parser.parse_args(argv)

    output = prepare_logo(
        args.source,
        args.output,
        size=args.size,
        black_point=args.black_point,
        white_point=args.white_point,
        gamma=args.gamma,
        padding_ratio=args.padding,
    )
    print(f"Prepared transparent white emblem: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
