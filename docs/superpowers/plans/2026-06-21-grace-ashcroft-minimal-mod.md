# Grace Ashcroft Minimal Civ VI Mod Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a minimal Civilization VI mod package that adds the Elpis Protocol civilization, Grace Ashcroft leader, Rhodes Hill Sanatorium, Infected Blood project loop, and local static validation.

**Architecture:** The mod lives under `mods/GraceAshcroft/` and follows Civ VI's `.modinfo` + SQL/XML + Gameplay Lua structure. Static validation is handled by a PowerShell script so we can verify package structure and key identifiers without requiring a local Civ VI runtime in this session.

**Tech Stack:** Civilization VI mod XML/SQL/Lua, PowerShell static checks, Markdown docs.

---

### Task 1: Static Validation Script

**Files:**
- Create: `tools/check_grace_mod_static.ps1`

- [ ] **Step 1: Write the failing validation script**

Create a PowerShell script that expects the following files and identifiers:

```powershell
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$modRoot = Join-Path $root "mods\GraceAshcroft"

function Assert-FileExists {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Missing required file: $Path"
    }
}

function Assert-Contains {
    param(
        [string]$Path,
        [string]$Needle
    )
    $content = Get-Content -Raw -LiteralPath $Path
    if ($content -notlike "*$Needle*") {
        throw "Expected '$Needle' in $Path"
    }
}

$modinfo = Join-Path $modRoot "GraceAshcroft.modinfo"
$config = Join-Path $modRoot "Data\Config.sql"
$gameplay = Join-Path $modRoot "Data\Gameplay.sql"
$text = Join-Path $modRoot "Text\GraceAshcroft_zh_Hans_CN.sql"
$lua = Join-Path $modRoot "Scripts\GraceGameplay.lua"

@($modinfo, $config, $gameplay, $text, $lua) | ForEach-Object {
    Assert-FileExists $_
}

Assert-Contains $modinfo "<Mod id="
Assert-Contains $modinfo "AddGameplayScripts"
Assert-Contains $modinfo "Data/Config.sql"
Assert-Contains $modinfo "Data/Gameplay.sql"
Assert-Contains $modinfo "Text/GraceAshcroft_zh_Hans_CN.sql"
Assert-Contains $modinfo "Scripts/GraceGameplay.lua"

Assert-Contains $config "CIVILIZATION_ELPIS_PROTOCOL"
Assert-Contains $config "LEADER_GRACE_ASHCROFT"
Assert-Contains $config "Players:Expansion2_Players"

Assert-Contains $gameplay "BUILDING_RHODES_HILL_SANATORIUM"
Assert-Contains $gameplay "PROJECT_GRACE_HEMOLYTIC_AGENT"
Assert-Contains $gameplay "PROJECT_GRACE_STABILIZER"
Assert-Contains $gameplay "PROJECT_GRACE_STEROID"
Assert-Contains $gameplay "PROJECT_GRACE_BLOOD_SAMPLE_ANALYSIS"
Assert-Contains $gameplay "PROJECT_GRACE_ABNORMAL_PATHOLOGY"
Assert-Contains $gameplay "PROJECT_GRACE_CONTAINMENT_REVIEW"
Assert-Contains $gameplay "GRACE_BLOOD_PER_BARBARIAN_KILL"

Assert-Contains $text "LOC_CIVILIZATION_ELPIS_PROTOCOL_NAME"
Assert-Contains $text "LOC_LEADER_GRACE_ASHCROFT_NAME"
Assert-Contains $text "LOC_BUILDING_RHODES_HILL_SANATORIUM_NAME"

Assert-Contains $lua "INFECTED_BLOOD"
Assert-Contains $lua "Events.CityProjectCompleted.Add"
Assert-Contains $lua "PROJECT_GRACE_BLOOD_SAMPLE_ANALYSIS"
Assert-Contains $lua "TriggerBoost"

Write-Host "Grace Ashcroft mod static validation passed."
```

- [ ] **Step 2: Run validation to verify it fails**

Run: `powershell -ExecutionPolicy Bypass -File tools\check_grace_mod_static.ps1`

Expected: FAIL with `Missing required file` because the mod package has not been created.

### Task 2: Mod Package Manifest

**Files:**
- Create: `mods/GraceAshcroft/GraceAshcroft.modinfo`

- [ ] **Step 1: Create the mod manifest**

Create `.modinfo` with:

```xml
<?xml version="1.0" encoding="utf-8"?>
<Mod id="6b8f93c1-7c19-4f06-a7c5-9ef0f1c7c911" version="1">
  <Properties>
    <Name>Grace Ashcroft - Elpis Protocol</Name>
    <Description>Adds Grace Ashcroft and the Elpis Protocol civilization.</Description>
    <Teaser>Clear barbarian threats, collect Infected Blood, and convert samples into combat and science.</Teaser>
    <Authors>Codex</Authors>
    <CompatibleVersions>1.2,2.0</CompatibleVersions>
  </Properties>
  <Dependencies>
    <Mod id="4873eb62-8ccc-4574-b784-dda455e74e68" title="Expansion: Gathering Storm" />
    <Mod id="1B28771A-C749-434B-9053-D1380C553DE9" title="Expansion: Rise and Fall" />
  </Dependencies>
  <FrontEndActions>
    <UpdateDatabase id="GraceConfig">
      <File>Data/Config.sql</File>
    </UpdateDatabase>
    <UpdateText id="GraceTextFrontEnd">
      <File>Text/GraceAshcroft_zh_Hans_CN.sql</File>
    </UpdateText>
  </FrontEndActions>
  <InGameActions>
    <UpdateDatabase id="GraceGameplay">
      <Properties>
        <LoadOrder>1000</LoadOrder>
      </Properties>
      <File>Data/Gameplay.sql</File>
    </UpdateDatabase>
    <UpdateText id="GraceTextInGame">
      <File>Text/GraceAshcroft_zh_Hans_CN.sql</File>
    </UpdateText>
    <AddGameplayScripts id="GraceGameplayScripts">
      <Properties>
        <LoadOrder>1000</LoadOrder>
      </Properties>
      <File>Scripts/GraceGameplay.lua</File>
    </AddGameplayScripts>
  </InGameActions>
  <Files>
    <File>Data/Config.sql</File>
    <File>Data/Gameplay.sql</File>
    <File>Text/GraceAshcroft_zh_Hans_CN.sql</File>
    <File>Scripts/GraceGameplay.lua</File>
  </Files>
</Mod>
```

### Task 3: Front-End Civilization and Leader Data

**Files:**
- Create: `mods/GraceAshcroft/Data/Config.sql`

- [ ] **Step 1: Define player selection data**

Create config SQL with `Players` and `PlayerItems` rows for `CIVILIZATION_ELPIS_PROTOCOL` and `LEADER_GRACE_ASHCROFT`, using fallback built-in icons:

```sql
INSERT INTO Players
    (CivilizationAbilityDescription, CivilizationAbilityIcon, CivilizationAbilityName, CivilizationIcon, CivilizationName, CivilizationType, LeaderAbilityDescription, LeaderAbilityIcon, LeaderAbilityName, LeaderIcon, LeaderName, LeaderType, Portrait, PortraitBackground, Domain)
VALUES
    ('LOC_TRAIT_CIVILIZATION_ELPIS_PROTOCOL_DESCRIPTION', 'ICON_CIVILIZATION_UNKNOWN', 'LOC_TRAIT_CIVILIZATION_ELPIS_PROTOCOL_NAME', 'ICON_CIVILIZATION_UNKNOWN', 'LOC_CIVILIZATION_ELPIS_PROTOCOL_NAME', 'CIVILIZATION_ELPIS_PROTOCOL', 'LOC_TRAIT_LEADER_GRACE_ASHCROFT_DESCRIPTION', 'ICON_LEADER_DEFAULT', 'LOC_TRAIT_LEADER_GRACE_ASHCROFT_NAME', 'ICON_LEADER_DEFAULT', 'LOC_LEADER_GRACE_ASHCROFT_NAME', 'LEADER_GRACE_ASHCROFT', 'LEADER_DEFAULT_NEUTRAL', 'LEADER_DEFAULT_BACKGROUND', 'Players:Expansion2_Players');

INSERT INTO PlayerItems
    (Domain, CivilizationType, LeaderType, Type, Icon, Name, Description, SortIndex)
VALUES
    ('Players:Expansion2_Players', 'CIVILIZATION_ELPIS_PROTOCOL', 'LEADER_GRACE_ASHCROFT', 'BUILDING_RHODES_HILL_SANATORIUM', 'ICON_BUILDING_RESEARCH_LAB', 'LOC_BUILDING_RHODES_HILL_SANATORIUM_NAME', 'LOC_BUILDING_RHODES_HILL_SANATORIUM_DESCRIPTION', 10);
```

### Task 4: Gameplay Database

**Files:**
- Create: `mods/GraceAshcroft/Data/Gameplay.sql`

- [ ] **Step 1: Define civilization, leader, building, projects, modifiers, and parameters**

Create gameplay SQL that includes:

```sql
INSERT INTO Types (Type, Kind) VALUES
    ('CIVILIZATION_ELPIS_PROTOCOL', 'KIND_CIVILIZATION'),
    ('LEADER_GRACE_ASHCROFT', 'KIND_LEADER'),
    ('TRAIT_CIVILIZATION_ELPIS_PROTOCOL', 'KIND_TRAIT'),
    ('TRAIT_LEADER_GRACE_ASHCROFT', 'KIND_TRAIT'),
    ('BUILDING_RHODES_HILL_SANATORIUM', 'KIND_BUILDING'),
    ('PROJECT_GRACE_HEMOLYTIC_AGENT', 'KIND_PROJECT'),
    ('PROJECT_GRACE_STABILIZER', 'KIND_PROJECT'),
    ('PROJECT_GRACE_STEROID', 'KIND_PROJECT'),
    ('PROJECT_GRACE_BLOOD_SAMPLE_ANALYSIS', 'KIND_PROJECT'),
    ('PROJECT_GRACE_ABNORMAL_PATHOLOGY', 'KIND_PROJECT'),
    ('PROJECT_GRACE_CONTAINMENT_REVIEW', 'KIND_PROJECT');

INSERT INTO Civilizations (CivilizationType, Name, Description, Adjective, StartingCivilizationLevelType, RandomCityNameDepth, Ethnicity)
VALUES ('CIVILIZATION_ELPIS_PROTOCOL', 'LOC_CIVILIZATION_ELPIS_PROTOCOL_NAME', 'LOC_CIVILIZATION_ELPIS_PROTOCOL_DESCRIPTION', 'LOC_CIVILIZATION_ELPIS_PROTOCOL_ADJECTIVE', 'CIVILIZATION_LEVEL_FULL_CIV', 10, 'ETHNICITY_EURO');

INSERT INTO Leaders (LeaderType, Name, InheritFrom, Sex, SceneLayers)
VALUES ('LEADER_GRACE_ASHCROFT', 'LOC_LEADER_GRACE_ASHCROFT_NAME', 'LEADER_DEFAULT', 'Female', 4);

INSERT INTO CivilizationLeaders (CivilizationType, LeaderType, CapitalName)
VALUES ('CIVILIZATION_ELPIS_PROTOCOL', 'LEADER_GRACE_ASHCROFT', 'LOC_CITY_NAME_RHODES_HILL');

INSERT INTO Traits (TraitType, Name, Description) VALUES
    ('TRAIT_CIVILIZATION_ELPIS_PROTOCOL', 'LOC_TRAIT_CIVILIZATION_ELPIS_PROTOCOL_NAME', 'LOC_TRAIT_CIVILIZATION_ELPIS_PROTOCOL_DESCRIPTION'),
    ('TRAIT_LEADER_GRACE_ASHCROFT', 'LOC_TRAIT_LEADER_GRACE_ASHCROFT_NAME', 'LOC_TRAIT_LEADER_GRACE_ASHCROFT_DESCRIPTION');

INSERT INTO CivilizationTraits (CivilizationType, TraitType)
VALUES ('CIVILIZATION_ELPIS_PROTOCOL', 'TRAIT_CIVILIZATION_ELPIS_PROTOCOL');

INSERT INTO LeaderTraits (LeaderType, TraitType)
VALUES ('LEADER_GRACE_ASHCROFT', 'TRAIT_LEADER_GRACE_ASHCROFT');

INSERT INTO CityNames (CivilizationType, CityName) VALUES
    ('CIVILIZATION_ELPIS_PROTOCOL', 'LOC_CITY_NAME_RHODES_HILL'),
    ('CIVILIZATION_ELPIS_PROTOCOL', 'LOC_CITY_NAME_ELPIS_SITE'),
    ('CIVILIZATION_ELPIS_PROTOCOL', 'LOC_CITY_NAME_CONTAINMENT_ZONE');

INSERT INTO Buildings
    (BuildingType, Name, Description, PrereqTech, PrereqDistrict, PurchaseYield, Cost, AdvisorType, Maintenance)
SELECT
    'BUILDING_RHODES_HILL_SANATORIUM',
    'LOC_BUILDING_RHODES_HILL_SANATORIUM_NAME',
    'LOC_BUILDING_RHODES_HILL_SANATORIUM_DESCRIPTION',
    'TECH_WRITING',
    'DISTRICT_CAMPUS',
    'YIELD_GOLD',
    120,
    'ADVISOR_TECHNOLOGY',
    1;

INSERT INTO Building_YieldChanges (BuildingType, YieldType, YieldChange)
VALUES ('BUILDING_RHODES_HILL_SANATORIUM', 'YIELD_SCIENCE', 2);

INSERT INTO Projects (ProjectType, Name, ShortName, Description, Cost, CostProgressionModel, PrereqDistrict, AdvisorType) VALUES
    ('PROJECT_GRACE_HEMOLYTIC_AGENT', 'LOC_PROJECT_GRACE_HEMOLYTIC_AGENT_NAME', 'LOC_PROJECT_GRACE_HEMOLYTIC_AGENT_SHORT_NAME', 'LOC_PROJECT_GRACE_HEMOLYTIC_AGENT_DESCRIPTION', 10, 'NO_COST_PROGRESSION', 'DISTRICT_CAMPUS', 'ADVISOR_CONQUEST'),
    ('PROJECT_GRACE_STABILIZER', 'LOC_PROJECT_GRACE_STABILIZER_NAME', 'LOC_PROJECT_GRACE_STABILIZER_SHORT_NAME', 'LOC_PROJECT_GRACE_STABILIZER_DESCRIPTION', 10, 'NO_COST_PROGRESSION', 'DISTRICT_CAMPUS', 'ADVISOR_CONQUEST'),
    ('PROJECT_GRACE_STEROID', 'LOC_PROJECT_GRACE_STEROID_NAME', 'LOC_PROJECT_GRACE_STEROID_SHORT_NAME', 'LOC_PROJECT_GRACE_STEROID_DESCRIPTION', 10, 'NO_COST_PROGRESSION', 'DISTRICT_CAMPUS', 'ADVISOR_CONQUEST'),
    ('PROJECT_GRACE_BLOOD_SAMPLE_ANALYSIS', 'LOC_PROJECT_GRACE_BLOOD_SAMPLE_ANALYSIS_NAME', 'LOC_PROJECT_GRACE_BLOOD_SAMPLE_ANALYSIS_SHORT_NAME', 'LOC_PROJECT_GRACE_BLOOD_SAMPLE_ANALYSIS_DESCRIPTION', 10, 'NO_COST_PROGRESSION', 'DISTRICT_CAMPUS', 'ADVISOR_TECHNOLOGY'),
    ('PROJECT_GRACE_ABNORMAL_PATHOLOGY', 'LOC_PROJECT_GRACE_ABNORMAL_PATHOLOGY_NAME', 'LOC_PROJECT_GRACE_ABNORMAL_PATHOLOGY_SHORT_NAME', 'LOC_PROJECT_GRACE_ABNORMAL_PATHOLOGY_DESCRIPTION', 10, 'NO_COST_PROGRESSION', 'DISTRICT_CAMPUS', 'ADVISOR_TECHNOLOGY'),
    ('PROJECT_GRACE_CONTAINMENT_REVIEW', 'LOC_PROJECT_GRACE_CONTAINMENT_REVIEW_NAME', 'LOC_PROJECT_GRACE_CONTAINMENT_REVIEW_SHORT_NAME', 'LOC_PROJECT_GRACE_CONTAINMENT_REVIEW_DESCRIPTION', 10, 'NO_COST_PROGRESSION', 'DISTRICT_CAMPUS', 'ADVISOR_TECHNOLOGY');

INSERT OR REPLACE INTO GlobalParameters (Name, Value) VALUES
    ('GRACE_BLOOD_PER_BARBARIAN_KILL', '1'),
    ('GRACE_PROJECT_BLOOD_COST', '3'),
    ('GRACE_MAX_HEMOLYTIC_LEVEL', '3'),
    ('GRACE_MAX_STABILIZER_LEVEL', '3'),
    ('GRACE_MAX_STEROID_LEVEL', '3'),
    ('GRACE_HEMOLYTIC_COMBAT_VS_BARBARIANS', '5'),
    ('GRACE_STABILIZER_COMBAT', '5'),
    ('GRACE_STEROID_DEFENSE', '5'),
    ('GRACE_STEROID_HEALING', '5'),
    ('GRACE_EUREKA_FALLBACK_SCIENCE', '100'),
    ('GRACE_EUREKA_FALLBACK_SCIENCE_PER_ERA', '50'),
    ('GRACE_GREAT_SCIENTIST_POINTS', '30'),
    ('GRACE_GREAT_SCIENTIST_POINTS_PER_ERA', '10');
```

### Task 5: Chinese Text

**Files:**
- Create: `mods/GraceAshcroft/Text/GraceAshcroft_zh_Hans_CN.sql`

- [ ] **Step 1: Add localized text**

Create Chinese localization for civilization, leader, building, projects, notifications, and city names.

### Task 6: Gameplay Lua

**Files:**
- Create: `mods/GraceAshcroft/Scripts/GraceGameplay.lua`

- [ ] **Step 1: Implement minimal gameplay script**

Create Lua that:

- Stores `INFECTED_BLOOD` on the player.
- Reads `GlobalParameters`.
- Handles barbarian kill events when available.
- Handles project completion through `Events.CityProjectCompleted.Add`.
- Consumes blood before rewards.
- Tracks enhancer levels with player properties.
- Attempts `PlayerTechs:TriggerBoost` for the eureka project.
- Falls back to science progress if no boost is available.
- Grants Great Scientist points where API support is available.
- Prints clear log messages for testing.

### Task 7: Verify Static Package

**Files:**
- Test: `tools/check_grace_mod_static.ps1`

- [ ] **Step 1: Run validation**

Run: `powershell -ExecutionPolicy Bypass -File tools\check_grace_mod_static.ps1`

Expected: PASS with `Grace Ashcroft mod static validation passed.`

- [ ] **Step 2: Review git diff**

Run: `git status --short`

Expected: `mods/GraceAshcroft/`, `tools/check_grace_mod_static.ps1`, and docs changes are visible.
