"""Tests for Chuuni Society source-logo preparation."""

from __future__ import annotations

import unittest

from PIL import Image

from tools.chuuni_society.prepare_logo import extract_white_emblem


class ExtractWhiteEmblemTests(unittest.TestCase):
    def test_maps_black_to_transparent_and_white_to_opaque(self) -> None:
        source = Image.new("RGB", (3, 1))
        source.putdata(((0, 0, 0), (128, 128, 128), (255, 255, 255)))

        result = extract_white_emblem(source, black_point=0, white_point=255)

        self.assertEqual(result.mode, "RGBA")
        self.assertEqual(result.getpixel((0, 0)), (255, 255, 255, 0))
        self.assertEqual(result.getpixel((2, 0)), (255, 255, 255, 255))
        self.assertGreater(result.getpixel((1, 0))[3], 0)
        self.assertLess(result.getpixel((1, 0))[3], 255)

    def test_rejects_invalid_tonal_range(self) -> None:
        with self.assertRaisesRegex(ValueError, "black_point"):
            extract_white_emblem(Image.new("RGB", (1, 1)), 200, 100)


if __name__ == "__main__":
    unittest.main()
