# Civ6 Generated Asset Git Policy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stop tracking reproducible Civ6 asset intermediates while retaining source assets, build definitions, and runtime mod packages.

**Architecture:** Git ignores four lifecycle directories beneath every `assets/<Mod>` root. The unified validation runner rebuilds GraceAshcroft and ChuuniSociety assets before tests and static checks, so an ignored or absent intermediate tree is reconstructed from committed sources. Runtime BLP, DEP, ArtDef, SQL, Lua, text, ModInfo, manifests, and project definitions remain tracked.

**Tech Stack:** Git ignore/index management, PowerShell, Python 3 with `-B`, Civilization VI asset builders and static checks.

## Global Constraints

- Ignore `assets/*/cooker/`, `assets/*/generated/`, `assets/*/leader-art/`, and `assets/*/processed/`.
- Remove existing intermediates from the Git index only; preserve all local files.
- Preserve original images, `mod-build.toml`, `projects/<Mod>/`, and every runtime file under `mods/<Mod>/`.
- Unified validation must rebuild both GraceAshcroft and ChuuniSociety intermediates before validating them.
- Do not stage, delete, or modify the user's untracked `编辑.af` file.

---

### Task 1: Make Unified Validation Rebuild Ignored Assets

**Files:**
- Modify: `tools/common/tests/test_run_civ6_tool_tests.py:23-31`
- Modify: `tools/run_civ6_tool_tests.ps1:9-38`

**Interfaces:**
- Consumes: `tools/grace_ashcroft/build_assets.py` and `tools/chuuni_society/build_assets.py`, both executable with `python -B` and no arguments.
- Produces: a unified runner that creates PNG, DDS, TEX, and XLP intermediates before executing unit tests and static checks.

- [ ] **Step 1: Add a failing runner-order contract**

Extend `test_runner_includes_chuuni_society_validation` with exact build commands and order checks:

```python
        grace_build = 'python -B (Join-Path $PSScriptRoot "grace_ashcroft\\build_assets.py")'
        chuuni_build = 'python -B (Join-Path $PSScriptRoot "chuuni_society\\build_assets.py")'
        unittest_command = "python -B -m unittest"

        self.assertIn(grace_build, content)
        self.assertIn(chuuni_build, content)
        self.assertLess(content.index(grace_build), content.index(unittest_command))
        self.assertLess(content.index(chuuni_build), content.index(unittest_command))
```

- [ ] **Step 2: Run the focused test and observe failure**

Run:

```powershell
python -B -m unittest tools.common.tests.test_run_civ6_tool_tests.ToolTestRunnerContracts.test_runner_includes_chuuni_society_validation -v
```

Expected: `FAIL` because neither `build_assets.py` command is present in the runner.

- [ ] **Step 3: Add pre-test asset builds to the runner**

At the start of the `try` block in `tools/run_civ6_tool_tests.ps1`, before `python -B -m unittest`, add:

```powershell
    & python -B (Join-Path $PSScriptRoot "grace_ashcroft\build_assets.py")
    if ($LASTEXITCODE -ne 0) {
        throw "Grace Ashcroft asset build failed."
    }

    & python -B (Join-Path $PSScriptRoot "chuuni_society\build_assets.py")
    if ($LASTEXITCODE -ne 0) {
        throw "Chuuni Society asset build failed."
    }
```

- [ ] **Step 4: Run the focused test and unified validation**

Run:

```powershell
python -B -m unittest tools.common.tests.test_run_civ6_tool_tests -v
powershell -ExecutionPolicy Bypass -File tools\run_civ6_tool_tests.ps1
```

Expected: runner contract passes; the unified command reports all tests `OK`, all three static validations pass, and workspace cleanup completes.

- [ ] **Step 5: Commit the runner change**

```powershell
git add tools/common/tests/test_run_civ6_tool_tests.py tools/run_civ6_tool_tests.ps1
git commit -m "test(civ6): rebuild generated assets before validation"
```

### Task 2: Ignore and Untrack Reproducible Asset Trees

**Files:**
- Modify: `.gitignore`
- Index-only removal: `assets/GraceAshcroft/{cooker,generated,leader-art,processed}`
- Index-only removal: `assets/ChuuniSociety/{cooker,generated,leader-art,processed}`

**Interfaces:**
- Consumes: Task 1's pre-validation asset builds.
- Produces: generic ignore policy for current and future Civ6 mods, with source and runtime results still tracked.

- [ ] **Step 1: Add generic lifecycle-directory ignore rules**

Replace mod-specific cooker rules with:

```gitignore
assets/*/cooker/
assets/*/generated/
assets/*/leader-art/
assets/*/processed/
```

Keep unrelated rules such as `sample/`, `.local-docs/`, `*.log`, `mods/GraceAshcroft/Logs/`, and `projects/**/*.civ6suo`.

- [ ] **Step 2: Verify the rules match representative files**

Run:

```powershell
git check-ignore -v --no-index assets/GraceAshcroft/cooker/XLPs/GraceUITexture.xlp assets/GraceAshcroft/generated/icons/dds/GraceAshcroft_Icon_Leader_50.dds assets/GraceAshcroft/leader-art/dds/GraceAshcroft_Background.dds assets/ChuuniSociety/processed/ChuuniSociety_Civilization_WhiteAlpha.png
```

Expected: four lines, each attributed to one of the new generic `.gitignore` rules.

- [ ] **Step 3: Remove process directories from the Git index without deleting local files**

Run:

```powershell
git rm -r --cached --ignore-unmatch -- assets/GraceAshcroft/cooker assets/GraceAshcroft/generated assets/GraceAshcroft/leader-art assets/GraceAshcroft/processed assets/ChuuniSociety/cooker assets/ChuuniSociety/generated assets/ChuuniSociety/leader-art assets/ChuuniSociety/processed
```

Expected: tracked files are staged as deletions while the directories and files remain present on disk.

- [ ] **Step 4: Verify source and runtime boundaries**

Run:

```powershell
$intermediateCount = (git ls-files "assets/*/cooker/**" "assets/*/generated/**" "assets/*/leader-art/**" "assets/*/processed/**" | Measure-Object -Line).Lines
$required = @(
    "assets/GraceAshcroft/mod-build.toml",
    "assets/ChuuniSociety/mod-build.toml",
    "mods/GraceAshcroft/Platforms/Windows/BLPs/GraceUITexture.blp",
    "mods/ChuuniSociety/Platforms/Windows/BLPs/ChuuniUITextureV1.blp"
)
if ($intermediateCount -ne 0) { throw "Tracked intermediate count: $intermediateCount" }
foreach ($path in $required) {
    if (-not (git ls-files --error-unmatch -- $path 2>$null)) { throw "Required tracked file missing: $path" }
}
```

Expected: exit code 0; zero tracked intermediates; all representative manifest/runtime files remain tracked.

- [ ] **Step 5: Run final reconstruction and repository checks**

Run:

```powershell
powershell -ExecutionPolicy Bypass -File tools\run_civ6_tool_tests.ps1
git status --short --ignored
git diff --check
git diff --cached --check
```

Expected: unified validation passes; generated trees appear only with `!!`; staged changes contain `.gitignore` plus intermediate deletions; the user's `编辑.af` remains untracked and unstaged; both diff checks return exit code 0.

- [ ] **Step 6: Commit the Git policy migration**

```powershell
git add .gitignore
git commit -m "chore(civ6): stop tracking generated assets"
```
