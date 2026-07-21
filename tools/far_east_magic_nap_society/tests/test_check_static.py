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
GAMEPLAY_LUA = (
    REPO_ROOT / "mods" / "ChuuniSociety" / "Scripts" / "ChuuniGameplay.lua"
)
TEXT_SQL = REPO_ROOT / "mods" / "ChuuniSociety" / "Text" / "Chuuni_zh_Hans_CN.sql"
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
            ["python", "tools/far_east_magic_nap_society/check_static.py"],
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

    def test_core_resource_and_threshold_contracts(self) -> None:
        text = CORE_SQL.read_text(encoding="utf-8")

        self.assertIn("'RESOURCE_CHUUNI_VALUE', 1, 0, 0, 0, 100", text)
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

    def test_society_adjacency_description_names_both_receivers(self) -> None:
        text = TEXT_SQL.read_text(encoding="utf-8")

        self.assertIn("自身固定获得+3信仰值", text)
        self.assertIn("相邻学院获得+2科技值", text)

    def test_modinfo_registers_core_gameplay_files(self) -> None:
        text = MODINFO.read_text(encoding="utf-8")

        self.assertIn("Data/Core.sql", text)
        self.assertIn("Data/DistrictBuilding.sql", text)

    def test_modinfo_registers_gameplay_script(self) -> None:
        text = MODINFO.read_text(encoding="utf-8")

        self.assertIn("<AddGameplayScripts", text)
        self.assertIn("Scripts/ChuuniGameplay.lua", text)

    def test_chuuni_progression_lua_contract(self) -> None:
        text = GAMEPLAY_LUA.read_text(encoding="utf-8")

        for contract in (
            "function GetChuuniValue",
            "function ChangeChuuniValue",
            "function UpdateChuuniStage",
            "CHUUNI_LAST_RESOURCE_TICK_TURN",
            "CHUUNI_FIRST_COASTAL_CITY_FOUNDED",
            "GetReligionTypeCreated",
            "Events.PlayerTurnActivated.Add",
            "Events.ReligionFounded.Add",
            "Events.CityAddedToMap.Add",
            "ChangeChuuniValue(playerID, 5)",
            "math.min(CHUUNI_VALUE_CAP",
            "AttachModifierByID(CHUUNI_COASTAL_AMENITY_MODIFIER)",
        ):
            self.assertIn(contract, text)

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
            "local lastResourceTickTurn = "
            "player:GetProperty(CHUUNI_LAST_RESOURCE_TICK_TURN)",
            text,
        )
        self.assertIn(
            "if tonumber(lastResourceTickTurn) == currentTurn then",
            text,
        )

    def test_stage_one_combat_contract(self) -> None:
        self.assertTrue(STAGE_COMBAT_SQL.is_file(), STAGE_COMBAT_SQL)
        modinfo_text = MODINFO.read_text(encoding="utf-8")
        stage_text = STAGE_COMBAT_SQL.read_text(encoding="utf-8")
        lua_text = GAMEPLAY_LUA.read_text(encoding="utf-8")

        self.assertIn("Data/StageCombat.sql", modinfo_text)
        self.assertIn("CHUUNI_STAGE_1_COMBAT", stage_text)
        self.assertIn("MODIFIER_PLAYER_UNITS_ADJUST_COMBAT_STRENGTH", stage_text)
        self.assertIn("('CHUUNI_STAGE_1_COMBAT', 'Amount', 3)", stage_text)
        self.assertIn(
            "('CHUUNI_STAGE_1_COMBAT', 'Preview', "
            "'LOC_CHUUNI_STAGE_1_COMBAT_PREVIEW')",
            stage_text,
        )
        self.assertIn("LOC_CHUUNI_STAGE_1_COMBAT_PREVIEW", TEXT_SQL.read_text(encoding="utf-8"))
        self.assertIn("CHUUNI_STAGE_1_COMBAT_ATTACHED", lua_text)
        self.assertIn(
            "player:AttachModifierByID(CHUUNI_STAGE_1_COMBAT_MODIFIER)",
            lua_text,
        )

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
                ),
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
            connection.executescript(CORE_SQL.read_text(encoding="utf-8"))
            connection.executescript(
                DISTRICT_BUILDING_SQL.read_text(encoding="utf-8")
            )
            connection.executescript(STAGE_COMBAT_SQL.read_text(encoding="utf-8"))
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
                    SELECT m.ModifierType, a.Value
                    FROM Modifiers AS m
                    JOIN ModifierArguments AS a ON a.ModifierId = m.ModifierId
                    WHERE m.ModifierId = 'CHUUNI_STAGE_1_COMBAT'
                      AND a.Name = 'Amount'
                    """
                ).fetchone(),
                ("MODIFIER_PLAYER_UNITS_ADJUST_COMBAT_STRENGTH", "3"),
            )
            self.assertEqual(
                connection.execute(
                    """
                    SELECT StockpileCap FROM Resource_Consumption
                    WHERE ResourceType = 'RESOURCE_CHUUNI_VALUE'
                    """
                ).fetchone(),
                (100,),
            )
        finally:
            connection.close()


if __name__ == "__main__":
    unittest.main()
