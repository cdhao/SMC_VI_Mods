#!/usr/bin/env python3
"""Static contracts for the deployable Chuuni Society Civilization VI mod."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.common.civ6_static_checks import (
    TextContract,
    ValidationError,
    apply_text_contracts,
    require_file,
    runtime_mod_paths,
)


MOD_ROOT = Path("mods") / "ChuuniSociety"


def check_runtime_layout(root: Path) -> None:
    mod_root = root / MOD_ROOT
    for relative in (
        "ChuuniSociety.modinfo",
        "Data/Config.sql",
        "Data/Colors.xml",
        "Data/Core.sql",
        "Data/StageCombat.sql",
        "Data/Chimera.sql",
        "Data/DistrictBuilding.sql",
        "Scripts/ChuuniGameplay.lua",
        "UI/ChuuniStatusHUD.xml",
        "UI/ChuuniStatusHUD.lua",
        "ChuuniSociety.dep",
        "ArtDefs/FallbackLeaders.artdef",
        "Platforms/Windows/BLPs/ChuuniUITextureV1.blp",
        "Platforms/Windows/BLPs/ChuuniLeaderFallbacks.blp",
        "Text/Chuuni_zh_Hans_CN.sql",
        "Icons/ChuuniIcons.sql",
    ):
        require_file(mod_root / relative)

    forbidden = runtime_mod_paths(mod_root)
    if forbidden:
        listed = ", ".join(str(path) for path in forbidden)
        raise ValidationError(f"Runtime mod contains build-only paths: {listed}")


def check_frontend_contract(root: Path) -> None:
    mod_root = root / MOD_ROOT
    apply_text_contracts(
        (
            TextContract(
                mod_root / "ChuuniSociety.modinfo",
                required=(
                    'id="4873eb62-8ccc-4574-b784-dda455e74e68"',
                    "<GameCoreInUse>Expansion2</GameCoreInUse>",
                    'criteria="ChuuniExpansion2"',
                    "Data/Config.sql",
                    "Data/Colors.xml",
                    "Data/Core.sql",
                    "Data/StageCombat.sql",
                    "Data/Chimera.sql",
                    "Data/DistrictBuilding.sql",
                    "Scripts/ChuuniGameplay.lua",
                    "UI/ChuuniStatusHUD.xml",
                    "UI/ChuuniStatusHUD.lua",
                    "AddUserInterfaces",
                    "AddGameplayScripts",
                    "ChuuniSociety.dep",
                    "Platforms/Windows/BLPs/ChuuniUITextureV1.blp",
                    "Platforms/Windows/BLPs/ChuuniLeaderFallbacks.blp",
                    "Text/Chuuni_zh_Hans_CN.sql",
                    "Icons/ChuuniIcons.sql",
                ),
                forbidden=(
                    "1B28771A-C749-434B-9053-D1380C553DE9",
                ),
            ),
            TextContract(
                mod_root / "Data/Config.sql",
                required=(
                    "CIVILIZATION_CHUUNI_SOCIETY",
                    "LEADER_RIKKA_TAKANASHI",
                    "Players:Expansion2_Players",
                    "ICON_CIVILIZATION_CHUUNI_SOCIETY",
                    "ICON_LEADER_RIKKA_TAKANASHI",
                ),
                forbidden=("RESOURCE_CHUUNI_VALUE",),
            ),
            TextContract(
                mod_root / "Text/Chuuni_zh_Hans_CN.sql",
                required=(
                    "LOC_CIVILIZATION_CHUUNI_SOCIETY_NAME",
                    "LOC_LEADER_RIKKA_TAKANASHI_NAME",
                    "LOC_TRAIT_CIVILIZATION_CHUUNI_SOCIETY_NAME",
                    "LOC_TRAIT_LEADER_RIKKA_TAKANASHI_NAME",
                    "LOC_DISTRICT_CHUUNI_SOCIETY_NAME",
                    "LOC_BUILDING_CLUB_MAGIC_CIRCLE_NAME",
                    "LOC_CHUUNI_FANTASY_COMBAT_STAGE_1_PREVIEW",
                    "LOC_CHUUNI_FANTASY_COMBAT_STAGE_2_PREVIEW",
                    "LOC_CHUUNI_FANTASY_COMBAT_STAGE_3_PREVIEW",
                    "LOC_CHUUNI_STATUS_STAGE_4_NAME",
                    "LOC_CHUUNI_STATUS_UNMET_RELIGION",
                    "LOC_CHUUNI_STATUS_BUTTON_TOOLTIP",
                    "LOC_CHUUNI_STATUS_POPUP_TITLE",
                    "LOC_CHUUNI_STATUS_CLOSE",
                    "LOC_GOVERNOR_CHIMERA_NAME",
                    "LOC_GOVERNOR_CHIMERA_TITLE",
                    "LOC_GOVERNOR_CHIMERA_SHORT_TITLE",
                    "LOC_GOVERNOR_CHIMERA_DESCRIPTION",
                    "LOC_GOVERNOR_PROMOTION_CHIMERA_BASE_NAME",
                    "LOC_GOVERNOR_PROMOTION_CHIMERA_BASE_DESCRIPTION",
                ),
                forbidden=("LOC_RESOURCE_CHUUNI_VALUE",),
            ),
            TextContract(
                mod_root / "Icons/ChuuniIcons.sql",
                required=(
                    "ICON_CIVILIZATION_CHUUNI_SOCIETY",
                    "CIVILIZATION_CHUUNI_SOCIETY",
                    "ICON_LEADER_RIKKA_TAKANASHI",
                    "ICON_CIVILIZATION_JAPAN",
                    "ICON_LEADER_HOJO",
                    "ICON_DISTRICT_CHUUNI_SOCIETY",
                    "ICON_BUILDING_CLUB_MAGIC_CIRCLE",
                    "ICON_CHUUNI_VALUE",
                ),
                forbidden=("RESOURCE_CHUUNI_VALUE", "ICON_RESOURCE_CHUUNI_VALUE"),
            ),
            TextContract(
                mod_root / "Data/Core.sql",
                required=(
                    "CIVILIZATION_CHUUNI_SOCIETY",
                    "LEADER_RIKKA_TAKANASHI",
                    "TRAIT_CIVILIZATION_CHUUNI_SOCIETY",
                    "TRAIT_LEADER_RIKKA_TAKANASHI",
                    "'CHUUNI_VALUE_PER_DISTRICT', 1",
                    "'CHUUNI_VALUE_PER_BUILDING', 1",
                    "'CHUUNI_STAGE_1_THRESHOLD', 1",
                    "'CHUUNI_STAGE_2_THRESHOLD', 20",
                    "'CHUUNI_STAGE_3_THRESHOLD', 50",
                    "'CHUUNI_STAGE_4_THRESHOLD', 100",
                    "CHUUNI_RIKKA_COASTAL_CITY_AMENITIES",
                    "MODIFIER_PLAYER_CITIES_ADJUST_TRAIT_AMENITY",
                    "'Amount', 2",
                ),
                forbidden=("RESOURCE_CHUUNI_VALUE", "RESOURCECLASS_STRATEGIC"),
            ),
            TextContract(
                mod_root / "Scripts/ChuuniGameplay.lua",
                required=(
                    "function GetChuuniValue",
                    "function ChangeChuuniValue",
                    "function UpdateChuuniStage",
                    'CHUUNI_VALUE = "CHUUNI_VALUE"',
                    "CHUUNI_LAST_VALUE_TICK_TURN",
                    "CHUUNI_STAGE_1_COMBAT_ATTACHED",
                    "CHUUNI_STAGE_2_COMBAT_ATTACHED",
                    "CHUUNI_STAGE_3_COMBAT_ATTACHED",
                    "CHUUNI_CHIMERA_UNLOCKED",
                    "CHUUNI_CHIMERA_TITLE_ATTACHED",
                    "CHUUNI_CHIMERA_GOVERNOR_POINT",
                    "CHUUNI_FIRST_COASTAL_CITY_FOUNDED",
                    "GetReligionTypeCreated",
                    "Events.PlayerTurnActivated.Add",
                    "Events.ReligionFounded.Add",
                    "Events.CityAddedToMap.Add",
                    "ChangeChuuniValue(playerID, 5)",
                    "AttachModifierByID(CHUUNI_COASTAL_AMENITY_MODIFIER)",
                    "player:AttachModifierByID(modifierID)",
                    "AttachModifierByID(CHUUNI_CHIMERA_GOVERNOR_POINT)",
                    "LuaEvents.ChuuniStatusChanged",
                ),
                forbidden=(
                    "RESOURCE_CHUUNI_VALUE",
                    "CHUUNI_RESOURCE_INDEX",
                    "CHUUNI_LAST_RESOURCE_TICK_TURN",
                    "GetResources()",
                    "GetResourceAmount",
                    "ChangeResourceAmount",
                    "tonumber(player:GetProperty(",
                ),
            ),
            TextContract(
                mod_root / "UI/ChuuniStatusHUD.xml",
                required=(
                    'Instance Name="ChuuniStatusButtonInstance"',
                    'Offset="292,72"',
                    "ChuuniStatusRoot",
                    "ChuuniStatusButton",
                    "ChuuniStatusIcon",
                    "ChuuniValueBadge",
                    "ChuuniValueText",
                ),
                forbidden=(
                    "ChuuniStatusContainer",
                    "ChuuniValueLabel",
                    "ChuuniStageLabel",
                    "ChuuniNextThresholdLabel",
                ),
            ),
            TextContract(
                mod_root / "UI/ChuuniStatusHUD.lua",
                required=(
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
                    'include("PopupDialog")',
                    "PopupDialogInGame:new",
                    "GOVERNOR_CHIMERA",
                    "PlayerOperations.APPOINT_GOVERNOR",
                    "PlayerOperations.PARAM_GOVERNOR_TYPE",
                    "UI.RequestPlayerOperation",
                    "HasGovernor",
                    "GetGovernorPointsSpent",
                    "BuildPopupText",
                    "OpenChuuniPopup",
                    "Mouse.eLClick",
                    "Mouse.eMouseEnter",
                    "LuaEvents.ChuuniStatusChanged.Add",
                    "Events.GameCoreEventPublishComplete.Add",
                    "Events.LocalPlayerChanged.Add",
                    "Events.LoadGameViewStateDone.Add(OnLoadGameViewStateDone)",
                    "if AttachStatusButton() then",
                    "m_buttonInstance.ChuuniStatusRoot:SetHide",
                    "m_buttonInstance.ChuuniStatusButton:SetToolTipString",
                    "m_buttonInstance.ChuuniValueText:SetText",
                    "LOC_CHUUNI_STATUS_UNMET_RELIGION",
                    "[ChuuniStatusHUD]",
                    '"hidden player="',
                    '"visible player="',
                ),
                forbidden=(
                    "RESOURCE_CHUUNI_VALUE",
                    "GetResources",
                    "GetResourceAmount",
                    "ChuuniStatusContainer",
                    "tonumber(player:GetProperty(",
                ),
            ),
            TextContract(
                mod_root / "Data/Chimera.sql",
                required=(
                    "'GOVERNOR_CHIMERA', 'KIND_GOVERNOR'",
                    "'GOVERNOR_PROMOTION_CHIMERA_BASE', 'KIND_GOVERNOR_PROMOTION'",
                    "INSERT INTO Governors",
                    "TransitionStrength",
                    "500",
                    "GovernorNormal_Builder",
                    "GovernorSelected_Builder",
                    "INSERT INTO Governors_XP2",
                    "AssignToMajor",
                    "INSERT INTO GovernorPromotions",
                    "BaseAbility",
                    "INSERT INTO GovernorPromotionSets",
                    "CHUUNI_CHIMERA_GOVERNOR_POINT",
                    "MODIFIER_PLAYER_ADJUST_GOVERNOR_POINTS",
                    "'Delta', 1",
                ),
            ),
            TextContract(
                mod_root / "Data/StageCombat.sql",
                required=(
                    "CHUUNI_FANTASY_COMBAT_STAGE_1",
                    "CHUUNI_FANTASY_COMBAT_STAGE_2",
                    "CHUUNI_FANTASY_COMBAT_STAGE_3",
                    "MODIFIER_PLAYER_UNITS_ADJUST_COMBAT_STRENGTH",
                    "Permanent",
                    "ModifierStrings",
                    "'Preview'",
                    "('CHUUNI_FANTASY_COMBAT_STAGE_1', 'Amount', 3)",
                    "('CHUUNI_FANTASY_COMBAT_STAGE_2', 'Amount', 2)",
                    "('CHUUNI_FANTASY_COMBAT_STAGE_3', 'Amount', 3)",
                ),
                forbidden=(
                    "Requirements",
                    "RequirementArguments",
                    "RequirementSetRequirements",
                    "TraitModifiers",
                    "RESOURCE_CHUUNI_VALUE",
                    "REQUIREMENT_PLAYER_HAS_RESOURCE_OWNED",
                ),
            ),
            TextContract(
                mod_root / "Data/DistrictBuilding.sql",
                required=(
                    "'DISTRICT_CHUUNI_SOCIETY', 'DISTRICT_HOLY_SITE'",
                    "'BUILDING_CLUB_MAGIC_CIRCLE', 'BUILDING_SHRINE'",
                    "'DISTRICT_CHUUNI_SOCIETY', 'GREAT_PERSON_CLASS_PROPHET', 2",
                    "'BUILDING_CLUB_MAGIC_CIRCLE', 'GREAT_PERSON_CLASS_PROPHET', 1",
                    "'BUILDING_CLUB_MAGIC_CIRCLE', 'YIELD_FAITH', 2",
                    "Entertainment = 1",
                    "Maintenance = 0",
                    "Unit_BuildingPrereqs",
                    "UNIT_MISSIONARY",
                    "CHUUNI_SOCIETY_CAMPUS_FAITH_",
                    "CHUUNI_SOCIETY_WONDER_FAITH",
                    "AdjacentWonder",
                    "DISTRICT_ENTERTAINMENT_COMPLEX",
                    "DISTRICT_WATER_ENTERTAINMENT_COMPLEX",
                ),
                forbidden=(
                    "CHUUNI_SOCIETY_ADJACENT_CAMPUS_FAITH",
                    "MODIFIER_PLAYER_DISTRICTS_ADJUST_YIELD_CHANGE",
                    "CHUUNI_SOCIETY_TO_GOLD",
                    "CHUUNI_SOCIETY_TO_FAITH",
                ),
            ),
        )
    )


def run(root: Path) -> None:
    check_runtime_layout(root)
    check_frontend_contract(root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="repository root")
    args = parser.parse_args(argv)
    try:
        run(args.root.resolve())
    except ValidationError as error:
        print(f"[ChuuniSociety] static validation failed: {error}", file=sys.stderr)
        return 1
    print("[ChuuniSociety] static checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
