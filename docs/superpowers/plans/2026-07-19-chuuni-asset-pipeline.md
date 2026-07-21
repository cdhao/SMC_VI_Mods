# Chuuni Society Asset Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the ten approved Chuuni Society PNG sources into self-contained Civilization VI icons, loading art and cooked runtime BLP packages without a Grace Ashcroft dependency.

**Architecture:** A manifest-driven Python builder normalizes source images, generates all Civ6 icon sizes and RGBA DDS/TEX/XLP cooker inputs, and composes leader loading art. A separate cooker wrapper invokes the official SDK and copies only validated BLPs into the runtime mod; SQL and ArtDefs register the outputs while keeping original-game icon aliases as fallback definitions.

**Tech Stack:** Python 3, Pillow, `tools.common.civ6_texture`, Civilization VI Asset Cooker, SQL, ArtDef XML, `unittest`.

## Global Constraints

- Work directly on `main`, as explicitly approved by the user.
- Do not overwrite or rename the ten user PNG sources.
- Do not add a runtime dependency on `mods/GraceAshcroft`.
- Use `PF_R8G8B8A8_UNORM`-compatible RGBA DDS output.
- Preserve the shared Magic Circle image for the building and teleport action.
- Keep original-game icon aliases as pre-cook fallback mappings.

---

### Task 1: Normalize sources and generate deterministic asset inputs

**Files:**
- Modify: `tools/chuuni_society/prepare_logo.py`
- Create: `tools/chuuni_society/build_assets.py`
- Create: `tools/chuuni_society/tests/test_build_assets.py`
- Create: `assets/ChuuniSociety/mod-build.toml`

**Interfaces:**
- Produces `prepare_icon(image, *, preserve_square=False) -> Image.Image`.
- Produces `build() -> None`, writing normalized PNG, RGBA DDS, TEX and XLP inputs.

- [ ] Write failing tests asserting safe transparent padding, exact icon entry names, loading scene size and source-file immutability.
- [ ] Run `python -B -m unittest tools.chuuni_society.tests.test_build_assets -v` and confirm failures are caused by missing builder interfaces.
- [ ] Implement manifest loading, source mappings, normalization, loading composition and generated output writing.
- [ ] Run focused tests and verify every assertion passes.
- [ ] Commit source preparation and deterministic build inputs.

### Task 2: Add cooker plan and runtime art registrations

**Files:**
- Create: `tools/chuuni_society/cook_assets.py`
- Create: `tools/chuuni_society/tests/test_cook_assets.py`
- Create: `mods/ChuuniSociety/ArtDefs/FallbackLeaders.artdef`
- Create: `projects/ChuuniSociety/ChuuniSociety.Art.xml`
- Create: `projects/ChuuniSociety/ChuuniSociety.civ6proj`
- Create: `projects/ChuuniSociety/ChuuniSociety.civ6sln`
- Modify: `mods/ChuuniSociety/Icons/ChuuniIcons.sql`
- Modify: `mods/ChuuniSociety/Data/Config.sql`
- Modify: `mods/ChuuniSociety/Data/Core.sql`
- Modify: `mods/ChuuniSociety/ChuuniSociety.modinfo`

**Interfaces:**
- Produces `build_cook_plan(config) -> tuple[CookPackage, ...]` for `ChuuniUITextureV1` and `ChuuniLeaderFallbacks`.
- Registers custom civilization, leader, district, building, resource, governor, improvement and teleport icons.

- [ ] Write failing tests for package names, runtime BLP paths, custom atlas definitions and leader loading/fallback identifiers.
- [ ] Run focused tests and confirm contract failures.
- [ ] Implement cooker wrapper, project files, DEP/ArtDef registrations and SQL/manifest integration.
- [ ] Run the asset builder and cooker dry-run; verify paths and package names.
- [ ] Commit runtime registrations.

### Task 3: Cook, validate and preview runtime assets

**Files:**
- Create: `tools/chuuni_society/check_static.py`
- Create: `tools/chuuni_society/check_static.ps1`
- Create: `mods/ChuuniSociety/ChuuniSociety.dep`
- Create: `mods/ChuuniSociety/Platforms/Windows/BLPs/ChuuniUITextureV1.blp`
- Create: `mods/ChuuniSociety/Platforms/Windows/BLPs/ChuuniLeaderFallbacks.blp`
- Modify: `tools/far_east_magic_nap_society/check_static.py`

**Interfaces:**
- Produces `python tools/chuuni_society/check_static.py` with exit code 0 only for a complete asset chain.

- [ ] Write failing static contracts for RGBA DDS headers, XLP/TEX inventory, DEP libraries, BLP entries and `.modinfo` inventory.
- [ ] Run the focused checker tests and confirm missing runtime packages fail.
- [ ] Cook both XLP packages with the installed Civ6 SDK and copy them into the mod.
- [ ] Render representative 22, 64 and 256 pixel PNG previews and inspect emblem legibility, alpha padding and leader composition.
- [ ] Run `python -B -m unittest tools.chuuni_society.tests -v`, `python tools/chuuni_society/check_static.py`, `python tools/far_east_magic_nap_society/check_static.py`, and `powershell -ExecutionPolicy Bypass -File tools/run_civ6_tool_tests.ps1`.
- [ ] Commit the validated runtime asset package.
