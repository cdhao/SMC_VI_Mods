"""Tests for the shared Civilization VI mod build manifest."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tools.common.civ6_mod_config import ConfigError, load_mod_config


def write_manifest(path: Path, package_lines: str) -> None:
    path.write_text(
        """
[mod]
slug = "ExampleMod"
release_version = 3

[paths]
asset_root = "assets/ExampleMod"
runtime_root = "mods/ExampleMod"
project_root = "projects/ExampleMod"

[assets]
revision = 7

[packages]
""".lstrip()
        + package_lines,
        encoding="utf-8",
    )


class ModBuildConfigTests(unittest.TestCase):
    def test_renders_versioned_package_names_from_one_manifest(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            manifest = root / "mod-build.toml"
            write_manifest(
                manifest,
                'ui = "ExampleUIV{asset_version}"\nresource = "ExampleResourceV{asset_version}"\n',
            )

            config = load_mod_config(manifest, repo_root=root)

        self.assertEqual(config.slug, "ExampleMod")
        self.assertEqual(config.release_version, 3)
        self.assertEqual(config.asset_revision, 7)
        self.assertEqual(config.package("ui"), "ExampleUIV7")
        self.assertEqual(config.package_names, ("ExampleUIV7", "ExampleResourceV7"))

    def test_rejects_duplicate_rendered_package_names(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            manifest = root / "mod-build.toml"
            write_manifest(
                manifest,
                'ui = "ExampleIconsV{asset_version}"\nresource = "ExampleIconsV7"\n',
            )

            with self.assertRaisesRegex(ConfigError, "duplicate package"):
                load_mod_config(manifest, repo_root=root)


if __name__ == "__main__":
    unittest.main()
