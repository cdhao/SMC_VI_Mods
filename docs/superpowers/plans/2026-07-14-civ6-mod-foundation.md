# Civ6 Mod Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve the Grace Ashcroft development lessons and provide a version-safe foundation for future Civilization VI civilization and leader mods.

**Architecture:** Keep gameplay and art generation mod-specific. Move only stable configuration parsing, Asset Cooker execution, and reusable static validation helpers into `tools/common`. Each mod owns one TOML build manifest; Python reads it for generation, cooking, and validation while PowerShell remains a compatibility launcher.

**Tech Stack:** Python 3.11+ standard library (`tomllib`, `subprocess`, `unittest`), existing Pillow image generation, Civilization VI Asset Cooker, PowerShell wrappers.

## Global Constraints

- Do not change Grace gameplay SQL, Lua behavior, source images, or currently deployed BLP package names.
- `assets/<Mod>/` stores editable sources and cooker inputs; `mods/<Mod>/` stores runtime files only.
- Every new asset package name and BLP must include a mod namespace and asset revision.
- SDK and installation paths remain environment variables, never repository configuration.
- Validation must fail before a cook/deploy operation when manifest and runtime package references disagree.

---

### Task 1: Create the shared TOML manifest contract

**Files:**
- Create: `tools/common/civ6_mod_config.py`
- Create: `tools/common/tests/test_civ6_mod_config.py`
- Create: `assets/GraceAshcroft/mod-build.toml`

**Interfaces:**
- Produces `load_mod_config(path: Path) -> ModBuildConfig`.
- Produces `ModBuildConfig.package_names` and `ModBuildConfig.render(template: str)`.

- [ ] Write tests for package-template rendering, duplicate package rejection, and path defaults.
- [ ] Run the tests and confirm import failure before implementation.
- [ ] Implement TOML loading with Python `tomllib`; keep all version values in the manifest.
- [ ] Add Grace's current release version, current asset revision, and current package names without renaming any package.
- [ ] Run the tests and confirm success.

### Task 2: Move Grace cook orchestration to Python

**Files:**
- Create: `tools/common/civ6_asset_cooker.py`
- Create: `tools/grace_ashcroft/cook_assets.py`
- Modify: `tools/grace_ashcroft/cook_assets.ps1`
- Test: `tools/grace_ashcroft/tests/test_cook_assets.py`

**Interfaces:**
- `run_asset_cooker(cooker, config, pantry, stewpot, xlp)` invokes one XLP cook.
- `cook_assets.py --dry-run` prints the resolved package plan without invoking the SDK.

- [ ] Write tests asserting the manifest drives the package list and the dry-run has no file changes.
- [ ] Run the tests and confirm failure before implementation.
- [ ] Implement the shared subprocess helper and Grace Python cook command.
- [ ] Replace PowerShell logic with a compatibility wrapper that forwards arguments to Python.
- [ ] Run the dry-run, static validator, and unit tests.

### Task 3: Extract reusable static validation helpers

**Files:**
- Create: `tools/common/civ6_static_checks.py`
- Modify: `tools/grace_ashcroft/check_static.py`
- Test: `tools/grace_ashcroft/tests/test_check_static.py`

**Interfaces:**
- Shared helpers validate files, text contracts, DDS headers, BLP entries, and runtime-directory exclusions.
- Grace retains only its gameplay, Lua, localization, and icon contracts.

- [ ] Write tests for the shared runtime-layout and package-reference validators.
- [ ] Run the tests and confirm failure before implementation.
- [ ] Move generic helpers out of the Grace-only checker.
- [ ] Validate Grace's `.dep`, `.modinfo`, XLP package names, and cook list against `mod-build.toml`.
- [ ] Run all static tests and compatibility entry points.

### Task 4: Add future-mod scaffold and retained knowledge base

**Files:**
- Create: `templates/civ6-leader-mod/`
- Create: `tools/scaffold_civ6_leader_mod.py`
- Create: `docs/civ6/README.md`
- Create: `docs/civ6/asset-pipeline.md`
- Create: `docs/civ6/runtime-patterns.md`
- Create: `docs/civ6/troubleshooting.md`
- Create: `docs/civ6/release-checklist.md`
- Test: `tools/common/tests/test_scaffold_civ6_leader_mod.py`

**Interfaces:**
- `python tools/scaffold_civ6_leader_mod.py --slug ExampleMod --display-name "Example Mod"` creates isolated `assets/`, `mods/`, `projects/`, and `tools/` paths from the template.
- The scaffold uses unique versioned UI, resource, and leader-fallback package names.

- [ ] Write a temporary-directory scaffold test that checks namespacing and required files.
- [ ] Run the test and confirm failure before implementation.
- [ ] Add the minimal runtime/template structure and scaffold command.
- [ ] Record validated facts and rejected approaches from Grace, clearly separating historical notes from current rules.
- [ ] Run scaffold tests, static validation, and workspace cleanup in `-WhatIf` mode.
