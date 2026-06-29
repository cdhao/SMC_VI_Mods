#!/usr/bin/env python3
"""Compatibility entry point for the Grace Ashcroft asset builder."""

from __future__ import annotations

import runpy
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "grace_ashcroft" / "build_assets.py"
runpy.run_path(str(TARGET), run_name="__main__")
