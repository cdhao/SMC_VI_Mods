"""End-to-end static contracts for cooked Chuuni Society assets."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.chuuni_society.check_static import validate_package_inventory
from tools.common.civ6_static_checks import ValidationError


REPO_ROOT = Path(__file__).resolve().parents[3]
CHECK_SCRIPT = REPO_ROOT / "tools" / "chuuni_society" / "check_static.py"


class AssetStaticTests(unittest.TestCase):
    def test_asset_checker_accepts_complete_runtime_chain(self) -> None:
        result = subprocess.run(
            [str(Path(subprocess.sys.executable)), "-B", str(CHECK_SCRIPT)],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_package_inventory_rejects_a_blp_missing_an_xlp_entry(self) -> None:
        scratch_root = REPO_ROOT / ".tmp"
        scratch_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch_root) as temp_dir:
            root = Path(temp_dir)
            tex_root = root / "Textures"
            dds_root = root / "dds"
            tex_root.mkdir()
            dds_root.mkdir()
            xlp = root / "package.xlp"
            blp = root / "package.blp"
            xlp.write_text(
                """<AssetObjects..XLP><m_ClassName text="UITexture"/><m_PackageName text="TestPackage"/><m_Entries>
<Element><m_EntryID text="ENTRY_A"/><m_ObjectName text="ObjectA"/></Element>
<Element><m_EntryID text="ENTRY_B"/><m_ObjectName text="ObjectB"/></Element>
</m_Entries></AssetObjects..XLP>""",
                encoding="utf-8",
            )
            for object_name in ("ObjectA", "ObjectB"):
                (tex_root / f"{object_name}.tex").write_text(
                    f"""<AssetObjects..TextureInstance><m_DataFiles><Element><m_RelativePath text="../{object_name}.dds"/></Element></m_DataFiles><m_Name text="{object_name}"/></AssetObjects..TextureInstance>""",
                    encoding="utf-8",
                )
                (dds_root / f"{object_name}.dds").write_bytes(b"DDS source")
            blp.write_bytes(b"ENTRY_A")

            with self.assertRaisesRegex(ValidationError, "ENTRY_B"):
                validate_package_inventory(
                    xlp_path=xlp,
                    tex_root=tex_root,
                    dds_roots=(dds_root,),
                    blp_path=blp,
                    expected_package="TestPackage",
                    expected_class="UITexture",
                    expected_entries=2,
                )


if __name__ == "__main__":
    unittest.main()
