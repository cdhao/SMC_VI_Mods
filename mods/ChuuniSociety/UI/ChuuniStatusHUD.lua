-- Compact Chuuni Value button and native in-game status popup.

include("PopupDialog")

local CIVILIZATION_CHUUNI_SOCIETY = "CIVILIZATION_CHUUNI_SOCIETY"
local CHUUNI_VALUE = "CHUUNI_VALUE"
local CHUUNI_STAGE = "CHUUNI_STAGE"
local GOVERNOR_CHIMERA = "GOVERNOR_CHIMERA"
local CHUUNI_VALUE_CAP = 100

local STAGE_THRESHOLDS = { 1, 20, 50, 100 }
local STAGE_NAME_KEYS = {
    "LOC_CHUUNI_STATUS_STAGE_0_NAME",
    "LOC_CHUUNI_STATUS_STAGE_1_NAME",
    "LOC_CHUUNI_STATUS_STAGE_2_NAME",
    "LOC_CHUUNI_STATUS_STAGE_3_NAME",
    "LOC_CHUUNI_STATUS_STAGE_4_NAME",
}
local STAGE_ABILITY_KEYS = {
    "LOC_CHUUNI_STATUS_STAGE_0_ABILITY",
    "LOC_CHUUNI_STATUS_STAGE_1_ABILITY",
    "LOC_CHUUNI_STATUS_STAGE_2_ABILITY",
    "LOC_CHUUNI_STATUS_STAGE_3_ABILITY",
    "LOC_CHUUNI_STATUS_STAGE_4_ABILITY",
}

local m_buttonInstance = {}
local m_chimeraAppointmentPending = false
local lastDiagnostic = nil

local function TraceOnce(message)
    if message ~= lastDiagnostic then
        print("[ChuuniStatusHUD] " .. message)
        lastDiagnostic = message
    end
end

local function Lookup(key, ...)
    if Locale ~= nil and Locale.Lookup ~= nil then
        return Locale.Lookup(key, ...)
    end
    return key
end

local function GetPropertyNumber(player, propertyName, defaultValue)
    local storedValue = player:GetProperty(propertyName)
    local numericValue = tonumber(storedValue)
    if numericValue == nil then
        return defaultValue
    end
    return numericValue
end

local function HasFoundedReligion(player)
    if player == nil or player.GetReligion == nil then
        return false
    end
    local religion = player:GetReligion()
    if religion == nil or religion.GetReligionTypeCreated == nil then
        return false
    end
    local religionType = religion:GetReligionTypeCreated()
    return (tonumber(religionType) or -1) >= 0
end

local function GetLocalChuuniPlayer()
    local playerID = Game.GetLocalPlayer()
    if playerID == nil or playerID < 0 or Players == nil then
        return nil, -1
    end

    local player = Players[playerID]
    local config = PlayerConfigurations ~= nil and PlayerConfigurations[playerID] or nil
    if player == nil or not player:IsAlive() or config == nil
        or config:GetCivilizationTypeName() ~= CIVILIZATION_CHUUNI_SOCIETY then
        return nil, playerID
    end
    return player, playerID
end

local function GetStatusModel(player)
    local value = math.max(0, math.min(
        CHUUNI_VALUE_CAP,
        GetPropertyNumber(player, CHUUNI_VALUE, 0)
    ))
    local stage = math.max(0, math.min(4, GetPropertyNumber(player, CHUUNI_STAGE, 0)))
    local foundedReligion = HasFoundedReligion(player)
    local nextThreshold = stage < 4 and STAGE_THRESHOLDS[stage + 1] or nil

    return {
        value = value,
        stage = stage,
        foundedReligion = foundedReligion,
        nextThreshold = nextThreshold,
        missingValue = nextThreshold ~= nil and math.max(0, nextThreshold - value) or 0,
        nextNeedsReligion = stage >= 1 and stage < 4,
    }
end

local function EnsureChimeraAppointed(player, playerID, stage)
    if stage < 1 or m_chimeraAppointmentPending then
        return
    end

    local governorDefinition = GameInfo.Governors[GOVERNOR_CHIMERA]
    local playerGovernors = player:GetGovernors()
    if governorDefinition == nil or playerGovernors == nil then
        return
    end
    if playerGovernors:HasGovernor(governorDefinition.Hash) then
        m_chimeraAppointmentPending = false
        return
    end

    local points = playerGovernors:GetGovernorPoints()
    local pointsSpent = playerGovernors:GetGovernorPointsSpent()
    if points - pointsSpent < 1 then
        TraceOnce("Chimera waiting for dedicated Governor point")
        return
    end

    local parameters = {}
    parameters[PlayerOperations.PARAM_GOVERNOR_TYPE] = governorDefinition.Index
    m_chimeraAppointmentPending = true
    UI.RequestPlayerOperation(
        playerID,
        PlayerOperations.APPOINT_GOVERNOR,
        parameters
    )
    print("[ChuuniStatusHUD] requested free Chimera appointment")
end

local function BuildStageOverview(status)
    local lines = {}
    for stage = 1, 4 do
        local markerKey = "LOC_CHUUNI_STATUS_STAGE_LOCKED"
        if stage < status.stage then
            markerKey = "LOC_CHUUNI_STATUS_STAGE_UNLOCKED"
        elseif stage == status.stage then
            markerKey = "LOC_CHUUNI_STATUS_STAGE_CURRENT"
        end
        table.insert(lines, Lookup(
            "LOC_CHUUNI_STATUS_STAGE_OVERVIEW_LINE",
            Lookup(markerKey),
            Lookup(STAGE_NAME_KEYS[stage + 1]),
            STAGE_THRESHOLDS[stage],
            Lookup(STAGE_ABILITY_KEYS[stage + 1])
        ))
    end
    return table.concat(lines, "[NEWLINE]")
end

local function BuildButtonTooltip(status)
    local lines = {
        Lookup("LOC_CHUUNI_STATUS_BUTTON_TOOLTIP", status.value),
        Lookup("LOC_CHUUNI_STATUS_STAGE_FORMAT", Lookup(STAGE_NAME_KEYS[status.stage + 1])),
    }
    if status.nextThreshold ~= nil then
        table.insert(lines, Lookup("LOC_CHUUNI_STATUS_NEXT_FORMAT", status.nextThreshold))
    else
        table.insert(lines, Lookup("LOC_CHUUNI_STATUS_MAX_STAGE"))
    end
    return table.concat(lines, "[NEWLINE]")
end

local function BuildPopupText(status)
    local lines = {
        Lookup("LOC_CHUUNI_STATUS_CURRENT_VALUE", status.value),
        Lookup("LOC_CHUUNI_STATUS_CURRENT_STAGE", Lookup(STAGE_NAME_KEYS[status.stage + 1])),
        Lookup("LOC_CHUUNI_STATUS_CURRENT_ABILITY"),
        Lookup(STAGE_ABILITY_KEYS[status.stage + 1]),
    }

    if status.stage < 4 then
        table.insert(lines, "")
        table.insert(lines, Lookup(
            "LOC_CHUUNI_STATUS_NEXT_STAGE",
            Lookup(STAGE_NAME_KEYS[status.stage + 2])
        ))
        table.insert(lines, Lookup("LOC_CHUUNI_STATUS_REQUIRED_VALUE", status.nextThreshold))
        if status.missingValue > 0 then
            table.insert(lines, Lookup("LOC_CHUUNI_STATUS_UNMET_VALUE", status.missingValue))
        end
        if status.nextNeedsReligion then
            local religionKey = status.foundedReligion
                and "LOC_CHUUNI_STATUS_RELIGION_MET"
                or "LOC_CHUUNI_STATUS_UNMET_RELIGION"
            table.insert(lines, Lookup(religionKey))
        end
    else
        table.insert(lines, "")
        table.insert(lines, Lookup("LOC_CHUUNI_STATUS_MAX_STAGE"))
    end

    table.insert(lines, "")
    table.insert(lines, Lookup("LOC_CHUUNI_STATUS_STAGE_OVERVIEW"))
    table.insert(lines, BuildStageOverview(status))
    return table.concat(lines, "[NEWLINE]")
end

local function OpenChuuniPopup()
    local player = GetLocalChuuniPlayer()
    if player == nil then
        return
    end

    local status = GetStatusModel(player)
    local popupDialog = PopupDialogInGame:new("ChuuniStatusPopup")
    popupDialog:AddTitle(Lookup("LOC_CHUUNI_STATUS_POPUP_TITLE"))
    popupDialog:AddText(BuildPopupText(status))
    local selectedUnit = UI.GetHeadSelectedUnit()
    if status.stage >= 1 and selectedUnit ~= nil
        and selectedUnit:GetOwner() == Game.GetLocalPlayer() then
        popupDialog:AddCustomButton(
            Lookup("LOC_CHUUNI_TELEPORT_NEAREST"),
            function()
                local parameters = {}
                parameters.OnStart = "ChuuniTeleport"
                parameters.UnitID = selectedUnit:GetID()
                UI.RequestPlayerOperation(
                    Game.GetLocalPlayer(),
                    PlayerOperations.EXECUTE_SCRIPT,
                    parameters
                )
            end
        )
    end
    popupDialog:AddConfirmButton(Lookup("LOC_CHUUNI_STATUS_CLOSE"), function() end)
    popupDialog:Open()
end

local function Refresh()
    if m_buttonInstance.ChuuniStatusRoot == nil then
        return
    end

    local player, playerID = GetLocalChuuniPlayer()
    if player == nil then
        m_buttonInstance.ChuuniStatusRoot:SetHide(true)
        local config = playerID >= 0 and PlayerConfigurations ~= nil
            and PlayerConfigurations[playerID] or nil
        local civilizationType = config ~= nil
            and config:GetCivilizationTypeName() or "<none>"
        TraceOnce(
            "hidden player=" .. tostring(playerID)
            .. " civilization=" .. tostring(civilizationType)
        )
        return
    end

    local status = GetStatusModel(player)
    EnsureChimeraAppointed(player, playerID, status.stage)
    m_buttonInstance.ChuuniValueText:SetText(tostring(status.value))
    m_buttonInstance.ChuuniStatusButton:SetToolTipString(BuildButtonTooltip(status))
    m_buttonInstance.ChuuniStatusRoot:SetHide(false)
    TraceOnce(
        "visible player=" .. tostring(playerID)
        .. " value=" .. tostring(status.value)
        .. " stage=" .. tostring(status.stage)
    )
end

local function OnChuuniStatusChanged(playerID)
    if playerID == Game.GetLocalPlayer() then
        Refresh()
    end
end

local function OnPlayerTurnActivated(playerID)
    if playerID == Game.GetLocalPlayer() then
        m_chimeraAppointmentPending = false
        Refresh()
    end
end

local function OnGovernorAppointed(playerID)
    if playerID == Game.GetLocalPlayer() then
        m_chimeraAppointmentPending = false
        Refresh()
    end
end

local function AttachStatusButton()
    if m_buttonInstance.ChuuniStatusButton ~= nil then
        return true
    end

    local topLevelHUD = ContextPtr:LookUpControl("/InGame/TopLevelHUD")
    if topLevelHUD == nil then
        TraceOnce("button mount failed: /InGame/TopLevelHUD unavailable")
        return false
    end

    ContextPtr:BuildInstanceForControl(
        "ChuuniStatusButtonInstance",
        m_buttonInstance,
        topLevelHUD
    )
    TraceOnce("button mounted target=/InGame/TopLevelHUD")
    m_buttonInstance.ChuuniStatusButton:RegisterCallback(Mouse.eLClick, OpenChuuniPopup)
    m_buttonInstance.ChuuniStatusButton:RegisterCallback(Mouse.eMouseEnter, Refresh)
    return true
end

local function OnLoadGameViewStateDone()
    if AttachStatusButton() then
        Refresh()
    end
end

LuaEvents.ChuuniStatusChanged.Add(OnChuuniStatusChanged)
Events.GameCoreEventPublishComplete.Add(Refresh)
Events.LocalPlayerChanged.Add(Refresh)
Events.PlayerTurnActivated.Add(OnPlayerTurnActivated)
Events.GovernorAppointed.Add(OnGovernorAppointed)
Events.LoadGameViewStateDone.Add(OnLoadGameViewStateDone)
