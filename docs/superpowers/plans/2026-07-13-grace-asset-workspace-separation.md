# Grace Asset Workspace Separation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Separate Grace Ashcroft cooker inputs and ModBuddy project files from the deployable Civilization VI mod while preserving the currently validated runtime BLP packages.

**Architecture:** `assets/GraceAshcroft/cooker` becomes the complete Asset Cooker pantry, XLP, log, and temporary output workspace. `projects/GraceAshcroft` contains only the ModBuddy solution/project/art specification. `mods/GraceAshcroft` contains gameplay files, ArtDefs, DEP, MODINFO, and cooked BLP runtime packages.

**Tech Stack:** Python 3/Pillow asset generation, PowerShell orchestration and static checks, Civilization VI Asset Cooker, ModBuddy MSBuild project files.

## Global Constraints

- Do not change Grace gameplay, localization, Lua, balance, or icon SQL behavior.
- Preserve `GraceUITexture.blp`, `GraceResourceIconsV2.blp`, and `LeaderFallbacks.blp` as runtime packages.
- Record the first-click save-loading icon failure as a known front-end initialization issue; do not claim it is fixed.
- Keep deployment as a complete copy of `mods/GraceAshcroft` after that directory becomes runtime-only.

---

### Task 1: Define runtime-only layout checks

**Files:**
- Modify: `tools/grace_ashcroft/check_static.ps1`
- Modify: `tools/_check_grace_mod_static_impl.ps1`

- [ ] Add assertions that cooker inputs (`Images`, `XLPs`, `.tex`, `.xlp`, logs) and ModBuddy project files do not exist under `mods/GraceAshcroft`.
- [ ] Add assertions for required cooker and project paths under `assets/GraceAshcroft/cooker` and `projects/GraceAshcroft`.
- [ ] Run the static checker and confirm it fails against the current mixed layout.

### Task 2: Move cooker generation and cooking

**Files:**
- Modify: `tools/grace_ashcroft/build_assets.py`
- Modify: `tools/grace_ashcroft/cook_assets.ps1`
- Create: `assets/GraceAshcroft/cooker/Images/Textures/*.tex`
- Create: `assets/GraceAshcroft/cooker/XLPs/*.xlp`
- Runtime output: `mods/GraceAshcroft/Platforms/Windows/BLPs/*.blp`

- [ ] Redirect all generated TEX, temporary DDS, XLP, and logs to the cooker workspace.
- [ ] Cook into a cooker-local BLP output directory, validate outputs, and copy only BLP results into the runtime mod.
- [ ] Keep cleanup and obsolete-version logic scoped to generated/cooker files and runtime BLP outputs.

### Task 3: Separate ModBuddy project metadata

**Files:**
- Move: `mods/GraceAshcroft/GraceAshcroft.Art.xml` to `projects/GraceAshcroft/GraceAshcroft.Art.xml`
- Move: `mods/GraceAshcroft/GraceAshcroft.civ6proj` to `projects/GraceAshcroft/GraceAshcroft.civ6proj`
- Move: `mods/GraceAshcroft/GraceAshcroft.civ6sln` to `projects/GraceAshcroft/GraceAshcroft.civ6sln`
- Remove from source control: `mods/GraceAshcroft/GraceAshcroft.v12.civ6suo`
- Modify: `projects/GraceAshcroft/GraceAshcroft.civ6proj`

- [ ] Point project content links to runtime files and cooker inputs using repository-relative paths.
- [ ] Keep ModBuddy metadata out of deployment.

### Task 4: Reduce runtime manifest and document workflow

**Files:**
- Modify: `mods/GraceAshcroft/GraceAshcroft.modinfo`
- Modify: `docs/civ6-mod-workflow.md`
- Modify: `docs/mods/grace-ashcroft-assets.md`
- Modify: `.gitignore`

- [ ] Remove TEX and XLP build inputs from the MODINFO file list.
- [ ] Document source, generated, cooker, project, runtime, and deployment responsibilities.
- [ ] Document the verified in-game icon fix and unresolved first-click save-list issue separately.

### Task 5: Rebuild and verify

**Files:**
- Verify all files above.

- [ ] Run asset generation and confirm it does not repopulate cooker inputs under `mods/GraceAshcroft`.
- [ ] Run the Asset Cooker and confirm all required BLP outputs are copied to the runtime mod.
- [ ] Run static checks and workspace cleanup.
- [ ] Inspect `git diff --check`, runtime file inventory, and project/cooker inventories.
