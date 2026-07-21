"""Black-box reconstruction contracts for Grace Ashcroft asset inputs."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


REPO_ROOT = Path(__file__).resolve().parents[3]


class BuildAssetsTests(unittest.TestCase):
    def test_builder_reconstructs_every_ignored_asset_from_indexed_sources(self) -> None:
        scratch_root = REPO_ROOT / ".tmp"
        scratch_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch_root) as temp_dir:
            snapshot = Path(temp_dir) / "snapshot"
            snapshot.mkdir()
            checkout = subprocess.run(
                ["git", "checkout-index", "-a", "-f", f"--prefix={snapshot}{os.sep}"],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(checkout.returncode, 0, checkout.stdout + checkout.stderr)

            build = subprocess.run(
                [sys.executable, "-B", "tools/grace_ashcroft/build_assets.py"],
                cwd=snapshot,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)

            asset_root = snapshot / "assets/GraceAshcroft"
            expected = (
                "leader-art/png/GraceAshcroft_Background.png",
                "leader-art/png/GraceAshcroft_Foreground.png",
                "leader-art/png/GraceAshcroft_LoadingScene.png",
                "leader-art/png/GraceAshcroft_LoadingBlank.png",
                "leader-art/dds/GraceAshcroft_Background.dds",
                "leader-art/dds/GraceAshcroft_Foreground.dds",
                "leader-art/dds/GraceAshcroft_LoadingScene.dds",
                "leader-art/dds/GraceAshcroft_LoadingBlank.dds",
                "cooker/Images/Textures/GraceAshcroft_Background_UI.tex",
                "cooker/Images/Textures/GraceAshcroft_Foreground_UI.tex",
                "cooker/Images/Textures/GraceAshcroft_LoadingScene_UI.tex",
                "cooker/Images/Textures/GraceAshcroft_LoadingBlank_UI.tex",
                "cooker/Images/Textures/GraceAshcroft_Foreground_Fallback.tex",
                "cooker/XLPs/GraceUITexture.xlp",
                "cooker/XLPs/GraceResourceIconsV2.xlp",
                "cooker/XLPs/leaderfallbacks.xlp",
            )
            self.assertTrue(all((asset_root / relative).is_file() for relative in expected), expected)

            expected_sizes = {
                "GraceAshcroft_Background.png": (2048, 1024),
                "GraceAshcroft_Foreground.png": (1024, 2048),
                "GraceAshcroft_LoadingScene.png": (2048, 1024),
                "GraceAshcroft_LoadingBlank.png": (8, 8),
            }
            for name, size in expected_sizes.items():
                with Image.open(asset_root / "leader-art/png" / name) as image:
                    self.assertEqual(image.size, size, name)

            with Image.open(asset_root / "leader-art/png/GraceAshcroft_Background.png") as image:
                expected_loading_scene = image.convert("RGBA")
            with Image.open(asset_root / "leader-art/png/GraceAshcroft_Foreground.png") as image:
                loading_foreground = image.convert("RGBA")
            expected_loading_scene.alpha_composite(loading_foreground, (1024, 0))
            with Image.open(asset_root / "leader-art/png/GraceAshcroft_LoadingScene.png") as image:
                actual_loading_scene = image.convert("RGBA")
            self.assertEqual(
                actual_loading_scene.tobytes(),
                expected_loading_scene.tobytes(),
                "LoadingScene must composite the full-size foreground at the right edge of the background",
            )


if __name__ == "__main__":
    unittest.main()
