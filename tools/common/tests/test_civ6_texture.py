"""Contracts for reusable Civilization VI texture helpers."""

from __future__ import annotations

import errno
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from PIL import Image

from tools.common.civ6_texture import save_png_atomic, write_bytes_atomic, write_rgba_dds


REPO_ROOT = Path(__file__).resolve().parents[3]


class TextureWriteTests(unittest.TestCase):
    def test_binary_copy_replaces_final_path_atomically(self) -> None:
        scratch_root = REPO_ROOT / ".tmp"
        scratch_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch_root) as temp_dir:
            target = Path(temp_dir) / "texture.dds"
            target.write_bytes(b"existing texture")
            real_write_bytes = Path.write_bytes

            def reject_direct_overwrite(path: Path, data: bytes) -> int:
                if path == target:
                    raise OSError(errno.EINVAL, "simulated transient final-path lock", str(path))
                return real_write_bytes(path, data)

            with mock.patch.object(Path, "write_bytes", reject_direct_overwrite):
                write_bytes_atomic(b"replacement texture", target)

            self.assertEqual(target.read_bytes(), b"replacement texture")

    def test_png_atomic_write_retries_a_transient_replace_lock(self) -> None:
        scratch_root = REPO_ROOT / ".tmp"
        scratch_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch_root) as temp_dir:
            target = Path(temp_dir) / "texture.png"
            target.write_bytes(b"existing texture")
            real_replace = os.replace
            attempts = 0

            def transient_lock(source: object, destination: object) -> None:
                nonlocal attempts
                attempts += 1
                if attempts < 3:
                    raise PermissionError(errno.EACCES, "simulated transient replace lock", str(destination))
                real_replace(source, destination)

            with mock.patch("tools.common.civ6_texture.os.replace", transient_lock):
                save_png_atomic(Image.new("RGBA", (2, 2), (255, 255, 255, 255)), target)

            self.assertEqual(attempts, 3)
            self.assertEqual(target.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")

    def test_png_write_replaces_final_path_atomically(self) -> None:
        scratch_root = REPO_ROOT / ".tmp"
        scratch_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch_root) as temp_dir:
            target = Path(temp_dir) / "texture.png"
            target.write_bytes(b"existing texture")
            real_save = Image.Image.save

            def reject_direct_overwrite(image: Image.Image, destination: object, *args: object, **kwargs: object) -> None:
                if Path(destination) == target:
                    raise OSError(errno.EINVAL, "simulated transient final-path lock", str(target))
                real_save(image, destination, *args, **kwargs)

            with mock.patch.object(Image.Image, "save", reject_direct_overwrite):
                save_png_atomic(Image.new("RGBA", (2, 2), (255, 255, 255, 255)), target)

            self.assertEqual(target.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")

    def test_dds_write_replaces_final_path_atomically(self) -> None:
        scratch_root = REPO_ROOT / ".tmp"
        scratch_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch_root) as temp_dir:
            target = Path(temp_dir) / "texture.dds"
            target.write_bytes(b"existing texture")
            real_write_bytes = Path.write_bytes

            def reject_direct_overwrite(path: Path, data: bytes) -> int:
                if path == target:
                    raise OSError(errno.EINVAL, "simulated transient final-path lock", str(path))
                return real_write_bytes(path, data)

            with mock.patch.object(Path, "write_bytes", reject_direct_overwrite):
                write_rgba_dds(Image.new("RGBA", (2, 2), (255, 255, 255, 255)), target)

            self.assertEqual(target.read_bytes()[:4], b"DDS ")


if __name__ == "__main__":
    unittest.main()
