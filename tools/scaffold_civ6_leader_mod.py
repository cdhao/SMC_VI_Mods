#!/usr/bin/env python3
"""Create a clean Civilization VI civilization-plus-leader mod workspace."""

from __future__ import annotations

import argparse
import re
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = REPO_ROOT / "templates" / "civ6-leader-mod"
SLUG_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


def _render_text(source: Path, destination: Path, replacements: dict[str, str]) -> None:
    content = source.read_text(encoding="utf-8")
    for marker, value in replacements.items():
        content = content.replace(marker, value)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8", newline="\n")


def scaffold_mod(repo_root: Path, *, slug: str, display_name: str) -> None:
    """Create a new Mod without overwriting any of its four ownership roots."""

    if not SLUG_PATTERN.fullmatch(slug):
        raise ValueError("slug must use ASCII letters, digits, and underscores, starting with a letter")
    if not display_name.strip():
        raise ValueError("display_name must not be empty")
    if not TEMPLATE_ROOT.is_dir():
        raise FileNotFoundError(f"Missing scaffold template: {TEMPLATE_ROOT}")

    repo_root = repo_root.resolve()
    destinations = tuple(repo_root / root / slug for root in ("assets", "mods", "projects", "tools"))
    existing = [path for path in destinations if path.exists()]
    if existing:
        raise FileExistsError("Mod root already exists: " + ", ".join(str(path) for path in existing))

    replacements = {
        "__MOD_SLUG__": slug,
        "__MOD_NAME__": display_name.strip(),
        "__MOD_ID__": str(uuid.uuid4()),
    }
    for source in TEMPLATE_ROOT.rglob("*"):
        relative = source.relative_to(TEMPLATE_ROOT)
        rendered_relative = Path(*(part.replace("__MOD_SLUG__", slug) for part in relative.parts))
        destination = repo_root / rendered_relative
        if source.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
        else:
            _render_text(source, destination, replacements)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug", help="ASCII identifier used for folders and package names")
    parser.add_argument("display_name", help="Human-readable mod name")
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="repository root")
    args = parser.parse_args(argv)
    scaffold_mod(args.root, slug=args.slug, display_name=args.display_name)
    print(f"Created Civilization VI mod scaffold for {args.slug} under {args.root.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
