"""Tests for the Grace Ashcroft Asset Cooker plan."""

from __future__ import annotations

import unittest
from pathlib import Path

from tools.common.civ6_mod_config import load_mod_config
from tools.grace_ashcroft.cook_assets import build_cook_plan


REPO_ROOT = Path(__file__).resolve().parents[3]


class CookPlanTests(unittest.TestCase):
    def test_internal_python_calls_disable_bytecode(self) -> None:
        source = (REPO_ROOT / "tools/grace_ashcroft/cook_assets.py").read_text(encoding="utf-8")

        self.assertGreaterEqual(source.count('[sys.executable, "-B"'), 3)

    def test_manifest_drives_current_cook_package_plan(self) -> None:
        config = load_mod_config(
            REPO_ROOT / "assets" / "GraceAshcroft" / "mod-build.toml",
            repo_root=REPO_ROOT,
        )

        packages = build_cook_plan(config)

        self.assertEqual(
            [(package.name, package.xlp_name) for package in packages],
            [
                ("GraceUITexture", "GraceUITexture.xlp"),
                ("GraceResourceIconsV2", "GraceResourceIconsV2.xlp"),
                ("LeaderFallbacks", "leaderfallbacks.xlp"),
            ],
        )
        self.assertEqual(
            [package.runtime_blp for package in packages],
            [
                REPO_ROOT / "mods" / "GraceAshcroft" / "Platforms" / "Windows" / "BLPs" / "GraceUITexture.blp",
                REPO_ROOT / "mods" / "GraceAshcroft" / "Platforms" / "Windows" / "BLPs" / "GraceResourceIconsV2.blp",
                REPO_ROOT / "mods" / "GraceAshcroft" / "Platforms" / "Windows" / "BLPs" / "LeaderFallbacks.blp",
            ],
        )


if __name__ == "__main__":
    unittest.main()
