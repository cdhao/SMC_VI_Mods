"""Contracts for the cache-safe Civilization VI tool-test entry point."""

from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


class ToolTestRunnerContracts(unittest.TestCase):
    def test_runner_disables_bytecode_and_cleans_in_finally(self) -> None:
        runner = REPO_ROOT / "tools" / "run_civ6_tool_tests.ps1"
        content = runner.read_text(encoding="utf-8")

        self.assertIn("python -B -m unittest", content)
        self.assertIn("try {", content)
        self.assertIn("finally {", content)
        self.assertIn("cleanup_workspace.ps1", content)
        self.assertIn("check_static.py", content)

    def test_runner_includes_chuuni_society_validation(self) -> None:
        runner = REPO_ROOT / "tools" / "run_civ6_tool_tests.ps1"
        content = runner.read_text(encoding="utf-8")

        grace_build = 'python -B (Join-Path $PSScriptRoot "grace_ashcroft\\build_assets.py")'
        chuuni_build = 'python -B (Join-Path $PSScriptRoot "chuuni_society\\build_assets.py")'
        unittest_command = "python -B -m unittest"

        self.assertIn("tools.chuuni_society.tests.test_check_assets", content)
        self.assertIn("tools.chuuni_society.tests.test_cook_assets", content)
        self.assertIn("tools.far_east_magic_nap_society.tests.test_check_static", content)
        self.assertIn('"chuuni_society\\check_static.py"', content)
        self.assertIn('"far_east_magic_nap_society\\check_static.py"', content)
        self.assertIn(grace_build, content)
        self.assertIn(chuuni_build, content)
        self.assertLess(content.index(grace_build), content.index(unittest_command))
        self.assertLess(content.index(chuuni_build), content.index(unittest_command))

    def test_runner_includes_asset_cooker_launch_contract(self) -> None:
        runner = REPO_ROOT / "tools" / "run_civ6_tool_tests.ps1"
        content = runner.read_text(encoding="utf-8")

        self.assertIn("tools.common.tests.test_civ6_asset_cooker", content)


if __name__ == "__main__":
    unittest.main()
