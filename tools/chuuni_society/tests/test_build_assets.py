"""Black-box contracts for the Chuuni Society asset builder."""

from __future__ import annotations

import hashlib
import subprocess
import unittest
from pathlib import Path

from PIL import Image


REPO_ROOT = Path(__file__).resolve().parents[3]
ASSET_ROOT = REPO_ROOT / "assets" / "ChuuniSociety"
BUILD_SCRIPT = REPO_ROOT / "tools" / "chuuni_society" / "build_assets.py"
SOURCE_NAMES = (
    "文明 Logo.png",
    "六花领袖头像.png",
    "六花载入前景.png",
    "载入背景.png",
    "极东魔术昼寝结社区域图标.png",
    "部室魔法阵建筑图标.png",
    "中二值资源图标.png",
    "奇美拉总督头像.png",
    "不可视境界线改良设施图标.png",
    "魔法阵传送按钮图标.png",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class BuildAssetsTests(unittest.TestCase):
    def run_builder(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(Path(subprocess.sys.executable)), "-B", str(BUILD_SCRIPT)],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_builder_preserves_sources_and_generates_core_outputs(self) -> None:
        before = {name: digest(ASSET_ROOT / name) for name in SOURCE_NAMES}

        result = self.run_builder()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            before,
            {name: digest(ASSET_ROOT / name) for name in SOURCE_NAMES},
        )
        expected = (
            ASSET_ROOT / "generated/icons/png/ChuuniCivilization_V1_22.png",
            ASSET_ROOT / "generated/icons/dds/ChuuniCivilization_V1_256.dds",
            ASSET_ROOT / "leader-art/png/Chuuni_LoadingScene.png",
            ASSET_ROOT / "leader-art/dds/Chuuni_LoadingScene.dds",
            ASSET_ROOT / "cooker/XLPs/ChuuniUITextureV1.xlp",
            ASSET_ROOT / "cooker/XLPs/leaderfallbacks.xlp",
        )
        self.assertTrue(all(path.is_file() for path in expected), expected)

    def test_transparent_gameplay_icons_have_safe_border(self) -> None:
        result = self.run_builder()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        for stem in (
            "Chuuni_Icon_SocietyDistrict",
            "Chuuni_Icon_ChuuniValue",
            "Chuuni_Icon_InvisibleBoundary",
        ):
            with Image.open(
                ASSET_ROOT / "generated/icons/png" / f"{stem}_256.png"
            ) as image:
                alpha = image.convert("RGBA").getchannel("A")
                left, top, right, bottom = alpha.getbbox()
                self.assertGreaterEqual(left, 12, stem)
                self.assertGreaterEqual(top, 12, stem)
                self.assertLessEqual(right, 244, stem)
                self.assertLessEqual(bottom, 244, stem)

    def test_loading_art_has_exact_dimensions(self) -> None:
        result = self.run_builder()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        expected_sizes = {
            "Chuuni_Background.png": (2048, 1024),
            "Chuuni_Foreground.png": (1024, 2048),
            "Chuuni_LoadingScene.png": (2048, 1024),
            "Chuuni_LoadingBlank.png": (8, 8),
        }
        for name, size in expected_sizes.items():
            with Image.open(ASSET_ROOT / "leader-art/png" / name) as image:
                self.assertEqual(image.size, size, name)
                self.assertEqual(image.mode, "RGBA", name)

    def test_loading_scene_uses_right_side_composition(self) -> None:
        result = self.run_builder()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        with Image.open(ASSET_ROOT / "载入背景.png") as image:
            expected = image.convert("RGBA")
        with Image.open(ASSET_ROOT / "六花载入前景.png") as image:
            source_foreground = image.convert("RGBA")
        resized = source_foreground.resize((480, 960), Image.Resampling.LANCZOS)
        expected.alpha_composite(resized, (1280, 32))

        with Image.open(ASSET_ROOT / "leader-art/png/Chuuni_LoadingScene.png") as image:
            actual = image.convert("RGBA")
        with Image.open(ASSET_ROOT / "leader-art/png/Chuuni_Foreground.png") as image:
            standalone = image.convert("RGBA")

        self.assertEqual(
            hashlib.sha256(actual.tobytes()).hexdigest(),
            hashlib.sha256(expected.tobytes()).hexdigest(),
        )
        self.assertEqual(standalone.tobytes(), source_foreground.tobytes())

    def test_fallback_xlp_uses_leader_fallback_class(self) -> None:
        result = self.run_builder()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        fallback_xlp = (ASSET_ROOT / "cooker/XLPs/leaderfallbacks.xlp").read_text(encoding="utf-8")
        fallback_tex = (ASSET_ROOT / "cooker/Images/Textures/Chuuni_Foreground_Fallback.tex").read_text(
            encoding="utf-8"
        )
        self.assertIn('<m_ClassName text="LeaderFallback"/>', fallback_xlp)
        self.assertNotIn('<m_ClassName text="UITexture"/>', fallback_xlp)
        self.assertIn('<m_ClassName text="Leader_Fallback"/>', fallback_tex)
        self.assertIn('<Element text="Leader"/>', fallback_tex)
        self.assertIn('<Element text="Fallback"/>', fallback_tex)


if __name__ == "__main__":
    unittest.main()
