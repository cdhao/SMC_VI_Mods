#!/usr/bin/env python3
"""CLI compatibility wrapper for the shared Civ VI RGBA DDS writer."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.common.civ6_texture import write_rgba_dds  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Write uncompressed legacy RGBA DDS files from PNG inputs."
    )
    parser.add_argument("sources", metavar="source.png", nargs="+")
    parser.add_argument("--out-dir", type=Path, default=None)
    args = parser.parse_args(argv)

    for arg in args.sources:
        source = Path(arg)
        if source.suffix.lower() != ".png":
            print(f"Skipping non-PNG input: {source}", file=sys.stderr)
            continue
        target = (
            args.out_dir / source.with_suffix(".dds").name
            if args.out_dir
            else source.with_suffix(".dds")
        )
        write_rgba_dds(source, target)
        print(f"Wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
