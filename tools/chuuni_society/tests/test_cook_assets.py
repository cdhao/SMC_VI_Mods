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

    def test_ui_only_dry_run_excludes_leader_fallback_package(self) -> None:
        result = subprocess.run(
            [
                str(Path(subprocess.sys.executable)),
                "-B",
                str(COOK_SCRIPT),
                "--package",
                "ui",
                "--dry-run",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ChuuniUITextureV1.xlp", result.stdout)
        self.assertNotIn("ChuuniLeaderFallbacks.blp", result.stdout)
        self.assertNotIn("leaderfallbacks.xlp", result.stdout)

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
            "ArtDefs/Districts.artdef",
            "Platforms/Windows/BLPs/ChuuniUITextureV1.blp",
            "Platforms/Windows/BLPs/ChuuniLeaderFallbacks.blp",
            "<UpdateArt",
        ):
            self.assertIn(contract, modinfo)

    def test_society_district_inherits_holy_site_art(self) -> None:
        districts = (MOD_ROOT / "ArtDefs/Districts.artdef").read_text(encoding="utf-8")
        art_project = (
            REPO_ROOT / "projects/ChuuniSociety/ChuuniSociety.Art.xml"
        ).read_text(encoding="utf-8")
        dependency = (MOD_ROOT / "ChuuniSociety.dep").read_text(encoding="utf-8")

        for contract in (
            "DISTRICT_CHUUNI_SOCIETY",
            "DISTRICT_HOLY_SITE",
            "HolySite",
            "HolySite_Pillaged",
            "HolySite_UnderConstruction",
            "Build_District_HolySite",
            "PLAY_AMBIENCE_DISTRICT_HOLYSITE",
            "STOP_AMBIENCE_DISTRICT_HOLYSITE",
        ):
            self.assertIn(contract, districts)
        for consumer in ("Audio", "StrategicView_Translate", "WorldView_Translate"):
            self.assertIn(consumer, art_project)
            self.assertIn(consumer, dependency)
        self.assertIn("Districts.artdef", art_project)
        self.assertIn("Districts.artdef", dependency)

    def test_cooker_cleans_temporary_dds_and_validates_output(self) -> None:
        source = COOK_SCRIPT.read_text(encoding="utf-8")

        self.assertIn("finally:", source)
        self.assertIn("cleanup_cooker_dds", source)
        self.assertIn("check_static.py", source)
        self.assertGreaterEqual(source.count('[sys.executable, "-B"'), 2)


if __name__ == "__main__":
    unittest.main()
