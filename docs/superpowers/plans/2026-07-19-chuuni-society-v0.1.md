# Chuuni Society v0.1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Gathering Storm-only Civilization VI mod for the Far East Magic Nap Society with Rikka, the Society district, Magic Circle building, Chuuni Value progression, Chimera governor, staged combat and upgrade effects, Invisible Boundary improvement, and land-unit teleportation.

**Architecture:** Keep static game definitions in focused SQL files and use Gameplay Lua only for state that cannot be expressed reliably by database modifiers. Player and city Properties remain the stable state boundary for Lua transitions; staged combat uses SQL resource/religion requirements because Gathering Storm exposes no player-Property RequirementType. Every risky subsystem begins with a static or runtime spike and is promoted into the main implementation only after its acceptance checks pass.

**Tech Stack:** Civilization VI Gathering Storm SQL/XML/Lua, Python 3.11 `unittest`, PowerShell launchers, shared helpers under `tools/common`.

## Global Constraints

- Runtime mod root is `mods/ChuuniSociety/`; do not modify `mods/GraceAshcroft/`.
- Only Gathering Storm is supported: dependency id `4873eb62-8ccc-4574-b784-dda455e74e68`, game core `Expansion2`, FrontEnd domain `Players:Expansion2_Players`.
- All new gameplay identifiers use the `CHUUNI_` namespace or the exact types in the approved spec.
- Chuuni Value is a non-map strategic resource with stockpile cap 100 and never decreases.
- Stage 1 requires value 1 only. Stages 2, 3, and 4 require a founded religion and unlock sequentially at 20, 50, and 100.
- The Society district has a final Great Prophet output of 2 per turn; the Magic Circle retains the Shrine's 1 point.
- Teleport supports map-present land combat units, land civilians including religious units, and Great People. It rejects naval, air, trader, spy, and off-map special units.
- Chimera's dynamic faith, culture, and science must appear in the governed city's yield panel.
- Implement and validate mechanics before changing balance values.
- Rikka's first self-founded coastal city grants exactly 5 Chuuni Value, never 10.
- The first release carries the existing `.dep`, fallback-leader ArtDef and cooked BLP files. Their loading and in-game composition were visually verified on 2026-07-20; source changes still require rebuilding the affected art package.

## Completion Status

Only these states are used: `未开始`, `技术Spike`, `已实现未实机验证`, `已实机验证`.

| Deliverable | Status | Evidence or next gate |
| --- | --- | --- |
| Phase 1 civilization and leader skeleton | 已实机验证 | Civilization selection, loading scene and in-game leader presentation were visually confirmed. |
| Fallback art loading chain | 已实机验证 | `.dep`, fallback ArtDef and both BLP packages loaded in the supplied game screenshots. |
| Phase 2 Society district and Magic Circle | 已实现未实机验证 | Static/schema checks pass; recheck construction, Prophet points and adjacency in a fresh game. |
| Phase 3 Chuuni Value and sequential stages | 已实现未实机验证 | Runtime nil conversion was fixed; recheck save/load, coastal +5 and religion gates. |
| Phase 4 resource-threshold staged combat | 已实现未实机验证 | SQL spike is implemented; verify resource quantity arguments, religion gate, live refresh and 3/5/8 totals in game. |
| Rikka Schwarz Sechs | 未开始 | Starts only after staged combat is confirmed. |
| Chimera | 未开始 | Minimal Governor spike required first. |
| Fantasy Armament discounts | 未开始 | Native upgrade-cost modifier spike required first. |
| Invisible Boundary | 未开始 | Ocean placement spike required first. |
| Magic Circle teleport | 未开始 | Gameplay movement spike required first. |
| Faith purchasing and final content pass | 未开始 | Begins after preceding mechanics are stable. |

---

## File Structure

```text
mods/ChuuniSociety/
  ChuuniSociety.modinfo           Gathering Storm actions and file inventory
  Data/Config.sql                 FrontEnd player and PlayerItems rows
  Data/Core.sql                   civilization, leader, traits, resource and parameters
  Data/DistrictBuilding.sql       Society district, Magic Circle and adjacencies
  Data/StageCombat.sql            resource-gated staged combat modifiers
  Data/RikkaCombat.sql            Rikka defensive and stage-4 offensive modifiers
  Data/Chimera.sql                governor, governed-city yields, healing and production
  Data/Upgrade.sql                city-conditioned upgrade discounts
  Data/Improvement.sql            Invisible Boundary definition and yields
  Data/FaithPurchase.sql          faith-purchase modifiers and requirements
  Data/Colors.xml                 player colors
  Scripts/ChuuniGameplay.lua      Chuuni Value, stages, coastal trigger and Chimera state
  Scripts/ChuuniTeleport.lua      gameplay-side teleport validation and execution
  UI/ChuuniTeleportUI.lua         city-list teleport action and selection bridge
  Text/Chuuni_zh_Hans_CN.sql      Simplified Chinese localization
  Icons/ChuuniIcons.sql           custom cooked icon mappings with safe base-game fallbacks
tools/far_east_magic_nap_society/
  check_static.py                 mod-specific contract validator
  check_static.ps1               PowerShell compatibility launcher
  deploy.ps1                     validated deployment to the Civ6 Mods directory
  tests/test_check_static.py      static validator contract tests
```

---

### Task 1: Scaffold the Runtime Package and Static Contract

**Files:**
- Create: `mods/ChuuniSociety/ChuuniSociety.modinfo`
- Create: `mods/ChuuniSociety/Data/Config.sql`
- Create: `mods/ChuuniSociety/Data/Colors.xml`
- Create: `mods/ChuuniSociety/Text/Chuuni_zh_Hans_CN.sql`
- Create: `mods/ChuuniSociety/Icons/ChuuniIcons.sql`
- Create: `tools/far_east_magic_nap_society/check_static.py`
- Create: `tools/far_east_magic_nap_society/check_static.ps1`
- Create: `tools/far_east_magic_nap_society/tests/test_check_static.py`
- Modify: `tools/far_east_magic_nap_society/README.md`

**Interfaces:**
- Produces: `python tools/far_east_magic_nap_society/check_static.py` with exit code 0 on a complete contract and nonzero on missing files or stale rules.
- Produces: Gathering Storm-only FrontEnd entry for `CIVILIZATION_CHUUNI_SOCIETY` and `LEADER_RIKKA_TAKANASHI`.

- [ ] **Step 1: Write the failing static-checker tests**

```python
class ChuuniStaticTests(unittest.TestCase):
    def test_checker_runs_as_direct_script(self):
        result = subprocess.run(
            ["python", "tools/far_east_magic_nap_society/check_static.py"],
            cwd=REPO_ROOT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_modinfo_is_gathering_storm_only(self):
        text = (REPO_ROOT / "mods/ChuuniSociety/ChuuniSociety.modinfo").read_text(encoding="utf-8")
        self.assertIn('id="4873eb62-8ccc-4574-b784-dda455e74e68"', text)
        self.assertIn("<GameCoreInUse>Expansion2</GameCoreInUse>", text)
        self.assertNotIn("1B28771A-C749-434B-9053-D1380C553DE9", text)
```

- [ ] **Step 2: Run the focused tests and verify the expected failure**

Run: `python -m unittest tools.far_east_magic_nap_society.tests.test_check_static -v`

Expected: FAIL because the checker and runtime package do not exist.

- [ ] **Step 3: Create the minimum Gathering Storm manifest**

Use a new UUID and include this exact dependency and criterion:

```xml
<Dependencies>
  <Mod id="4873eb62-8ccc-4574-b784-dda455e74e68" title="Expansion: Gathering Storm" />
</Dependencies>
<ActionCriteria>
  <Criteria id="ChuuniExpansion2">
    <GameCoreInUse>Expansion2</GameCoreInUse>
  </Criteria>
</ActionCriteria>
```

Register only the files created by this task: `Config.sql`, localization, icons and colors in FrontEndActions. Each later task adds its new runtime file to `Files` and the appropriate InGameAction in the same commit; the manifest must never reference a file that does not yet exist.

- [ ] **Step 4: Create the FrontEnd player contract and icon fallbacks**

`Config.sql` must insert one `Players` row and PlayerItems rows using:

```sql
'CIVILIZATION_CHUUNI_SOCIETY',
'LEADER_RIKKA_TAKANASHI',
'Players:Expansion2_Players'
```

Map civilization, leader, district, building and resource icons to the verified Chuuni packages while retaining safe base-game fallbacks for types whose custom art is not ready. Do not reference nonexistent texture files.

- [ ] **Step 5: Implement the checker**

Reuse `require_files`, text-contract and runtime-layout primitives from `tools.common.civ6_static_checks`. Assert the Gathering Storm id, Expansion2 criterion, Expansion2 domain, registered file inventory, required LOC keys and absence of the Rise and Fall id.

- [ ] **Step 6: Run the tests and shared suite**

Run: `python -m unittest tools.far_east_magic_nap_society.tests.test_check_static -v`

Expected: PASS.

Run: `powershell -ExecutionPolicy Bypass -File tools/run_civ6_tool_tests.ps1`

Expected: all existing common and Grace tool tests remain PASS.

- [ ] **Step 7: Commit the isolated deliverable**

```powershell
git add mods/ChuuniSociety tools/far_east_magic_nap_society
git commit -m "feat(chuuni): add civilization and leader skeleton"
```

---

### Task 2: Define the Civilization, Society District, Magic Circle and Chuuni Resource

**Files:**
- Create: `mods/ChuuniSociety/Data/Core.sql`
- Create: `mods/ChuuniSociety/Data/DistrictBuilding.sql`
- Modify: `mods/ChuuniSociety/ChuuniSociety.modinfo`
- Modify: `mods/ChuuniSociety/Text/Chuuni_zh_Hans_CN.sql`
- Modify: `tools/far_east_magic_nap_society/check_static.py`
- Modify: `tools/far_east_magic_nap_society/tests/test_check_static.py`

**Interfaces:**
- Produces: `RESOURCE_CHUUNI_VALUE`, `DISTRICT_CHUUNI_SOCIETY`, `BUILDING_CLUB_MAGIC_CIRCLE`.
- Produces: `CHUUNI_STAGE_1_THRESHOLD=1`, `CHUUNI_STAGE_2_THRESHOLD=20`, `CHUUNI_STAGE_3_THRESHOLD=50`, `CHUUNI_STAGE_4_THRESHOLD=100` through `GlobalParameters`.

- [ ] **Step 1: Add failing SQL contract tests**

Assert exact strings for resource cap 100, `DistrictReplaces`, `BuildingReplaces`, final district Great Prophet points 2, Shrine Great Prophet points 1, and stage thresholds `1,20,50,100`.

- [ ] **Step 2: Run the focused test and confirm failure**

Run: `python -m unittest tools.far_east_magic_nap_society.tests.test_check_static -v`

Expected: FAIL with missing gameplay contracts.

- [ ] **Step 3: Implement `Core.sql`**

Insert exact Types, civilization/leader traits, trait attachments and resource rows. The resource contract is:

```sql
INSERT INTO Resources
  (ResourceType, Name, ResourceClassType, Frequency, RevealedEra)
VALUES
  ('RESOURCE_CHUUNI_VALUE', 'LOC_RESOURCE_CHUUNI_VALUE_NAME', 'RESOURCECLASS_STRATEGIC', 0, 0);

INSERT OR REPLACE INTO Resource_Consumption
  (ResourceType, Accumulate, PowerProvided, BaseExtractionRate, ImprovedExtractionRate, StockpileCap)
VALUES
  ('RESOURCE_CHUUNI_VALUE', 1, 0, 0, 0, 100);
```

- [ ] **Step 4: Implement district and building copies**

Copy complete compatible columns from `DISTRICT_HOLY_SITE` and `BUILDING_SHRINE`, then add:

```sql
INSERT INTO DistrictReplaces VALUES ('DISTRICT_CHUUNI_SOCIETY', 'DISTRICT_HOLY_SITE');
INSERT INTO BuildingReplaces VALUES ('BUILDING_CLUB_MAGIC_CIRCLE', 'BUILDING_SHRINE');
```

Replace the copied district Great Prophet record so the final value is 2. Keep the copied Shrine building Great Prophet value at 1. Set Magic Circle faith to 2, amenity to 1 and maintenance to 0 without breaking Temple prerequisites.

- [ ] **Step 5: Implement adjacencies**

Generate explicit outgoing adjacency rows for Campus/science, Theater/culture, Commercial Hub and Harbor/gold, Industrial Zone/production and Holy Site/faith. Implement “at least one adjacent Campus gives fixed +3 faith” with a requirement modifier; retain the city-Property scan as a documented fallback only if the original database has no reliable adjacent-district requirement.

- [ ] **Step 6: Run static tests**

Run: `python tools/far_east_magic_nap_society/check_static.py`

Expected: `[ChuuniSociety] static checks passed`.

- [ ] **Step 7: Commit**

```powershell
git add mods/ChuuniSociety/Data mods/ChuuniSociety/Text tools/far_east_magic_nap_society
git commit -m "feat(chuuni): add society district and magic circle"
```

---

### Task 3: Implement Chuuni Value, Coastal Trigger and Sequential Stages

**Files:**
- Create: `mods/ChuuniSociety/Scripts/ChuuniGameplay.lua`
- Modify: `mods/ChuuniSociety/ChuuniSociety.modinfo`
- Modify: `mods/ChuuniSociety/Data/Core.sql`
- Modify: `mods/ChuuniSociety/Text/Chuuni_zh_Hans_CN.sql`
- Modify: `tools/far_east_magic_nap_society/check_static.py`
- Modify: `tools/far_east_magic_nap_society/tests/test_check_static.py`

**Interfaces:**
- Produces: `GetChuuniValue(playerID) -> integer`, `ChangeChuuniValue(playerID, amount) -> integer`, `UpdateChuuniStage(playerID) -> integer`.
- Produces Properties: `CHUUNI_LAST_RESOURCE_TICK_TURN`, `CHUUNI_STAGE`, `CHUUNI_STAGE_1_UNLOCKED` through `_4_UNLOCKED`, `CHUUNI_FIRST_COASTAL_CITY_FOUNDED`.

- [ ] **Step 1: Add failing Lua contract tests**

Assert that the script contains exact threshold order, a founded-religion guard for stages 2–4, previous-stage guards, duplicate-turn protection, cap clamping, coastal reward 5, and `Events.PlayerTurnActivated` registration.

- [ ] **Step 2: Confirm test failure**

Run: `python -m unittest tools.far_east_magic_nap_society.tests.test_check_static -v`

Expected: FAIL because `ChuuniGameplay.lua` is absent.

- [ ] **Step 3: Implement resource helpers and per-turn production**

Use the Grace defensive API pattern. Count one value per Society district and one per Magic Circle. Clamp gains to `100 - currentValue`. Record the current game turn before applying the tick.

- [ ] **Step 4: Implement sequential stage transitions**

Use sequential `if` blocks in one call so a player who founds a religion at value 100 unlocks stages 2, 3 and 4 in order. Stage 1 has no religion test. Stages 2–4 require the founded-religion predicate and the previous `_UNLOCKED` Property. Emit each notification only when its Property changes from unset to 1.

- [ ] **Step 5: Implement the first self-founded coastal city trigger**

Reject captured cities. On the first verified self-founded coastal city, set `CHUUNI_FIRST_COASTAL_CITY_FOUNDED`, add exactly 5 Chuuni Value and enable the player-cities +2 amenities modifier through a player Property.

- [ ] **Step 6: Run static and Lua syntax checks**

Run: `python tools/far_east_magic_nap_society/check_static.py`

Expected: PASS.

If a Lua interpreter is available, run: `lua -e "assert(loadfile('mods/ChuuniSociety/Scripts/ChuuniGameplay.lua'))"`.

Expected: exit 0. If no interpreter exists, record `Lua syntax not locally executable` and rely on Civ6 `Lua.log` in the runtime spike.

- [ ] **Step 7: Perform Spike A in Gathering Storm**

Set temporary thresholds `1,3,5,10`, deploy, start a Gathering Storm game, build the district and building, save/reload, and capture `Database.log`, `Modding.log` and `Lua.log`. Verify cap 100, no duplicate tick, coastal +5, and no stage 2–4 before religion.

- [ ] **Step 8: Restore production thresholds and commit**

```powershell
git add mods/ChuuniSociety tools/far_east_magic_nap_society
git commit -m "feat(chuuni): add chuuni value progression"
```

---

### Task 4A: Add Resource-Gated Staged Combat

**Files:**
- Modify: `mods/ChuuniSociety/Data/StageCombat.sql`
- Modify: `mods/ChuuniSociety/ChuuniSociety.modinfo`
- Modify: `mods/ChuuniSociety/Scripts/ChuuniGameplay.lua`
- Modify: `mods/ChuuniSociety/Text/Chuuni_zh_Hans_CN.sql`
- Modify: `tools/far_east_magic_nap_society/check_static.py`
- Modify: `tools/far_east_magic_nap_society/tests/test_check_static.py`
- Modify: `docs/superpowers/plans/2026-07-19-chuuni-society-v0.1.md`

**Interfaces:**
- Consumes: `RESOURCE_CHUUNI_VALUE` stockpile and the founded-religion state from Task 3.
- Produces: military combat totals 3/5/8/8 and religious combat totals 3/5/8/8 without Lua modifier attachment.

- [ ] **Step 1: Add failing assertions for three static trait modifiers with `3,2,3` amounts, resource thresholds `1,20,50`, founded-religion requirements on the latter two, and no stage-combat `AttachModifierByID` in Lua.**
- [ ] **Step 2: Run the focused test and confirm that the current single Lua-attached `+3` implementation fails the new contract.**
- [ ] **Step 3: Implement the three modifiers with `MODIFIER_PLAYER_UNITS_ADJUST_COMBAT_STRENGTH`. Gate them through `OwnerRequirementSetId` sets built from `REQUIREMENT_PLAYER_HAS_RESOURCE_OWNED`; pass `ResourceType=RESOURCE_CHUUNI_VALUE` and `Amount=1/20/50`, and add `REQUIREMENT_PLAYER_IS_RELIGION_FOUNDER` to the 20 and 50 sets.**
- [ ] **Step 4: Remove `CHUUNI_STAGE_1_COMBAT_ATTACHED`, `CHUUNI_STAGE_1_COMBAT_MODIFIER` and `EnsureStageModifiers` from Lua. Keep `CHUUNI_STAGE` and all four `_UNLOCKED` Properties.**
- [ ] **Step 5: Run the focused unit tests, Expansion2 schema execution and Chuuni static checker. Deploy only ChuuniSociety.**
- [ ] **Step 6: In Gathering Storm, inspect military and theological combat previews at values `1,20,50,100`, test live threshold refresh and the religion gate. Expected totals are `3,5,8,8`, never `16`. Until this passes, keep the status as `已实现未实机验证`.**
- [ ] **Step 7: Commit with `git commit -m "feat(chuuni): add resource-gated staged combat"`.**

### Task 4B: Add Rikka Schwarz Sechs

**Files:**
- Create: `mods/ChuuniSociety/Data/RikkaCombat.sql`
- Modify: `mods/ChuuniSociety/ChuuniSociety.modinfo`
- Modify: `mods/ChuuniSociety/Text/Chuuni_zh_Hans_CN.sql`
- Modify: `tools/far_east_magic_nap_society/check_static.py`
- Modify: `tools/far_east_magic_nap_society/tests/test_check_static.py`

**Interfaces:**
- Consumes: the verified stage-4 resource/religion gate from Task 4A.
- Produces: military-only defense +5 and stage-4 military-only attack +5; religious units receive neither modifier.

- [ ] **Step 1: Add failing contracts for distinct defense and attack modifiers, military-unit and combat-role requirements, and the stage-4 gate.**
- [ ] **Step 2: Implement the leader-trait modifiers and their combat preview strings without changing staged fantasy combat.**
- [ ] **Step 3: Run focused checks, deploy ChuuniSociety and verify military defense, stage-4 military attack and religious exclusion in game.**
- [ ] **Step 4: Commit with `git commit -m "feat(chuuni): add Schwarz Sechs combat ability"`.**

---

### Task 5: Spike and Implement Chimera

**Files:**
- Create: `mods/ChuuniSociety/Data/Chimera.sql`
- Modify: `mods/ChuuniSociety/ChuuniSociety.modinfo`
- Modify: `mods/ChuuniSociety/Scripts/ChuuniGameplay.lua`
- Modify: `mods/ChuuniSociety/Text/Chuuni_zh_Hans_CN.sql`
- Modify: `mods/ChuuniSociety/Icons/ChuuniIcons.sql`
- Modify: `tools/far_east_magic_nap_society/check_static.py`

**Interfaces:**
- Produces: `GOVERNOR_CHIMERA`, `CHUUNI_CHIMERA_CITY_ID`, `CHUUNI_CHIMERA_YIELD_STEP`.
- Produces: governed-city production, stationed healing, combat, start-turn movement/sight and panel-visible dynamic yields.

- [ ] **Step 1: Add checker assertions for the Governor row, one-turn establishment, no Rise and Fall dependency, Property names and ten yield steps.**
- [ ] **Step 2: Create a minimal Governor row and verify in-game that it appears, can be granted without consuming a title and survives save/load. Stop this task if any assertion fails.**
- [ ] **Step 3: Implement stage effects through player stage Properties plus “city governed by Chimera” requirements; do not use automatic GovernorPromotion grants.**
- [ ] **Step 4: Implement +100% Society/Magic Circle production and normal stationed/rest healing +20. Do not affect pillage, promotion, upgrade or instant-heal sources.**
- [ ] **Step 5: Implement governed-territory combat +5 at stage 2 and start-turn-only movement +1/sight +1 at stage 3 with per-turn unit Properties preventing re-entry stacking.**
- [ ] **Step 6: Implement ten incremental city-yield modifiers. Stage 1 exposes faith, stage 2 culture and stage 3 science; each active threshold 10–100 contributes +1 to the governed city panel.**
- [ ] **Step 7: Implement stage-4 +5 faith/culture/science for every Magic Circle city while keeping previous governed-city effects local to Chimera.**
- [ ] **Step 8: Validate assignment changes, city-panel values and save/load, then commit with `git commit -m "feat(chuuni): add Chimera governor"`.**

---

### Task 6: Spike and Implement Fantasy Armament Upgrade Discounts

**Files:**
- Create: `mods/ChuuniSociety/Data/Upgrade.sql`
- Modify: `mods/ChuuniSociety/ChuuniSociety.modinfo`
- Modify: `mods/ChuuniSociety/Scripts/ChuuniGameplay.lua` only if a unit Property bridge is required
- Modify: `tools/far_east_magic_nap_society/check_static.py`

**Interfaces:**
- Produces: Magic Circle city territory discount tiers `25/50/100` gold and `50/50/100` strategic resources.

- [ ] **Step 1: Extract the exact Professional Army and Force Modernization modifiers from installed Expansion2 data and add their identifiers to a failing checker fixture.**
- [ ] **Step 2: Build a one-tier Spike C modifier and verify the upgrade UI price equals the actual deduction inside and outside a Magic Circle city.**
- [ ] **Step 3: If city-building subject requirements work, implement all tiers in SQL. If they do not, synchronize a unit Property on selection/movement and keep cost calculation in original modifiers.**
- [ ] **Step 4: Verify interaction with Professional Army/Force Modernization and reject Lua post-upgrade refund logic.**
- [ ] **Step 5: Commit with `git commit -m "feat(chuuni): add fantasy armament upgrade discounts"`.**

---

### Task 7: Implement Invisible Boundary

**Files:**
- Create: `mods/ChuuniSociety/Data/Improvement.sql`
- Modify: `mods/ChuuniSociety/ChuuniSociety.modinfo`
- Modify: `mods/ChuuniSociety/Scripts/ChuuniGameplay.lua` only for restrictions unsupported by SQL
- Modify: `mods/ChuuniSociety/Text/Chuuni_zh_Hans_CN.sql`
- Modify: `tools/far_east_magic_nap_society/check_static.py`

**Interfaces:**
- Produces: `IMPROVEMENT_INVISIBLE_BOUNDARY`, Cartography unlock, ocean-only placement, one per city, no resources, no adjacency to another Boundary, no pillage, coast/ocean adjacency yields.

- [ ] **Step 1: Add failing static assertions for terrain, technology, yields and restrictions.**
- [ ] **Step 2: Query installed schema for `OnePerCity`, pillage and placement columns before writing the row.**
- [ ] **Step 3: Implement every supported restriction in SQL and use Lua placement validation only for unsupported one-per-city or non-adjacency rules.**
- [ ] **Step 4: Verify Builder ocean access after Cartography and test ownership transfer, resource plots, adjacent Boundary rejection and pillage immunity.**
- [ ] **Step 5: Commit with `git commit -m "feat(chuuni): add invisible boundary improvement"`.**

---

### Task 8: Spike and Implement Magic Circle Teleport

**Files:**
- Create: `mods/ChuuniSociety/Scripts/ChuuniTeleport.lua`
- Create: `mods/ChuuniSociety/UI/ChuuniTeleportUI.lua`
- Modify: `mods/ChuuniSociety/ChuuniSociety.modinfo`
- Modify: `mods/ChuuniSociety/Text/Chuuni_zh_Hans_CN.sql`
- Modify: `tools/far_east_magic_nap_society/check_static.py`

**Interfaces:**
- Produces: `CanChuuniTeleport(playerID, unitID) -> boolean, reason`, `GetValidMagicCircleDestinations(playerID, unitID) -> city list`, `ExecuteChuuniTeleport(playerID, unitID, cityID) -> boolean, reason`.

- [ ] **Step 1: Add failing checker assertions for both scripts, UI registration, unit whitelist, exclusion list, move exhaustion and per-turn Property.**
- [ ] **Step 2: Implement `TeleportUnitToFirstValidMagicCircle` as Spike D without custom UI. Validate land combat, civilian, religious and Great Person units; reject naval, air, traders and spies.**
- [ ] **Step 3: Validate destination ownership, Magic Circle presence, Society plot occupancy and unit compatibility before moving.**
- [ ] **Step 4: After a successful move, set moves remaining to zero and store the current turn on the unit so the same unit cannot teleport twice.**
- [ ] **Step 5: Once gameplay relocation is proven, add a city-list UI add-in using `LuaEvents` to request the gameplay operation. Do not let UI code mutate gameplay state directly.**
- [ ] **Step 6: Test AI safety, save/load, occupied destinations and every allowed/rejected unit category.**
- [ ] **Step 7: Commit with `git commit -m "feat(chuuni): add magic-circle teleport"`.**

---

### Task 9: Implement Faith Purchases

**Files:**
- Create: `mods/ChuuniSociety/Data/FaithPurchase.sql`
- Modify: `mods/ChuuniSociety/ChuuniSociety.modinfo`
- Modify: `mods/ChuuniSociety/Text/Chuuni_zh_Hans_CN.sql`
- Modify: `tools/far_east_magic_nap_society/check_static.py`

**Interfaces:**
- Produces: Society district cities can faith-buy Magic Circle; Magic Circle cities can faith-buy Campus buildings, Temple and worship buildings.

- [ ] **Step 1: Extract the Jesuit Education ModifierType and arguments from installed Expansion2 data.**
- [ ] **Step 2: Add failing assertions that Magic Circle purchase requires only the Society district and does not require the Magic Circle itself.**
- [ ] **Step 3: Implement separate requirement sets for buying the Magic Circle and for buying downstream Campus/Holy Site buildings.**
- [ ] **Step 4: Verify the production panel has no circular prerequisite and actual faith deductions match displayed costs.**
- [ ] **Step 5: Commit with `git commit -m "feat(chuuni): add faith building purchases"`.**

---

### Task 10: Final Static, Runtime and Deployment Gate

**Files:**
- Create: `tools/far_east_magic_nap_society/deploy.ps1`
- Modify: `tools/far_east_magic_nap_society/check_static.py`
- Modify: `tools/far_east_magic_nap_society/README.md`
- Modify: `mods/ChuuniSociety/Text/Chuuni_zh_Hans_CN.sql`

**Interfaces:**
- Produces: validated deployment command and a complete v0.1 runtime package.

- [ ] **Step 1: Make the checker enforce all files, LOC keys, unique ids, resource cap, sequential stages, final Great Prophet values, Gathering Storm-only manifest, combat differences, Chimera +5, stage-4 `5/5/5`, teleport whitelist and faith-purchase non-cycle.**
- [ ] **Step 2: Run `powershell -ExecutionPolicy Bypass -File tools/run_civ6_tool_tests.ps1`; expected all tests PASS.**
- [ ] **Step 3: Run `python tools/far_east_magic_nap_society/check_static.py`; expected exit 0 and a single success summary.**
- [ ] **Step 4: Deploy to a temporary validation destination first and compare the deployed inventory with the `.modinfo` Files list.**
- [ ] **Step 5: Run the complete Gathering Storm manual matrix and inspect fresh `Database.log`, `Modding.log` and `Lua.log` for Chuuni errors.**
- [ ] **Step 6: Record actual balance observations without changing values during the mechanism-validation pass.**
- [ ] **Step 7: Commit with `git commit -m "test(chuuni): validate v0.1 gameplay package"`.**

---

## Execution Order and Stop Conditions

1. Execute Tasks 1–3 first and stop for a runtime review after Spike A.
2. Execute Task 4 only after stages are stable across save/load.
3. Execute Tasks 5, 6 and 8 only when their individual Spikes pass; use the approved degradation path instead of silently changing mechanics.
4. Execute Tasks 7 and 9 after their original database contracts are confirmed locally.
5. Execute Task 10 only after every earlier checker and runtime acceptance test passes.

Any failed Spike is a review checkpoint. Record the exact database/API limitation and obtain approval before selecting a degradation path from the design specification.
