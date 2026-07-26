# Chuuni District, Building, Adjacency and Portrait Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore Holy Site art for the Society, restore Missionary unlocking through the Magic Circle, replace obsolete adjacency logic with native rows, and generate a circular Rikka icon.

**Architecture:** Gameplay fixes stay in `DistrictBuilding.sql` and use original database tables so the city UI calculates and displays them natively. District presentation uses a small ArtDef that references original Holy Site assets. Portrait correction happens before cooking through an antialiased alpha mask, and the Cooker gains a selector so only the changed UI package is rebuilt.

**Tech Stack:** Civilization VI Gathering Storm SQL/schema, Civ6 ArtDef/DEP XML, Python 3/Pillow, official Civilization VI Asset Cooker, `unittest`.

## Global Constraints

- Support only the Gathering Storm `Expansion2` ruleset.
- Keep `BUILDING_CLUB_MAGIC_CIRCLE` as the replacement for `BUILDING_SHRINE`.
- Preserve all original Holy Site adjacency rules.
- Do not redesign the Chuuni Value popup.
- Do not add custom 3D assets or change loading/fallback leader art.
- Cook only `ChuuniUITextureV1` for the portrait correction.
- Use the current branch as previously authorized.

---

### Task 1: Restore Missionary Unlock and Native Adjacency

**Files:**
- Modify: `mods/ChuuniSociety/Data/DistrictBuilding.sql`
- Modify: `mods/ChuuniSociety/Text/Chuuni_zh_Hans_CN.sql`
- Modify: `tools/far_east_magic_nap_society/tests/test_check_static.py`
- Modify: `tools/far_east_magic_nap_society/check_static.py`

**Interfaces:**
- Consumes: base `Unit_BuildingPrereqs`, `District_Adjacencies`, `Adjacency_YieldChanges`, `DistrictReplaces`.
- Produces: Missionary/Magic Circle prerequisite and native Society adjacency rows.

- [ ] **Step 1: Add failing gameplay contracts**

Add assertions requiring:

```python
self.assertIn(
    "('UNIT_MISSIONARY', 'BUILDING_CLUB_MAGIC_CIRCLE'",
    district_text,
)
self.assertNotIn("CHUUNI_SOCIETY_ADJACENT_CAMPUS_FAITH", district_text)
self.assertIn("CHUUNI_SOCIETY_ADJACENT_WONDER_FAITH", district_text)
self.assertIn("DISTRICT_ENTERTAINMENT_COMPLEX", district_text)
self.assertIn("DISTRICT_WATER_ENTERTAINMENT_COMPLEX", district_text)
```

Extend the schema test with base Missionary/Shrine prerequisite setup and
assert the custom prerequisite, per-Campus/per-Wonder rows and exact receiver
district groups.

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```powershell
python -B -m unittest tools.far_east_magic_nap_society.tests.test_check_static.ChuuniStaticTests.test_society_and_magic_circle_contracts
python -B -m unittest tools.far_east_magic_nap_society.tests.test_check_static.ChuuniStaticTests.test_gameplay_sql_executes_against_expansion2_schema
```

Expected: failures for the missing Missionary prerequisite and missing native
adjacency rows.

- [ ] **Step 3: Implement the SQL and localization**

Insert the Missionary prerequisite by selecting `NumSupported` from the
Shrine row. Delete the fixed +3 Modifier/Requirement block. Create native
Society-to-Campus and Society-to-Wonder faith rows plus reciprocal rows for:

```text
Campus -> Science
Theater Square -> Culture
Entertainment Complex -> Culture
Water Park -> Culture
Industrial Zone -> Production
```

Include unique replacements through `DistrictReplaces`; do not create
Commercial Hub, Harbor or Holy Site receiver rows. Update the district text to
state per-neighbor +2 values.

- [ ] **Step 4: Run focused and full gameplay tests**

Run:

```powershell
python -B -m unittest tools.far_east_magic_nap_society.tests.test_check_static
powershell -NoProfile -ExecutionPolicy Bypass -File tools\far_east_magic_nap_society\check_static.ps1
```

Expected: all Chuuni gameplay/static tests pass.

- [ ] **Step 5: Commit the gameplay fix**

```powershell
git add mods/ChuuniSociety/Data/DistrictBuilding.sql mods/ChuuniSociety/Text/Chuuni_zh_Hans_CN.sql tools/far_east_magic_nap_society/check_static.py tools/far_east_magic_nap_society/tests/test_check_static.py
git commit -m "fix(chuuni): restore missionary and native adjacency"
```

---

### Task 2: Inherit Holy Site District Art

**Files:**
- Create: `mods/ChuuniSociety/ArtDefs/Districts.artdef`
- Modify: `projects/ChuuniSociety/ChuuniSociety.Art.xml`
- Modify: `mods/ChuuniSociety/ChuuniSociety.dep`
- Modify: `mods/ChuuniSociety/ChuuniSociety.modinfo`
- Modify: `tools/chuuni_society/tests/test_cook_assets.py`
- Modify: `tools/chuuni_society/check_static.py`
- Modify: `tools/far_east_magic_nap_society/tests/test_check_static.py`
- Modify: `tools/far_east_magic_nap_society/check_static.py`

**Interfaces:**
- Consumes: original Holy Site ArtDef identifiers.
- Produces: `DISTRICT_CHUUNI_SOCIETY` world/strategic/audio mapping.

- [ ] **Step 1: Add failing ArtDef registration tests**

Require these identifiers and registrations:

```text
DISTRICT_HOLY_SITE
HolySite
HolySite_Pillaged
HolySite_UnderConstruction
Build_District_HolySite
PLAY_AMBIENCE_DISTRICT_HOLYSITE
STOP_AMBIENCE_DISTRICT_HOLYSITE
ArtDefs/Districts.artdef
```

- [ ] **Step 2: Run focused tests and verify RED**

Run:

```powershell
python -B -m unittest tools.chuuni_society.tests.test_cook_assets.CookAssetsTests.test_runtime_registrations_use_custom_loading_and_icons
python -B -m unittest tools.far_east_magic_nap_society.tests.test_check_static.ChuuniStaticTests.test_modinfo_registers_core_gameplay_files
```

Expected: failure because `Districts.artdef` does not exist or is not declared.

- [ ] **Step 3: Add the Holy Site reference ArtDef and registrations**

Create the ArtDef from the existing Grace district pattern with the exact Holy
Site references. Add `Audio`, `StrategicView_Translate` and
`WorldView_Translate` consumers to the art project and `.dep`; add the ArtDef
dependency and runtime file declaration.

- [ ] **Step 4: Validate the art chain**

Run:

```powershell
python -B -m unittest tools.chuuni_society.tests.test_cook_assets
python -B tools/chuuni_society/check_static.py
python -B tools/far_east_magic_nap_society/check_static.py
```

Expected: all commands exit `0` without invoking the official Cooker.

- [ ] **Step 5: Commit the ArtDef fix**

```powershell
git add mods/ChuuniSociety/ArtDefs/Districts.artdef projects/ChuuniSociety/ChuuniSociety.Art.xml mods/ChuuniSociety/ChuuniSociety.dep mods/ChuuniSociety/ChuuniSociety.modinfo tools/chuuni_society/check_static.py tools/chuuni_society/tests/test_cook_assets.py tools/far_east_magic_nap_society/check_static.py tools/far_east_magic_nap_society/tests/test_check_static.py
git commit -m "fix(chuuni): inherit holy site district art"
```

---

### Task 3: Generate and Cook a Circular Rikka Icon

**Files:**
- Modify: `tools/chuuni_society/build_assets.py`
- Modify: `tools/chuuni_society/cook_assets.py`
- Modify: `tools/chuuni_society/tests/test_cook_assets.py`
- Modify: `tools/chuuni_society/check_static.py`
- Regenerate: `assets/ChuuniSociety/generated/icons/png/Chuuni_Icon_Rikka_*.png`
- Regenerate: `assets/ChuuniSociety/generated/icons/dds/Chuuni_Icon_Rikka_*.dds`
- Replace: `mods/ChuuniSociety/Platforms/Windows/BLPs/ChuuniUITextureV1.blp`

**Interfaces:**
- Produces: `apply_circular_alpha(image: Image.Image) -> Image.Image`.
- Produces: `cook_assets.py --package ui`.

- [ ] **Step 1: Add failing circle and package-selection tests**

Build assets in the test, open `Chuuni_Icon_Rikka_64.png`, and assert:

```python
self.assertEqual(icon.getpixel((0, 0))[3], 0)
self.assertEqual(icon.getpixel((63, 0))[3], 0)
self.assertGreater(icon.getpixel((32, 32))[3], 0)
```

Assert `--package ui --dry-run` prints only:

```text
ChuuniUITextureV1.xlp
```

and does not print `leaderfallbacks.xlp`.

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```powershell
python -B -m unittest tools.chuuni_society.tests.test_cook_assets
```

Expected: the corner-alpha assertion and package-selector assertion fail.

- [ ] **Step 3: Implement the circular mask and selector**

Use a 4x supersampled grayscale ellipse mask, downsample it with LANCZOS, and
combine it with the existing source alpha. Change only Rikka's icon mode to
`leader_circle`. Add `--package {all,ui,leader-fallback}` and filter the cook
plan before calling the official Cooker.

- [ ] **Step 4: Verify GREEN before cooking**

Run:

```powershell
python -B -m unittest tools.chuuni_society.tests.test_cook_assets
python -B tools/chuuni_society/build_assets.py
python -B tools/chuuni_society/check_static.py
```

Expected: generated Rikka corners are transparent and all static checks pass
against the still-current BLP inventory.

- [ ] **Step 5: Cook only the UI package**

Run:

```powershell
python -B tools/chuuni_society/cook_assets.py --package ui
```

Expected: exactly one official Cooker invocation for
`ChuuniUITextureV1.xlp`; `ChuuniLeaderFallbacks.blp` hash remains unchanged.

- [ ] **Step 6: Validate and visually inspect the generated icon**

Run:

```powershell
python -B tools/chuuni_society/check_static.py
python -B -m unittest tools.chuuni_society.tests.test_cook_assets
```

Inspect:

```text
assets/ChuuniSociety/generated/icons/png/Chuuni_Icon_Rikka_256.png
```

Expected: circular portrait, transparent corners, no change to loading art.

- [ ] **Step 7: Commit the portrait fix**

```powershell
git add tools/chuuni_society/build_assets.py tools/chuuni_society/cook_assets.py tools/chuuni_society/check_static.py tools/chuuni_society/tests/test_cook_assets.py mods/ChuuniSociety/Platforms/Windows/BLPs/ChuuniUITextureV1.blp
git commit -m "fix(chuuni): render circular leader portrait"
```

---

### Task 4: Final Validation, Status and Deployment

**Files:**
- Modify: `docs/superpowers/plans/2026-07-19-chuuni-society-v0.1.md`

**Interfaces:**
- Consumes: Tasks 1–3.
- Produces: deployed runtime and in-game verification checklist.

- [ ] **Step 1: Record implementation status accurately**

Mark the four fixes `已实现未实机验证`; do not claim the district model,
Missionary purchase, adjacency previews or circular in-game rendering are
`已实机验证`.

- [ ] **Step 2: Run fresh complete verification**

Run:

```powershell
python -B -m unittest tools.far_east_magic_nap_society.tests.test_check_static
python -B -m unittest tools.chuuni_society.tests.test_cook_assets
python -B tools/chuuni_society/check_static.py
powershell -NoProfile -ExecutionPolicy Bypass -File tools\far_east_magic_nap_society\check_static.ps1
git diff --check
```

Expected: zero failures and zero diff errors.

- [ ] **Step 3: Deploy only ChuuniSociety**

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools\far_east_magic_nap_society\deploy.ps1
```

Compare every deployed runtime file SHA-256 with
`mods/ChuuniSociety`; expected mismatch count is zero.

- [ ] **Step 4: Commit status and hand off in-game checks**

```powershell
git add docs/superpowers/plans/2026-07-19-chuuni-society-v0.1.md
git commit -m "docs(chuuni): record district and portrait fixes"
```

Hand off the ten in-game checks from the approved design, with the four user
priorities listed first.
