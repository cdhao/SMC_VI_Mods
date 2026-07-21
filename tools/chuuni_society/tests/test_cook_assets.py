"""Contracts for Chuuni Society runtime asset integration."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
COOK_SCRIPT = REPO_ROOT / "tools" / "chuuni_society" / "cook_assets.py"
MOD_ROOT = REPO_ROOT / "mods" / "ChuuniSociety"


class CookAssetsTests(unittest.TestCase):
    def test_dry_run_uses_isolated_package_names(self) -> None:
        result = subprocess.run(
            [str(Path(subprocess.sys.executable)), "-B", str(COOK_SCRIPT), "--dry-run"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ChuuniUITextureV1.xlp", result.stdout)
        self.assertIn("ChuuniLeaderFallbacks.blp", result.stdout)
        self.assertNotIn("Grace", result.stdout)

    def test_runtime_registrations_use_custom_loading_and_icons(self) -> None:
        icons = (MOD_ROOT / "Icons/ChuuniIcons.sql").read_text(encoding="utf-8")
        config = (MOD_ROOT / "Data/Config.sql").read_text(encoding="utf-8")
        core = (MOD_ROOT / "Data/Core.sql").read_text(encoding="utf-8")
        modinfo = (MOD_ROOT / "ChuuniSociety.modinfo").read_text(encoding="utf-8")

        for contract in (
            "ICON_ATLAS_CHUUNI_CIVILIZATION_V1",
            "ICON_ATLAS_CHUUNI_LEADER",
            "ICON_ATLAS_CHUUNI_GAMEPLAY",
            "ChuuniCivilization_V1_22",
            "Chuuni_Icon_Rikka_22",
            "Chuuni_Icon_MagicCircle_22",
        ):
            self.assertIn(contract, icons)
        self.assertIn("IMG_LOADING_FOREGROUND_RIKKA_TAKANASHI", config)
        self.assertIn("IMG_LOADING_BACKGROUND_RIKKA_TAKANASHI", config)
        self.assertIn("IMG_LOADING_SCENE_RIKKA_TAKANASHI", core)
        self.assertIn("IMG_LOADING_FOREGROUND_BLANK_RIKKA_TAKANASHI", core)
        for contract in (
            "ChuuniSociety.dep",
            "ArtDefs/FallbackLeaders.artdef",
            "Platforms/Windows/BLPs/ChuuniUITextureV1.blp",
            "Platforms/Windows/BLPs/ChuuniLeaderFallbacks.blp",
            "<UpdateArt",
        ):
            self.assertIn(contract, modinfo)

    def test_cooker_cleans_temporary_dds_and_validates_output(self) -> None:
        source = COOK_SCRIPT.read_text(encoding="utf-8")

        self.assertIn("finally:", source)
        self.assertIn("cleanup_cooker_dds", source)
        self.assertIn("check_static.py", source)
        self.assertGreaterEqual(source.count('[sys.executable, "-B"'), 2)


if __name__ == "__main__":
    unittest.main()
