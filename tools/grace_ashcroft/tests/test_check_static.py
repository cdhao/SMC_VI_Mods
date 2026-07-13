"""Tests for the Grace Ashcroft static validation entry point."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tools.grace_ashcroft.check_static import runtime_mod_paths


REPO_ROOT = Path(__file__).resolve().parents[3]


class RuntimeLayoutTests(unittest.TestCase):
    def test_runtime_mod_excludes_cooker_inputs_and_project_files(self) -> None:
        forbidden = runtime_mod_paths(REPO_ROOT / "mods" / "GraceAshcroft")

        self.assertEqual(forbidden, [])

    def test_runtime_mod_reports_cooker_inputs_and_project_files(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            mod_root = Path(temporary_directory)
            (mod_root / "Images").mkdir()
            (mod_root / "Images" / "input.dds").write_bytes(b"DDS ")
            (mod_root / "Icons").mkdir()
            (mod_root / "Icons" / "entry.tex").write_text("input", encoding="utf-8")
            (mod_root / "GraceAshcroft.civ6proj").write_text("project", encoding="utf-8")

            forbidden = runtime_mod_paths(mod_root)

        self.assertEqual(
            forbidden,
            [
                Path("GraceAshcroft.civ6proj"),
                Path("Icons/entry.tex"),
                Path("Images"),
                Path("Images/input.dds"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
