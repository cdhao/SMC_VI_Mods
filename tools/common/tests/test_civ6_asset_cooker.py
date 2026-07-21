"""Contracts for launching the official Civilization VI Asset Cooker."""

from __future__ import annotations

import os
import subprocess
import unittest
from pathlib import Path
from unittest import mock

from tools.common.civ6_asset_cooker import AssetCookerPaths, cook_xlp


class AssetCookerLaunchTests(unittest.TestCase):
    @unittest.skipUnless(os.name == "nt", "Windows priority contract")
    def test_cooker_starts_below_normal_priority_on_windows(self) -> None:
        paths = AssetCookerPaths(
            Path("Civ6AssetCooker_FinalRelease.exe"),
            Path("Civ6.cfg"),
        )

        with mock.patch("tools.common.civ6_asset_cooker.subprocess.run") as run:
            cook_xlp(paths, cooker_root=Path("cooker"), xlp_name="UI.xlp")

        self.assertIn("creationflags", run.call_args.kwargs)
        self.assertEqual(
            run.call_args.kwargs.get("creationflags"),
            subprocess.BELOW_NORMAL_PRIORITY_CLASS,
        )


if __name__ == "__main__":
    unittest.main()
