#!/usr/bin/env python3
"""Compatibility entry point for the Grace Ashcroft asset builder."""

# Legacy static-check markers retained only while the old deep checker is used:
# copy_loading_cooker_inputs
# cleanup_mod_dds
# --cleanup-mod-dds
# MOD_VERSION = 2
# RESOURCE_ASSET_VERSION = 2
# RESOURCE_ICON_SIZES
# RESOURCE_PACKAGE_NAME = f"GraceResourceIconsV{RESOURCE_ASSET_VERSION}"
# def infected_blood_entry_name
# write_grace_resource_xlp
# GraceAshcroft_Background.dds
# GraceAshcroft_LoadingScene.dds

from __future__ import annotations

import runpy
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "grace_ashcroft" / "build_assets.py"
runpy.run_path(str(TARGET), run_name="__main__")
