# Chuuni Loading Scene Composition Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the precomposited loading-screen Rikka to the right at `480x960` and `(1280, 32)` without changing the standalone in-game foreground.

**Architecture:** Keep the tracked source images and runtime registrations unchanged. Modify only `build_loading_art` in the Chuuni asset builder, then cook the existing UI package and deploy the validated runtime mod.

**Tech Stack:** Python 3, Pillow, Civilization VI SDK Asset Cooker, PowerShell deployment.

## Global Constraints

- The loading-scene foreground is exactly `480x960`, placed at `(1280, 32)`.
- `Chuuni_Foreground.png` remains `1024x2048` and pixel-equivalent to the tracked source.
- Do not add sharpening or change gameplay, TEX/XLP identifiers, package names, or fallback behavior.

---

### Task 1: Recompose, cook, validate, and deploy the loading scene

**Files:**
- Modify: `tools/chuuni_society/tests/test_build_assets.py`
- Modify: `tools/chuuni_society/build_assets.py`
- Modify after cook: `mods/ChuuniSociety/Platforms/Windows/BLPs/ChuuniUITextureV1.blp`

**Interfaces:**
- Consumes: tracked `assets/ChuuniSociety/六花载入前景.png` and `assets/ChuuniSociety/载入背景.png`.
- Produces: unchanged standalone foreground plus a recomposed `Chuuni_LoadingScene` and cooked UI BLP.

- [ ] **Step 1: Write the failing composition test**

```python
def test_loading_scene_uses_right_side_composition(self) -> None:
    result = self.run_builder()
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    with Image.open(ASSET_ROOT / "载入背景.png") as image:
        expected = image.convert("RGBA")
    with Image.open(ASSET_ROOT / "六花载入前景.png") as image:
        source_foreground = image.convert("RGBA")
    resized = source_foreground.resize((480, 960), Image.Resampling.LANCZOS)
    expected.alpha_composite(resized, (1280, 32))

    with Image.open(ASSET_ROOT / "leader-art/png/Chuuni_LoadingScene.png") as image:
        actual = image.convert("RGBA")
    with Image.open(ASSET_ROOT / "leader-art/png/Chuuni_Foreground.png") as image:
        standalone = image.convert("RGBA")

    self.assertEqual(actual.tobytes(), expected.tobytes())
    self.assertEqual(standalone.tobytes(), source_foreground.tobytes())
```

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```powershell
python -B -m unittest tools.chuuni_society.tests.test_build_assets.BuildAssetsTests.test_loading_scene_uses_right_side_composition -v
```

Expected: FAIL because the current loading scene uses a `560x1120` foreground at `(80, -40)`.

- [ ] **Step 3: Implement the approved composition**

```python
    loading_scene = background.copy()
    scene_foreground = foreground.resize((480, 960), Image.Resampling.LANCZOS)
    loading_scene.alpha_composite(scene_foreground, (1280, 32))
```

- [ ] **Step 4: Verify the generated preview and tests**

Run:

```powershell
python -B -m unittest tools.chuuni_society.tests.test_build_assets -v
powershell -ExecutionPolicy Bypass -File tools\run_civ6_tool_tests.ps1
git diff --check
```

Expected: composition and unified tests pass, all static checks exit `0`, and the generated loading PNG visually places Rikka to the right without overlapping the text panel.

- [ ] **Step 5: Cook and deploy**

Run:

```powershell
python -B tools\chuuni_society\cook_assets.py --sdk-root "D:\SteamLibrary\steamapps\common\Sid Meier's Civilization VI SDK"
powershell -ExecutionPolicy Bypass -File tools\far_east_magic_nap_society\deploy.ps1
```

Expected: both Chuuni packages cook successfully, static validation passes, and deployment reports the `ChuuniSociety` Mods target.

- [ ] **Step 6: Commit**

```powershell
git add tools/chuuni_society/build_assets.py tools/chuuni_society/tests/test_build_assets.py mods/ChuuniSociety/Platforms/Windows/BLPs/ChuuniUITextureV1.blp
git commit -m "fix(chuuni): reposition loading scene portrait"
```
