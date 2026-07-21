"""Tests for reusable Civilization VI static-check helpers."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tools.common.civ6_static_checks import runtime_mod_paths


class RuntimeLayoutTests(unittest.TestCase):
    def test_reports_only_build_inputs_in_a_runtime_mod(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            mod_root = Path(temporary_directory)
            (mod_root / "Images").mkdir()
            (mod_root / "Images" / "input.dds").write_bytes(b"DDS ")
            (mod_root / "Icons").mkdir()
            (mod_root / "Icons" / "entry.tex").write_text("input", encoding="utf-8")
            (mod_root / "ExampleMod.civ6proj").write_text("project", encoding="utf-8")
            (mod_root / "Data").mkdir()
            (mod_root / "Data" / "Gameplay.sql").write_text("SELECT 1;", encoding="utf-8")

            forbidden = runtime_mod_paths(
                mod_root,
                project_file_names={"ExampleMod.civ6proj"},
            )

        self.assertEqual(
            forbidden,
            [
                Path("ExampleMod.civ6proj"),
                Path("Icons/entry.tex"),
                Path("Images"),
                Path("Images/input.dds"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
