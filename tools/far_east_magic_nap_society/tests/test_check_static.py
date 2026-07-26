"""Tests for the Far East Magic Nap Society static validator."""

from __future__ import annotations

import subprocess
import sqlite3
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
MODINFO = REPO_ROOT / "mods" / "ChuuniSociety" / "ChuuniSociety.modinfo"
CORE_SQL = REPO_ROOT / "mods" / "ChuuniSociety" / "Data" / "Core.sql"
DISTRICT_BUILDING_SQL = (
    REPO_ROOT / "mods" / "ChuuniSociety" / "Data" / "DistrictBuilding.sql"
)
STAGE_COMBAT_SQL = REPO_ROOT / "mods" / "ChuuniSociety" / "Data" / "StageCombat.sql"
CHIMERA_SQL = REPO_ROOT / "mods" / "ChuuniSociety" / "Data" / "Chimera.sql"
RIKKA_COMBAT_SQL = REPO_ROOT / "mods" / "ChuuniSociety" / "Data" / "RikkaCombat.sql"
UPGRADE_SQL = REPO_ROOT / "mods" / "ChuuniSociety" / "Data" / "UpgradeDiscounts.sql"
BOUNDARY_SQL = REPO_ROOT / "mods" / "ChuuniSociety" / "Data" / "InvisibleBoundary.sql"
FAITH_PURCHASE_SQL = REPO_ROOT / "mods" / "ChuuniSociety" / "Data" / "FaithPurchase.sql"
GAMEPLAY_LUA = (
    REPO_ROOT / "mods" / "ChuuniSociety" / "Scripts" / "ChuuniGameplay.lua"
)
TEXT_SQL = REPO_ROOT / "mods" / "ChuuniSociety" / "Text" / "Chuuni_zh_Hans_CN.sql"
ICON_SQL = REPO_ROOT / "mods" / "ChuuniSociety" / "Icons" / "ChuuniIcons.sql"
STATUS_HUD_XML = REPO_ROOT / "mods" / "ChuuniSociety" / "UI" / "ChuuniStatusHUD.xml"
STATUS_HUD_LUA = REPO_ROOT / "mods" / "ChuuniSociety" / "UI" / "ChuuniStatusHUD.lua"
DEPLOY_SCRIPT = REPO_ROOT / "tools" / "far_east_magic_nap_society" / "deploy.ps1"
CHECK_WRAPPER = REPO_ROOT / "tools" / "far_east_magic_nap_society" / "check_static.ps1"
GAME_ROOT = Path(
    "C:/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization VI"
)
GAMEPLAY_SCHEMAS = (
    GAME_ROOT / "Base/Assets/Gameplay/Data/Schema/01_GameplaySchema.sql",
    GAME_ROOT / "DLC/Expansion2/Data/Expansion2_Schema.sql",
)


class ChuuniStaticTests(unittest.TestCase):
    def test_checker_wrapper_disables_bytecode(self) -> None:
        text = CHECK_WRAPPER.read_text(encoding="utf-8")

        self.assertIn('& python -B "tools\\far_east_magic_nap_society\\check_static.py"', text)

    def test_deployment_script_targets_only_chuuni_society(self) -> None:
        self.assertTrue(DEPLOY_SCRIPT.is_file(), DEPLOY_SCRIPT)
        text = DEPLOY_SCRIPT.read_text(encoding="utf-8")

        self.assertIn('"mods\\ChuuniSociety"', text)
        self.assertIn('"ChuuniSociety"', text)
        self.assertIn('"check_static.ps1"', text)
        self.assertIn("Refusing to deploy outside ModsRoot", text)
        self.assertNotIn("GraceAshcroft", text)

    def test_checker_runs_as_direct_script(self) -> None:
        result = subprocess.run(
            ["python", "-B", "tools/far_east_magic_nap_society/check_static.py"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_modinfo_is_gathering_storm_only(self) -> None:
        text = MODINFO.read_text(encoding="utf-8")

        self.assertIn('id="4873eb62-8ccc-4574-b784-dda455e74e68"', text)
        self.assertIn("<GameCoreInUse>Expansion2</GameCoreInUse>", text)
        self.assertIn('criteria="ChuuniExpansion2"', text)
        self.assertNotIn("1B28771A-C749-434B-9053-D1380C553DE9", text)

    def test_core_property_and_threshold_contracts(self) -> None:
        text = CORE_SQL.read_text(encoding="utf-8")

        self.assertNotIn("RESOURCE_CHUUNI_VALUE", text)
        self.assertNotIn("RESOURCECLASS_STRATEGIC", text)
        self.assertIn("'CHUUNI_VALUE_PER_DISTRICT', 1", text)
        self.assertIn("'CHUUNI_VALUE_PER_BUILDING', 1", text)
        self.assertIn("'CHUUNI_STAGE_1_THRESHOLD', 1", text)
        self.assertIn("'CHUUNI_STAGE_2_THRESHOLD', 20", text)
        self.assertIn("'CHUUNI_STAGE_3_THRESHOLD', 50", text)
        self.assertIn("'CHUUNI_STAGE_4_THRESHOLD', 100", text)

    def test_society_and_magic_circle_contracts(self) -> None:
        text = DISTRICT_BUILDING_SQL.read_text(encoding="utf-8")

        self.assertIn(
            "'DISTRICT_CHUUNI_SOCIETY', 'DISTRICT_HOLY_SITE'", text
        )
        self.assertIn(
            "'BUILDING_CLUB_MAGIC_CIRCLE', 'BUILDING_SHRINE'", text
        )
        self.assertIn(
            "'DISTRICT_CHUUNI_SOCIETY', 'GREAT_PERSON_CLASS_PROPHET', 2", text
        )
        self.assertIn(
            "'BUILDING_CLUB_MAGIC_CIRCLE', 'GREAT_PERSON_CLASS_PROPHET', 1", text
        )
        self.assertIn(
            "'BUILDING_CLUB_MAGIC_CIRCLE', 'YIELD_FAITH', 2", text
        )
        self.assertIn("Entertainment = 1", text)
        self.assertIn("Maintenance = 0", text)
        self.assertIn("Unit_BuildingPrereqs", text)
        self.assertIn("'UNIT_MISSIONARY'", text)
        self.assertIn("'BUILDING_CLUB_MAGIC_CIRCLE'", text)
        self.assertIn("CHUUNI_SOCIETY_WONDER_FAITH", text)
        self.assertIn("AdjacentWonder", text)
        self.assertIn("DISTRICT_ENTERTAINMENT_COMPLEX", text)
        self.assertIn("DISTRICT_WATER_ENTERTAINMENT_COMPLEX", text)
        self.assertNotIn("CHUUNI_SOCIETY_ADJACENT_CAMPUS_FAITH", text)
        self.assertNotIn("MODIFIER_PLAYER_DISTRICTS_ADJUST_YIELD_CHANGE", text)

    def test_society_adjacency_description_names_both_receivers(self) -> None:
        text = TEXT_SQL.read_text(encoding="utf-8")

        self.assertIn("每相邻一个学院额外获得+2信仰值", text)
        self.assertIn("每相邻一个世界奇观额外获得+2信仰值", text)
        self.assertIn("相邻学院获得+2科技值", text)
        self.assertNotIn("自身固定获得+3信仰值", text)

    def test_modinfo_registers_core_gameplay_files(self) -> None:
        text = MODINFO.read_text(encoding="utf-8")

        self.assertIn("Data/Core.sql", text)
        self.assertIn("Data/DistrictBuilding.sql", text)
        self.assertIn("Data/Chimera.sql", text)

    def test_chimera_governor_stage_one_contract(self) -> None:
        self.assertTrue(CHIMERA_SQL.is_file(), CHIMERA_SQL)
        sql_text = CHIMERA_SQL.read_text(encoding="utf-8")
        lua_text = GAMEPLAY_LUA.read_text(encoding="utf-8")
        hud_text = STATUS_HUD_LUA.read_text(encoding="utf-8")
        text = TEXT_SQL.read_text(encoding="utf-8")

        for contract in (
            "'GOVERNOR_CHIMERA', 'KIND_GOVERNOR'",
            "'GOVERNOR_PROMOTION_CHIMERA_BASE', 'KIND_GOVERNOR_PROMOTION'",
            "INSERT INTO Governors",
            "'GOVERNOR_CHIMERA'",
            "TransitionStrength",
            "500",
            "Chuuni_Icon_Chimera_512",
            "INSERT INTO Governors_XP2",
            "AssignToMajor",
            "VALUES ('GOVERNOR_CHIMERA', 0)",
            "INSERT INTO GovernorPromotions",
            "BaseAbility",
            "INSERT INTO GovernorPromotionSets",
            "CHUUNI_CHIMERA_GOVERNOR_POINT",
            "MODIFIER_PLAYER_ADJUST_GOVERNOR_POINTS",
            "'Delta', 1",
            "CHUUNI_CHIMERA_SOCIETY_PRODUCTION",
            "CHUUNI_CHIMERA_MAGIC_CIRCLE_PRODUCTION",
            "MODIFIER_CHUUNI_SINGLE_CITY_ADJUST_DISTRICT_PRODUCTION",
            "EFFECT_ADJUST_DISTRICT_PRODUCTION",
            "MODIFIER_SINGLE_CITY_ADJUST_BUILDING_PRODUCTION",
            "'DistrictType', 'DISTRICT_CHUUNI_SOCIETY'",
            "'BuildingType', 'BUILDING_CLUB_MAGIC_CIRCLE'",
            "'Amount', 100",
            "CHUUNI_CHIMERA_FAITH_TIER_10",
            "MODIFIER_PLAYER_CITIES_ADJUST_CITY_YIELD_CHANGE",
            "REQUIREMENT_CITY_HAS_SPECIFIC_GOVERNOR_PROMOTION_TYPE",
            "'Established', 1",
        ):
            self.assertIn(contract, sql_text)
        self.assertNotIn("GovernorNormal_Builder", sql_text)
        self.assertNotIn("GovernorSelected_Builder", sql_text)

        for contract in (
            'CHUUNI_CHIMERA_UNLOCKED = "CHUUNI_CHIMERA_UNLOCKED"',
            'CHUUNI_CHIMERA_TITLE_ATTACHED = "CHUUNI_CHIMERA_TITLE_ATTACHED"',
            "CHUUNI_CHIMERA_GOVERNOR_POINT",
            "AttachModifierByID(CHUUNI_CHIMERA_GOVERNOR_POINT)",
            'CHUUNI_CHIMERA_FAITH_TIER = "CHUUNI_CHIMERA_FAITH_TIER"',
            "EnsureChimeraYieldTiers",
            "CHIMERA_FAITH_MODIFIERS",
            "SnapshotChimeraRestCandidates",
            "ApplyChimeraRestBonuses",
            "ShouldGrantChimeraRestBonus",
            "unit:ChangeDamage(-actualHeal)",
            "Events.PlayerTurnDeactivated.Add",
        ):
            self.assertIn(contract, lua_text)

        for contract in (
            "GOVERNOR_CHIMERA",
            "PlayerOperations.APPOINT_GOVERNOR",
            "PlayerOperations.PARAM_GOVERNOR_TYPE",
            "UI.RequestPlayerOperation",
            "HasGovernor",
            "GetGovernorPointsSpent",
        ):
            self.assertIn(contract, hud_text)

        for contract in (
            "LOC_GOVERNOR_CHIMERA_NAME",
            "LOC_GOVERNOR_CHIMERA_TITLE",
            "LOC_GOVERNOR_CHIMERA_SHORT_TITLE",
            "LOC_GOVERNOR_CHIMERA_DESCRIPTION",
            "LOC_GOVERNOR_PROMOTION_CHIMERA_BASE_NAME",
            "LOC_GOVERNOR_PROMOTION_CHIMERA_BASE_DESCRIPTION",
        ):
            self.assertIn(contract, text)

    def test_remaining_v01_mechanics_contract(self) -> None:
        rikka = RIKKA_COMBAT_SQL.read_text(encoding="utf-8")
        chimera = CHIMERA_SQL.read_text(encoding="utf-8")
        upgrade = UPGRADE_SQL.read_text(encoding="utf-8")
        boundary = BOUNDARY_SQL.read_text(encoding="utf-8")
        faith = FAITH_PURCHASE_SQL.read_text(encoding="utf-8")
        lua = GAMEPLAY_LUA.read_text(encoding="utf-8")
        hud = STATUS_HUD_LUA.read_text(encoding="utf-8")

        for token in (
            "RIKKA_SCHWARZ_SECHS_DEFENSE",
            "RIKKA_SCHWARZ_SECHS_ATTACK_STAGE_4",
            "CLASS_ALL_COMBAT_UNITS",
            "CHUUNI_STAGE_4_OWNER_REQUIREMENTS",
        ):
            self.assertIn(token, rikka)
        for token in (
            "ABILITY_CHUUNI_CHIMERA_COMBAT",
            "ABILITY_CHUUNI_CHIMERA_MOBILITY",
            "CHUUNI_CHIMERA_CULTURE_TIER_",
            "CHUUNI_CHIMERA_SCIENCE_TIER_",
            "CHUUNI_CHIMERA_STAGE_4_MAGIC_CIRCLE_FAITH",
            "CHUUNI_CHIMERA_STAGE_4_MAGIC_CIRCLE_CULTURE",
            "CHUUNI_CHIMERA_STAGE_4_MAGIC_CIRCLE_SCIENCE",
        ):
            self.assertIn(token, chimera)
        self.assertIn("MODIFIER_PLAYER_ADJUST_UNIT_UPGRADE_DISCOUNT_PERCENT", upgrade)
        self.assertIn("MODIFIER_PLAYER_ADJUST_UNIT_UPGRADE_RESOURCE_COST_MODIFIER", upgrade)
        self.assertIn("IMPROVEMENT_INVISIBLE_BOUNDARY", boundary)
        self.assertIn("OnePerCity", boundary)
        self.assertIn("NO_PLUNDER", boundary)
        self.assertIn("MODIFIER_CITY_ENABLE_BUILDING_FAITH_PURCHASE", faith)
        self.assertIn("GameEvents.ChuuniTeleport.Add", lua)
        self.assertIn("UnitManager.PlaceUnit", lua)
        self.assertIn("parameters.OnStart = \"ChuuniTeleport\"", hud)

    def test_modinfo_registers_gameplay_script(self) -> None:
        text = MODINFO.read_text(encoding="utf-8")

        self.assertIn("<AddGameplayScripts", text)
        self.assertIn("Scripts/ChuuniGameplay.lua", text)

    def test_modinfo_registers_chuuni_status_hud(self) -> None:
        text = MODINFO.read_text(encoding="utf-8")

        self.assertIn("<AddUserInterfaces", text)
        self.assertIn("<Context>InGame</Context>", text)
        self.assertIn("UI/ChuuniStatusHUD.xml", text)
        self.assertIn("UI/ChuuniStatusHUD.lua", text)

    def test_chuuni_status_hud_contract(self) -> None:
        self.assertTrue(STATUS_HUD_XML.is_file(), STATUS_HUD_XML)
        self.assertTrue(STATUS_HUD_LUA.is_file(), STATUS_HUD_LUA)
        xml_text = STATUS_HUD_XML.read_text(encoding="utf-8")
        lua_text = STATUS_HUD_LUA.read_text(encoding="utf-8")

        self.assertIn('<Instance Name="ChuuniStatusButtonInstance">', xml_text)
        self.assertIn('Offset="292,72"', xml_text)
        for control_id in (
            'ID="ChuuniStatusRoot"',
            'ID="ChuuniStatusButton"',
            'ID="ChuuniStatusIcon"',
            'ID="ChuuniValueBadge"',
            'ID="ChuuniValueText"',
        ):
            self.assertIn(control_id, xml_text)
        for obsolete_control in (
            "ChuuniStatusContainer",
            "ChuuniValueLabel",
            "ChuuniStageLabel",
            "ChuuniNextThresholdLabel",
        ):
            self.assertNotIn(obsolete_control, xml_text)

        for contract in (
            "CIVILIZATION_CHUUNI_SOCIETY",
            'CHUUNI_VALUE = "CHUUNI_VALUE"',
            "CHUUNI_STAGE",
            "Game.GetLocalPlayer()",
            "GetCivilizationTypeName",
            "GetPropertyNumber",
            "GetStatusModel",
            "AttachStatusButton",
            'ContextPtr:LookUpControl("/InGame/TopLevelHUD")',
            "ContextPtr:BuildInstanceForControl(",
            '"ChuuniStatusButtonInstance"',
            '"button mounted target=/InGame/TopLevelHUD"',
            "include(\"PopupDialog\")",
            "PopupDialogInGame:new",
            "AddTitle",
            "AddText",
            "AddConfirmButton",
            "BuildPopupText",
            "OpenChuuniPopup",
            "Mouse.eLClick",
            "Mouse.eMouseEnter",
            "LuaEvents.ChuuniStatusChanged.Add",
            "Events.GameCoreEventPublishComplete.Add",
            "Events.LocalPlayerChanged.Add",
            "Events.PlayerTurnActivated.Add",
            "Events.LoadGameViewStateDone.Add(OnLoadGameViewStateDone)",
            "m_buttonInstance.ChuuniStatusRoot:SetHide",
            "m_buttonInstance.ChuuniStatusButton:SetToolTipString",
            "m_buttonInstance.ChuuniValueText:SetText",
            "LOC_CHUUNI_STATUS_UNMET_RELIGION",
            "[ChuuniStatusHUD]",
            '"hidden player="',
            '"visible player="',
        ):
            self.assertIn(contract, lua_text)
        for obsolete_contract in (
            "RESOURCE_CHUUNI_VALUE",
            "GetResources",
            "GetResourceAmount",
            "ChuuniStatusContainer",
        ):
            self.assertNotIn(obsolete_contract, lua_text)

        popup_function_offset = lua_text.index("local function OpenChuuniPopup")
        popup_constructor_offset = lua_text.index("PopupDialogInGame:new")
        self.assertGreater(popup_constructor_offset, popup_function_offset)
        self.assertNotIn("local m_popupDialog", lua_text)
        self.assertIn(
            "local function OnLoadGameViewStateDone()\n"
            "    if AttachStatusButton() then\n"
            "        Refresh()\n"
            "    end\n"
            "end",
            lua_text,
        )

    def test_chuuni_popup_localization_lists_all_stages(self) -> None:
        text = TEXT_SQL.read_text(encoding="utf-8")
        lua_text = STATUS_HUD_LUA.read_text(encoding="utf-8")

        self.assertNotIn("LOC_RESOURCE_CHUUNI_VALUE", text)
        self.assertIn("LOC_CHUUNI_STATUS_POPUP_TITLE", text)
        self.assertIn("LOC_CHUUNI_STATUS_BUTTON_TOOLTIP", text)
        self.assertIn("LOC_CHUUNI_STATUS_CLOSE", text)
        self.assertIn("特色结社与部室魔法阵+100%生产力", text)
        self.assertIn("每10点中二值使该城市+1信仰", text)
        self.assertIn("正常休整的单位额外恢复20生命值", text)
        self.assertNotIn("阶段专属能力尚未实现", text)
        self.assertIn("幻想武装：升级金币-25%", text)
        self.assertIn("所有部室魔法阵城市+5信仰", text)
        for stage in ("第一阶段", "第二阶段", "第三阶段", "第四阶段"):
            self.assertIn(stage, text)

        tooltip_start = lua_text.index("local function BuildButtonTooltip")
        tooltip_end = lua_text.index("local function BuildPopupText")
        tooltip_function = lua_text[tooltip_start:tooltip_end]
        self.assertNotIn("BuildStageOverview", tooltip_function)
        self.assertIn("status.nextThreshold", tooltip_function)

    def test_chuuni_value_icon_is_ui_only(self) -> None:
        text = ICON_SQL.read_text(encoding="utf-8")

        self.assertIn("ICON_CHUUNI_VALUE", text)
        self.assertIn("ICON_ATLAS_CHUUNI_VALUE", text)
        self.assertNotIn("RESOURCE_CHUUNI_VALUE", text)
        self.assertNotIn("ICON_RESOURCE_CHUUNI_VALUE", text)

    def test_custom_icon_registration_is_deterministic(self) -> None:
        text = ICON_SQL.read_text(encoding="utf-8")

        self.assertIn("DELETE FROM IconDefinitions", text)
        self.assertIn("DELETE FROM IconTextureAtlases", text)
        self.assertNotIn(
            "SELECT 'ICON_BUILDING_CLUB_MAGIC_CIRCLE', Atlas", text
        )
        for icon_name, atlas_name in (
            ("ICON_DISTRICT_CHUUNI_SOCIETY", "ICON_ATLAS_CHUUNI_GAMEPLAY"),
            (
                "ICON_BUILDING_CLUB_MAGIC_CIRCLE",
                "ICON_ATLAS_CHUUNI_MAGIC_CIRCLE",
            ),
            ("ICON_GOVERNOR_CHIMERA", "ICON_ATLAS_CHUUNI_CHIMERA"),
            ("ICON_GOVERNOR_CHIMERA_FILL", "ICON_ATLAS_CHUUNI_CHIMERA"),
            ("ICON_GOVERNOR_CHIMERA_SLOT", "ICON_ATLAS_CHUUNI_CHIMERA"),
        ):
            self.assertEqual(text.count(f"('{icon_name}', '{atlas_name}', 0)"), 1)

    def test_chuuni_progression_lua_contract(self) -> None:
        text = GAMEPLAY_LUA.read_text(encoding="utf-8")

        for contract in (
            "function GetChuuniValue",
            "function ChangeChuuniValue",
            "function UpdateChuuniStage",
            "CHUUNI_FIRST_COASTAL_CITY_FOUNDED",
            'CHUUNI_VALUE = "CHUUNI_VALUE"',
            "CHUUNI_LAST_VALUE_TICK_TURN",
            "player:SetProperty(CHUUNI_VALUE",
            "STAGE_MARKER_RESOURCE_TYPES",
            "STAGE_MARKER_RESOURCE_INDICES",
            "EnsureStageMarkerResource",
            "EnsureStageMarkerResources",
            "resources:GetResourceAmount(resourceIndex)",
            "resources:ChangeResourceAmount(resourceIndex, 1 - currentAmount)",
            "GetReligionTypeCreated",
            "Events.PlayerTurnActivated.Add",
            "Events.ReligionFounded.Add",
            "Events.CityAddedToMap.Add",
            "ChangeChuuniValue(playerID, 5)",
            "math.min(CHUUNI_VALUE_CAP",
            "AttachModifierByID(CHUUNI_COASTAL_AMENITY_MODIFIER)",
            "LuaEvents.ChuuniStatusChanged",
        ):
            self.assertIn(contract, text)

        for obsolete_contract in (
            "RESOURCE_CHUUNI_VALUE",
            "CHUUNI_RESOURCE_INDEX",
            "CHUUNI_LAST_RESOURCE_TICK_TURN",
            "CHUUNI_STAGE_1_COMBAT_ATTACHED",
            "CHUUNI_STAGE_2_COMBAT_ATTACHED",
            "CHUUNI_STAGE_3_COMBAT_ATTACHED",
            "EnsureStageCombatModifier",
            "STAGE_MODIFIERS",
            "player:AttachModifierByID(modifierID)",
        ):
            self.assertNotIn(obsolete_contract, text)

        stage_properties = [
            f"CHUUNI_STAGE_{stage}_UNLOCKED" for stage in range(1, 5)
        ]
        positions = [text.index(property_name) for property_name in stage_properties]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("HasFoundedReligion(player)", text)
        self.assertIn("stage >= 1", text)
        self.assertIn("stage >= 2", text)
        self.assertIn("stage >= 3", text)

    def test_unset_player_properties_are_materialized_before_number_conversion(self) -> None:
        text = GAMEPLAY_LUA.read_text(encoding="utf-8")

        self.assertNotIn("tonumber(player:GetProperty(", text)
        self.assertIn(
            "local storedStage = player:GetProperty(CHUUNI_STAGE)",
            text,
        )
        self.assertIn("local stage = tonumber(storedStage) or 0", text)
        self.assertIn(
            "local lastValueTickTurn = "
            "player:GetProperty(CHUUNI_LAST_VALUE_TICK_TURN)",
            text,
        )
        self.assertIn(
            "if tonumber(lastValueTickTurn) == currentTurn then",
            text,
        )

    def test_bonus_marker_gated_full_staged_combat_contract(self) -> None:
        self.assertTrue(STAGE_COMBAT_SQL.is_file(), STAGE_COMBAT_SQL)
        modinfo_text = MODINFO.read_text(encoding="utf-8")
        stage_text = STAGE_COMBAT_SQL.read_text(encoding="utf-8")
        lua_text = GAMEPLAY_LUA.read_text(encoding="utf-8")

        self.assertIn("Data/StageCombat.sql", modinfo_text)
        for stage in range(1, 5):
            resource_type = f"RESOURCE_CHUUNI_STAGE_MARKER_{stage}"
            modifier_id = f"CHUUNI_FANTASY_COMBAT_STAGE_{stage}_FULL"
            self.assertIn(f"('{resource_type}', 'KIND_RESOURCE')", stage_text)
            self.assertIn(resource_type, lua_text)
            self.assertIn(modifier_id, stage_text)
            self.assertIn(
                f"('TRAIT_CIVILIZATION_CHUUNI_SOCIETY', '{modifier_id}')",
                stage_text,
            )

        for modifier_id, amount in (
            ("CHUUNI_FANTASY_COMBAT_STAGE_1_FULL", 3),
            ("CHUUNI_FANTASY_COMBAT_STAGE_2_FULL", 5),
            ("CHUUNI_FANTASY_COMBAT_STAGE_3_FULL", 8),
            ("CHUUNI_FANTASY_COMBAT_STAGE_4_FULL", 8),
        ):
            self.assertIn(f"('{modifier_id}', 'Amount', {amount})", stage_text)
        self.assertEqual(
            stage_text.count("MODIFIER_PLAYER_UNITS_ADJUST_COMBAT_STRENGTH"),
            4,
        )
        self.assertEqual(stage_text.count("'Preview'"), 4)
        self.assertEqual(stage_text.count("'RESOURCECLASS_BONUS', 0"), 4)
        self.assertIn("CivilopediaPageExcludes", stage_text)
        self.assertIn("REQUIREMENT_PLAYER_HAS_RESOURCE_OWNED", stage_text)
        self.assertIn("TraitModifiers", stage_text)
        self.assertIn("CHUUNI_STAGE_1_OWNER_REQUIREMENTS", stage_text)
        self.assertIn("CHUUNI_STAGE_4_OWNER_REQUIREMENTS", stage_text)
        self.assertNotIn("'Amount', '1'", stage_text)
        self.assertNotIn("'Amount', 1", stage_text)
        for forbidden in (
            "RESOURCE_CHUUNI_VALUE",
            "CHUUNI_FANTASY_COMBAT_STAGE_1',",
            "CHUUNI_FANTASY_COMBAT_STAGE_2',",
            "CHUUNI_FANTASY_COMBAT_STAGE_3',",
        ):
            self.assertNotIn(forbidden, stage_text)
        self.assertNotIn("player:AttachModifierByID(modifierID)", lua_text)

    def test_coastal_amenity_modifier_contract(self) -> None:
        text = CORE_SQL.read_text(encoding="utf-8")

        self.assertIn("CHUUNI_RIKKA_COASTAL_CITY_AMENITIES", text)
        self.assertIn("MODIFIER_PLAYER_CITIES_ADJUST_TRAIT_AMENITY", text)
        self.assertIn("'Amount', 2", text)

    @unittest.skipUnless(
        all(path.is_file() for path in GAMEPLAY_SCHEMAS),
        "installed Civilization VI Gathering Storm schemas are unavailable",
    )
    def test_gameplay_sql_executes_against_expansion2_schema(self) -> None:
        connection = sqlite3.connect(":memory:")
        try:
            for schema in GAMEPLAY_SCHEMAS:
                connection.executescript(schema.read_text(encoding="utf-8-sig"))
            # Civ6 fills Types.Hash through its database loader. Plain SQLite
            # leaves the NOT NULL UNIQUE default at zero, so replace only this
            # loader-owned table for semantic SQL validation.
            connection.executescript(
                """
                ALTER TABLE Types RENAME TO TypesWithGameHash;
                CREATE TABLE Types (
                    Type TEXT PRIMARY KEY,
                    Hash INTEGER,
                    Kind TEXT NOT NULL
                );
                """
            )
            connection.executemany(
                """
                INSERT INTO Districts
                    (DistrictType, Name, Cost, RequiresPlacement, NoAdjacentCity,
                     Aqueduct, InternalOnly, CaptureRemovesBuildings,
                     CaptureRemovesCityDefenses, PlunderType, MilitaryDomain)
                VALUES (?, ?, ?, 1, 0, 0, 0, 0, 0, 'PLUNDER_FAITH', 'NO_DOMAIN')
                """,
                (
                    ("DISTRICT_HOLY_SITE", "Holy Site", 54),
                    ("DISTRICT_CAMPUS", "Campus", 54),
                    ("DISTRICT_THEATER", "Theater", 54),
                    ("DISTRICT_COMMERCIAL_HUB", "Commercial Hub", 54),
                    ("DISTRICT_HARBOR", "Harbor", 54),
                    ("DISTRICT_INDUSTRIAL_ZONE", "Industrial Zone", 54),
                    ("DISTRICT_ENTERTAINMENT_COMPLEX", "Entertainment", 54),
                    ("DISTRICT_WATER_ENTERTAINMENT_COMPLEX", "Water Park", 54),
                    ("DISTRICT_TEST_CAMPUS_REPLACEMENT", "Test Campus", 54),
                ),
            )
            connection.execute(
                """
                INSERT INTO DistrictReplaces
                    (CivUniqueDistrictType, ReplacesDistrictType)
                VALUES
                    ('DISTRICT_TEST_CAMPUS_REPLACEMENT', 'DISTRICT_CAMPUS')
                """
            )
            connection.execute(
                """
                INSERT INTO Buildings
                    (BuildingType, Name, Description, PrereqTech, PrereqDistrict,
                     PurchaseYield, Cost, AdvisorType, Maintenance, CitizenSlots)
                VALUES
                    ('BUILDING_SHRINE', 'Shrine', 'Shrine', 'TECH_ASTROLOGY',
                     'DISTRICT_HOLY_SITE', 'YIELD_GOLD', 70,
                     'ADVISOR_RELIGIOUS', 1, 1)
                """
            )
            connection.execute(
                """
                INSERT INTO District_GreatPersonPoints
                    (DistrictType, GreatPersonClassType, PointsPerTurn)
                VALUES
                    ('DISTRICT_HOLY_SITE', 'GREAT_PERSON_CLASS_PROPHET', 1)
                """
            )
            connection.execute(
                """
                INSERT INTO Building_GreatPersonPoints
                    (BuildingType, GreatPersonClassType, PointsPerTurn)
                VALUES
                    ('BUILDING_SHRINE', 'GREAT_PERSON_CLASS_PROPHET', 1)
                """
            )
            connection.execute(
                """
                INSERT INTO Units
                    (UnitType, Name, BaseSightRange, BaseMoves, Domain,
                     FormationClass, Cost)
                VALUES
                    ('UNIT_MISSIONARY', 'Missionary', 2, 4, 'DOMAIN_LAND',
                     'FORMATION_CLASS_CIVILIAN', 75)
                """
            )
            connection.execute(
                """
                INSERT INTO Unit_BuildingPrereqs
                    (Unit, PrereqBuilding, NumSupported)
                VALUES
                    ('UNIT_MISSIONARY', 'BUILDING_SHRINE', -1)
                """
            )
            connection.execute(
                """
                INSERT INTO Adjacency_YieldChanges
                    (ID, Description, YieldType, YieldChange,
                     TilesRequired, AdjacentNaturalWonder)
                VALUES
                    ('TEST_HOLY_SITE_NATURAL_WONDER',
                     'Test Holy Site natural wonder',
                     'YIELD_FAITH', 2, 1, 1)
                """
            )
            connection.execute(
                """
                INSERT INTO District_Adjacencies (DistrictType, YieldChangeId)
                VALUES
                    ('DISTRICT_HOLY_SITE',
                     'TEST_HOLY_SITE_NATURAL_WONDER')
                """
            )
            connection.executescript(CORE_SQL.read_text(encoding="utf-8"))
            connection.executescript(
                DISTRICT_BUILDING_SQL.read_text(encoding="utf-8")
            )
            connection.executescript(STAGE_COMBAT_SQL.read_text(encoding="utf-8"))
            connection.executescript(RIKKA_COMBAT_SQL.read_text(encoding="utf-8"))
            connection.executescript(CHIMERA_SQL.read_text(encoding="utf-8"))
            connection.executescript(UPGRADE_SQL.read_text(encoding="utf-8"))
            connection.executescript(BOUNDARY_SQL.read_text(encoding="utf-8"))
            connection.executescript(FAITH_PURCHASE_SQL.read_text(encoding="utf-8"))
            self.assertEqual(
                connection.execute(
                    """
                    SELECT PointsPerTurn FROM District_GreatPersonPoints
                    WHERE DistrictType = 'DISTRICT_CHUUNI_SOCIETY'
                      AND GreatPersonClassType = 'GREAT_PERSON_CLASS_PROPHET'
                    """
                ).fetchone(),
                (2,),
            )
            self.assertEqual(
                connection.execute(
                    """
                    SELECT Maintenance, Entertainment FROM Buildings
                    WHERE BuildingType = 'BUILDING_CLUB_MAGIC_CIRCLE'
                    """
                ).fetchone(),
                (0, 1),
            )
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
            self.assertEqual(
                connection.execute(
                    """
                    SELECT NumSupported
                    FROM Unit_BuildingPrereqs
                    WHERE Unit = 'UNIT_MISSIONARY'
                      AND PrereqBuilding = 'BUILDING_CLUB_MAGIC_CIRCLE'
                    """
                ).fetchone(),
                (-1,),
            )
            self.assertEqual(
                connection.execute(
                    """
                    SELECT COUNT(*)
                    FROM District_Adjacencies
                    WHERE DistrictType = 'DISTRICT_CHUUNI_SOCIETY'
                      AND YieldChangeId =
                          'TEST_HOLY_SITE_NATURAL_WONDER'
                    """
                ).fetchone(),
                (1,),
            )
            self.assertEqual(
                connection.execute(
                    """
                    SELECT a.AdjacentDistrict, a.AdjacentWonder,
                           a.YieldType, a.YieldChange
                    FROM District_Adjacencies AS d
                    JOIN Adjacency_YieldChanges AS a
                      ON a.ID = d.YieldChangeId
                    WHERE d.DistrictType = 'DISTRICT_CHUUNI_SOCIETY'
                      AND (
                          d.YieldChangeId LIKE
                              'CHUUNI_SOCIETY_CAMPUS_FAITH_%'
                          OR d.YieldChangeId =
                              'CHUUNI_SOCIETY_WONDER_FAITH'
                      )
                    ORDER BY a.AdjacentWonder, a.AdjacentDistrict
                    """
                ).fetchall(),
                [
                    ("DISTRICT_CAMPUS", 0, "YIELD_FAITH", 2),
                    (
                        "DISTRICT_TEST_CAMPUS_REPLACEMENT",
                        0,
                        "YIELD_FAITH",
                        2,
                    ),
                    (None, 1, "YIELD_FAITH", 2),
                ],
            )
            self.assertEqual(
                connection.execute(
                    """
                    SELECT d.DistrictType, a.YieldType, a.YieldChange
                    FROM District_Adjacencies AS d
                    JOIN Adjacency_YieldChanges AS a
                      ON a.ID = d.YieldChangeId
                    WHERE a.AdjacentDistrict =
                          'DISTRICT_CHUUNI_SOCIETY'
                    ORDER BY d.DistrictType
                    """
                ).fetchall(),
                [
                    ("DISTRICT_CAMPUS", "YIELD_SCIENCE", 2),
                    (
                        "DISTRICT_ENTERTAINMENT_COMPLEX",
                        "YIELD_CULTURE",
                        2,
                    ),
                    (
                        "DISTRICT_INDUSTRIAL_ZONE",
                        "YIELD_PRODUCTION",
                        2,
                    ),
                    (
                        "DISTRICT_TEST_CAMPUS_REPLACEMENT",
                        "YIELD_SCIENCE",
                        2,
                    ),
                    ("DISTRICT_THEATER", "YIELD_CULTURE", 2),
                    (
                        "DISTRICT_WATER_ENTERTAINMENT_COMPLEX",
                        "YIELD_CULTURE",
                        2,
                    ),
                ],
            )
            self.assertEqual(
                connection.execute(
                    """
                    SELECT m.ModifierId, m.ModifierType, a.Value
                    FROM Modifiers AS m
                    JOIN ModifierArguments AS a ON a.ModifierId = m.ModifierId
                    WHERE m.ModifierId LIKE 'CHUUNI_FANTASY_COMBAT_STAGE_%'
                      AND a.Name = 'Amount'
                    ORDER BY m.ModifierId
                    """
                ).fetchall(),
                [
                    ("CHUUNI_FANTASY_COMBAT_STAGE_1_FULL", "MODIFIER_PLAYER_UNITS_ADJUST_COMBAT_STRENGTH", "3"),
                    ("CHUUNI_FANTASY_COMBAT_STAGE_2_FULL", "MODIFIER_PLAYER_UNITS_ADJUST_COMBAT_STRENGTH", "5"),
                    ("CHUUNI_FANTASY_COMBAT_STAGE_3_FULL", "MODIFIER_PLAYER_UNITS_ADJUST_COMBAT_STRENGTH", "8"),
                    ("CHUUNI_FANTASY_COMBAT_STAGE_4_FULL", "MODIFIER_PLAYER_UNITS_ADJUST_COMBAT_STRENGTH", "8"),
                ],
            )
            self.assertEqual(
                connection.execute(
                    """
                    SELECT ModifierId, Permanent, OwnerRequirementSetId
                    FROM Modifiers
                    WHERE ModifierId LIKE 'CHUUNI_FANTASY_COMBAT_STAGE_%'
                    ORDER BY ModifierId
                    """
                ).fetchall(),
                [
                    ("CHUUNI_FANTASY_COMBAT_STAGE_1_FULL", 0, "CHUUNI_STAGE_1_OWNER_REQUIREMENTS"),
                    ("CHUUNI_FANTASY_COMBAT_STAGE_2_FULL", 0, "CHUUNI_STAGE_2_OWNER_REQUIREMENTS"),
                    ("CHUUNI_FANTASY_COMBAT_STAGE_3_FULL", 0, "CHUUNI_STAGE_3_OWNER_REQUIREMENTS"),
                    ("CHUUNI_FANTASY_COMBAT_STAGE_4_FULL", 0, "CHUUNI_STAGE_4_OWNER_REQUIREMENTS"),
                ],
            )
            self.assertEqual(
                connection.execute(
                    """
                    SELECT COUNT(*) FROM TraitModifiers
                    WHERE ModifierId LIKE 'CHUUNI_FANTASY_COMBAT_STAGE_%'
                    """
                ).fetchone(),
                (4,),
            )
            self.assertEqual(
                connection.execute(
                    """
                    SELECT TransitionStrength, TraitType, PortraitImage,
                           PortraitImageSelected
                    FROM Governors
                    WHERE GovernorType = 'GOVERNOR_CHIMERA'
                    """
                ).fetchone(),
                (
                    500,
                    "TRAIT_CIVILIZATION_CHUUNI_SOCIETY",
                    "Chuuni_Icon_Chimera_512",
                    "Chuuni_Icon_Chimera_512",
                ),
            )
            self.assertEqual(
                connection.execute(
                    """
                    SELECT COUNT(*) FROM Resources
                    WHERE ResourceType LIKE 'RESOURCE_CHUUNI_STAGE_MARKER_%'
                      AND ResourceClassType = 'RESOURCECLASS_BONUS'
                      AND Frequency = 0
                    """
                ).fetchone(),
                (4,),
            )
            self.assertEqual(
                connection.execute(
                    """
                    SELECT COUNT(*) FROM Modifiers
                    WHERE ModifierId LIKE 'CHUUNI_CHIMERA_FAITH_TIER_%'
                      AND ModifierType =
                          'MODIFIER_PLAYER_CITIES_ADJUST_CITY_YIELD_CHANGE'
                      AND SubjectRequirementSetId =
                          'CHUUNI_CITY_HAS_ESTABLISHED_CHIMERA_REQUIREMENTS'
                    """
                ).fetchone(),
                (10,),
            )
            self.assertEqual(
                connection.execute(
                    """
                    SELECT CollectionType, EffectType
                    FROM DynamicModifiers
                    WHERE ModifierType =
                          'MODIFIER_CHUUNI_SINGLE_CITY_ADJUST_DISTRICT_PRODUCTION'
                    """
                ).fetchone(),
                ("COLLECTION_OWNER", "EFFECT_ADJUST_DISTRICT_PRODUCTION"),
            )
            self.assertEqual(
                connection.execute(
                    """
                    SELECT ModifierId FROM GovernorPromotionModifiers
                    WHERE GovernorPromotionType =
                          'GOVERNOR_PROMOTION_CHIMERA_BASE'
                    ORDER BY ModifierId
                    """
                ).fetchall(),
                [
                    ("CHUUNI_CHIMERA_MAGIC_CIRCLE_PRODUCTION",),
                    ("CHUUNI_CHIMERA_SOCIETY_PRODUCTION",),
                ],
            )
            self.assertEqual(
                connection.execute(
                    """
                    SELECT BaseAbility
                    FROM GovernorPromotions
                    WHERE GovernorPromotionType =
                          'GOVERNOR_PROMOTION_CHIMERA_BASE'
                    """
                ).fetchone(),
                (1,),
            )
            self.assertEqual(
                connection.execute(
                    """
                    SELECT ModifierId, Value
                    FROM ModifierArguments
                    WHERE ModifierId IN (
                        'RIKKA_SCHWARZ_SECHS_DEFENSE',
                        'RIKKA_SCHWARZ_SECHS_ATTACK_STAGE_4'
                    )
                      AND Name = 'Amount'
                    ORDER BY ModifierId
                    """
                ).fetchall(),
                [
                    ("RIKKA_SCHWARZ_SECHS_ATTACK_STAGE_4", "5"),
                    ("RIKKA_SCHWARZ_SECHS_DEFENSE", "5"),
                ],
            )
            self.assertEqual(
                connection.execute(
                    """
                    SELECT ModifierId, Value
                    FROM ModifierArguments
                    WHERE ModifierId LIKE
                          'CHUUNI_FANTASY_ARMAMENT_STAGE_%_GOLD'
                      AND Name = 'Amount'
                    ORDER BY ModifierId
                    """
                ).fetchall(),
                [
                    ("CHUUNI_FANTASY_ARMAMENT_STAGE_2_GOLD", "25"),
                    ("CHUUNI_FANTASY_ARMAMENT_STAGE_3_GOLD", "50"),
                    ("CHUUNI_FANTASY_ARMAMENT_STAGE_4_GOLD", "100"),
                ],
            )
            self.assertEqual(
                connection.execute(
                    """
                    SELECT PrereqTech, Domain, SameAdjacentValid, OnePerCity,
                           PlunderType
                    FROM Improvements
                    WHERE ImprovementType =
                          'IMPROVEMENT_INVISIBLE_BOUNDARY'
                    """
                ).fetchone(),
                ("TECH_CARTOGRAPHY", "DOMAIN_SEA", 0, 1, "NO_PLUNDER"),
            )
            self.assertEqual(
                connection.execute(
                    """
                    SELECT COUNT(*)
                    FROM Modifiers
                    WHERE ModifierType =
                          'MODIFIER_CITY_ENABLE_BUILDING_FAITH_PURCHASE'
                      AND ModifierId LIKE 'CHUUNI_%_BUILDING_FAITH_PURCHASE'
                    """
                ).fetchone(),
                (2,),
            )
        finally:
            connection.close()


if __name__ == "__main__":
    unittest.main()
