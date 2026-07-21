"""Tests for the Civilization VI civilization-plus-leader scaffold."""

from __future__ import annotations

import unittest
import uuid
from pathlib import Path
from tempfile import TemporaryDirectory

from tools.scaffold_civ6_leader_mod import scaffold_mod


class ScaffoldModTests(unittest.TestCase):
    def test_creates_isolated_roots_and_versioned_manifest(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            repo_root = Path(temporary_directory)

            scaffold_mod(repo_root, slug="TestLeader", display_name="Test Leader")

            manifest = (repo_root / "assets" / "TestLeader" / "mod-build.toml").read_text(
                encoding="utf-8"
            )
            modinfo = (repo_root / "mods" / "TestLeader" / "TestLeader.modinfo").read_text(
                encoding="utf-8"
            )

        self.assertIn('slug = "TestLeader"', manifest)
        self.assertIn('ui = "TestLeaderUIV{asset_version}"', manifest)
        self.assertIn('resource = "TestLeaderResourceIconsV{asset_version}"', manifest)
        self.assertIn('leader_fallback = "TestLeaderLeaderFallbacksV{asset_version}"', manifest)
        self.assertIn('version="1"', modinfo)
        mod_id = modinfo.split('id="', maxsplit=1)[1].split('"', maxsplit=1)[0]
        self.assertIsInstance(uuid.UUID(mod_id), uuid.UUID)

    def test_refuses_to_overwrite_an_existing_mod_root(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            repo_root = Path(temporary_directory)
            (repo_root / "mods" / "ExistingMod").mkdir(parents=True)

            with self.assertRaisesRegex(FileExistsError, "already exists"):
                scaffold_mod(repo_root, slug="ExistingMod", display_name="Existing")


if __name__ == "__main__":
    unittest.main()
