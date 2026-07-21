# Chuuni Runtime Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Correct the Society adjacency description, restore Magic Circle production and faith purchase, and make stage one grant +3 combat strength.

**Architecture:** Keep static building and adjacency behavior in `DistrictBuilding.sql`. Define the combat modifier in a focused `StageCombat.sql`, then attach it once from the existing progression Lua when stage one is active. Validate both database rows and the Lua attachment contract against the installed Gathering Storm schemas.

**Tech Stack:** Civilization VI Gathering Storm SQL/XML mod database, gameplay Lua, Python `unittest`, PowerShell deployment tooling.

## Global Constraints

- Support Gathering Storm only.
- Preserve Society `+3` Faith when adjacent to at least one Campus and Campus `+2` Science when adjacent to a Society.
- Magic Circle remains production-buildable and additionally purchasable with Faith.
- Stage one requires no founded religion and grants exactly `+3` combat strength.
- Do not modify BLP or other cooked art assets.
- Leave `assets/ChuuniSociety/素材文件 记录用/原始资源/编辑.af` untouched.

---

### Task 1: Magic Circle Production, Purchase, and Description

**Files:**
- Modify: `tools/far_east_magic_nap_society/tests/test_check_static.py`
- Modify: `mods/ChuuniSociety/Data/DistrictBuilding.sql`
- Modify: `mods/ChuuniSociety/Text/Chuuni_zh_Hans_CN.sql`

**Interfaces:**
- Consumes: `BUILDING_CLUB_MAGIC_CIRCLE`, `DISTRICT_CHUUNI_SOCIETY`, and the existing Campus adjacency modifier.
- Produces: a Magic Circle row with `PrereqDistrict='DISTRICT_HOLY_SITE'`, `PurchaseYield='YIELD_FAITH'`, and `MustPurchase=0`.

- [ ] **Step 1: Write failing production and purchase tests**

Add a test that executes the existing SQL fixture and asserts:

```python
self.assertEqual(
    connection.execute(
        """
        SELECT PrereqDistrict, PurchaseYield, MustPurchase
        FROM Buildings
        WHERE BuildingType = 'BUILDING_CLUB_MAGIC_CIRCLE'
        """
    ).fetchone(),
    ("DISTRICT_HOLY_SITE", "YIELD_FAITH", 0),
)
```

Add `TEXT_SQL = REPO_ROOT / "mods" / "ChuuniSociety" / "Text" / "Chuuni_zh_Hans_CN.sql"` and this test:

```python
def test_society_adjacency_description_names_both_receivers(self) -> None:
    text = TEXT_SQL.read_text(encoding="utf-8")

    self.assertIn("自身固定获得+3信仰值", text)
    self.assertIn("相邻学院获得+2科技值", text)
```

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```powershell
python -B -m unittest tools.far_east_magic_nap_society.tests.test_check_static.ChuuniStaticTests.test_gameplay_sql_executes_against_expansion2_schema tools.far_east_magic_nap_society.tests.test_check_static.ChuuniStaticTests.test_society_adjacency_description_names_both_receivers -v
```

Expected: FAIL because the building currently uses `DISTRICT_CHUUNI_SOCIETY` and `YIELD_GOLD`, and the description does not name both receivers.

- [ ] **Step 3: Implement the minimal building and text changes**

In the Magic Circle `SELECT`, use explicit values:

```sql
'DISTRICT_HOLY_SITE',
'YIELD_FAITH',
```

Keep `MustPurchase` at its schema default `0`. Replace the district description with this exact text:

```text
替代圣地。最终每回合提供2点大预言家点数。只要相邻至少一个学院，自身固定获得+3信仰值；相邻学院获得+2科技值，其他相邻专业区域也获得+2对应主要产出。
```

- [ ] **Step 4: Run the focused tests and verify GREEN**

Run the Step 2 command. Expected: both tests PASS.

- [ ] **Step 5: Commit Task 1**

```powershell
git add mods/ChuuniSociety/Data/DistrictBuilding.sql mods/ChuuniSociety/Text/Chuuni_zh_Hans_CN.sql tools/far_east_magic_nap_society/tests/test_check_static.py
git commit -m "fix(chuuni): restore magic circle availability"
```

---

### Task 2: Stage One Combat Modifier

**Files:**
- Create: `mods/ChuuniSociety/Data/StageCombat.sql`
- Modify: `mods/ChuuniSociety/ChuuniSociety.modinfo`
- Modify: `mods/ChuuniSociety/Scripts/ChuuniGameplay.lua`
- Modify: `tools/far_east_magic_nap_society/check_static.py`
- Modify: `tools/far_east_magic_nap_society/tests/test_check_static.py`

**Interfaces:**
- Consumes: `CHUUNI_STAGE`, `CHUUNI_STAGE_1_UNLOCKED`, and `UpdateChuuniStage(playerID)`.
- Produces: `CHUUNI_STAGE_1_COMBAT`, an unconditional player-units combat modifier attached once when the player's stage is at least one.

- [ ] **Step 1: Write failing stage-combat tests**

Add `STAGE_COMBAT_SQL = REPO_ROOT / "mods" / "ChuuniSociety" / "Data" / "StageCombat.sql"` and this contract:

```python
def test_stage_one_combat_contract(self) -> None:
    modinfo_text = MODINFO.read_text(encoding="utf-8")
    stage_text = STAGE_COMBAT_SQL.read_text(encoding="utf-8")
    lua_text = GAMEPLAY_LUA.read_text(encoding="utf-8")

    self.assertIn("Data/StageCombat.sql", modinfo_text)
    self.assertIn("CHUUNI_STAGE_1_COMBAT", stage_text)
    self.assertIn("MODIFIER_PLAYER_UNITS_ADJUST_COMBAT_STRENGTH", stage_text)
    self.assertIn("('CHUUNI_STAGE_1_COMBAT', 'Amount', 3)", stage_text)
    self.assertIn("CHUUNI_STAGE_1_COMBAT_ATTACHED", lua_text)
    self.assertIn(
        "player:AttachModifierByID(CHUUNI_STAGE_1_COMBAT_MODIFIER)",
        lua_text,
    )
```

After executing `DistrictBuilding.sql` in the Gathering Storm schema test, execute:

```python
connection.executescript(STAGE_COMBAT_SQL.read_text(encoding="utf-8"))
self.assertEqual(
    connection.execute(
        """
        SELECT m.ModifierType, a.Value
        FROM Modifiers AS m
        JOIN ModifierArguments AS a ON a.ModifierId = m.ModifierId
        WHERE m.ModifierId = 'CHUUNI_STAGE_1_COMBAT'
          AND a.Name = 'Amount'
        """
    ).fetchone(),
    ("MODIFIER_PLAYER_UNITS_ADJUST_COMBAT_STRENGTH", "3"),
)
```

- [ ] **Step 2: Run the stage test and verify RED**

Run:

```powershell
python -B -m unittest tools.far_east_magic_nap_society.tests.test_check_static.ChuuniStaticTests.test_stage_one_combat_contract -v
```

Expected: FAIL because `StageCombat.sql` and the Lua attachment contract are absent.

- [ ] **Step 3: Add the combat database definition**

Create `StageCombat.sql` with:

```sql
INSERT INTO Modifiers (ModifierId, ModifierType)
VALUES ('CHUUNI_STAGE_1_COMBAT', 'MODIFIER_PLAYER_UNITS_ADJUST_COMBAT_STRENGTH');

INSERT INTO ModifierArguments (ModifierId, Name, Value)
VALUES ('CHUUNI_STAGE_1_COMBAT', 'Amount', 3);
```

Register it in `.modinfo` as an `UpdateDatabase` action after `Core.sql`, and include it in `<Files>`.

- [ ] **Step 4: Attach the modifier once from progression Lua**

Add constants:

```lua
local CHUUNI_STAGE_1_COMBAT_ATTACHED = "CHUUNI_STAGE_1_COMBAT_ATTACHED"
local CHUUNI_STAGE_1_COMBAT_MODIFIER = "CHUUNI_STAGE_1_COMBAT"
```

Add and call this helper at the end of `UpdateChuuniStage` after the final stage value is stored:

```lua
local function EnsureStageModifiers(player, stage)
    if stage >= 1 and player:GetProperty(CHUUNI_STAGE_1_COMBAT_ATTACHED) ~= 1 then
        player:AttachModifierByID(CHUUNI_STAGE_1_COMBAT_MODIFIER)
        player:SetProperty(CHUUNI_STAGE_1_COMBAT_ATTACHED, 1)
    end
end
```

This call must run on every stage refresh so an existing save with stage one already unlocked receives the missing modifier once.

- [ ] **Step 5: Run focused tests and verify GREEN**

Run:

```powershell
python -B -m unittest tools.far_east_magic_nap_society.tests.test_check_static -v
```

Expected: all focused tests PASS and the schema execution test confirms `Amount=3`.

- [ ] **Step 6: Commit Task 2**

```powershell
git add mods/ChuuniSociety/Data/StageCombat.sql mods/ChuuniSociety/ChuuniSociety.modinfo mods/ChuuniSociety/Scripts/ChuuniGameplay.lua tools/far_east_magic_nap_society/check_static.py tools/far_east_magic_nap_society/tests/test_check_static.py
git commit -m "fix(chuuni): activate stage one combat bonus"
```

---

### Task 3: Full Verification and Deployment

**Files:**
- Verify: `mods/ChuuniSociety/**`
- Deploy: `C:/Users/82443/Documents/My Games/Sid Meier's Civilization VI/Mods/ChuuniSociety`

**Interfaces:**
- Consumes: the completed Task 1 and Task 2 commits.
- Produces: a deployed runtime package byte-identical to `mods/ChuuniSociety`.

- [ ] **Step 1: Run the unified regression suite**

```powershell
powershell -ExecutionPolicy Bypass -File tools/run_civ6_tool_tests.ps1
```

Expected: every unit test and both mod static validations PASS; cleanup removes generated cache directories.

- [ ] **Step 2: Verify repository hygiene**

```powershell
git diff --check
git status --short
```

Expected: no whitespace errors; only intended changes plus the untouched untracked `编辑.af` before commits.

- [ ] **Step 3: Deploy the mod**

```powershell
powershell -ExecutionPolicy Bypass -File tools/far_east_magic_nap_society/deploy.ps1
```

Expected: static checks pass and deployment reports the exact `ChuuniSociety` Mods path.

- [ ] **Step 4: Compare source and deployed hashes**

Run:

```powershell
$source = (Resolve-Path 'mods\ChuuniSociety').Path
$target = 'C:\Users\82443\Documents\My Games\Sid Meier''s Civilization VI\Mods\ChuuniSociety'
$sourceFiles = Get-ChildItem -LiteralPath $source -Recurse -File | ForEach-Object { [pscustomobject]@{ Relative = $_.FullName.Substring($source.Length).TrimStart('\'); Hash = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash } }
$targetFiles = Get-ChildItem -LiteralPath $target -Recurse -File | ForEach-Object { [pscustomobject]@{ Relative = $_.FullName.Substring($target.Length).TrimStart('\'); Hash = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash } }
$diff = Compare-Object $sourceFiles $targetFiles -Property Relative, Hash
"SOURCE_FILES=$($sourceFiles.Count)"
"DEPLOYED_FILES=$($targetFiles.Count)"
"DEPLOY_DIFFERENCES=$(@($diff).Count)"
```

Expected: identical file counts and `DEPLOY_DIFFERENCES=0`.

- [ ] **Step 5: Report the runtime verification boundary**

Report automated evidence separately from the remaining manual checks: Magic Circle appears in the Society production drawer and Faith purchase list, while a stage-one military unit's combat preview includes `+3`.
