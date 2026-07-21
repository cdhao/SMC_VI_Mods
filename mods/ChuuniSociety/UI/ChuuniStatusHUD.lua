-- Compact status panel for Chuuni Value progression.

local CIVILIZATION_CHUUNI_SOCIETY = "CIVILIZATION_CHUUNI_SOCIETY"
local RESOURCE_CHUUNI_VALUE = "RESOURCE_CHUUNI_VALUE"
local CHUUNI_STAGE = "CHUUNI_STAGE"
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

local resourceRow = GameInfo.Resources[RESOURCE_CHUUNI_VALUE]
local CHUUNI_RESOURCE_INDEX = resourceRow ~= nil and resourceRow.Index or -1

local function Lookup(key, ...)
    if Locale ~= nil and Locale.Lookup ~= nil then
        return Locale.Lookup(key, ...)
    end
    return key
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

local function GetStatus(player)
    local value = 0
    local resources = player:GetResources()
    if resources ~= nil and CHUUNI_RESOURCE_INDEX >= 0 then
        local storedValue = resources:GetResourceAmount(CHUUNI_RESOURCE_INDEX)
        value = math.max(0, math.min(CHUUNI_VALUE_CAP, tonumber(storedValue) or 0))
    end
    local storedStage = player:GetProperty(CHUUNI_STAGE)
    local stage = math.max(0, math.min(4, tonumber(storedStage) or 0))
    return value, stage
end

local function BuildTooltip(player, value, stage)
    local lines = {
        Lookup("LOC_CHUUNI_STATUS_VALUE_FORMAT", value),
        Lookup("LOC_CHUUNI_STATUS_STAGE_FORMAT", Lookup(STAGE_NAME_KEYS[stage + 1])),
        "",
        Lookup("LOC_CHUUNI_STATUS_ABILITY_TITLE"),
        Lookup(STAGE_ABILITY_KEYS[stage + 1]),
    }

    if stage < 4 then
        local nextThreshold = STAGE_THRESHOLDS[stage + 1]
        table.insert(lines, "")
        table.insert(lines, Lookup("LOC_CHUUNI_STATUS_UNMET_TITLE"))
        local unmet = false
        if value < nextThreshold then
            table.insert(lines, Lookup("LOC_CHUUNI_STATUS_UNMET_VALUE", nextThreshold - value))
            unmet = true
        end
        if stage >= 1 and not HasFoundedReligion(player) then
            table.insert(lines, Lookup("LOC_CHUUNI_STATUS_UNMET_RELIGION"))
            unmet = true
        end
        if not unmet then
            table.insert(lines, Lookup("LOC_CHUUNI_STATUS_ALL_MET"))
        end
    end

    return table.concat(lines, "[NEWLINE]")
end

local function Refresh()
    local player = GetLocalChuuniPlayer()
    if player == nil or CHUUNI_RESOURCE_INDEX < 0 then
        Controls.ChuuniStatusContainer:SetHide(true)
        return
    end

    local value, stage = GetStatus(player)
    Controls.ChuuniValueLabel:SetText(Lookup("LOC_CHUUNI_STATUS_VALUE_FORMAT", value))
    Controls.ChuuniStageLabel:SetText(
        Lookup("LOC_CHUUNI_STATUS_STAGE_FORMAT", Lookup(STAGE_NAME_KEYS[stage + 1]))
    )
    if stage < 4 then
        Controls.ChuuniNextThresholdLabel:SetText(
            Lookup("LOC_CHUUNI_STATUS_NEXT_FORMAT", STAGE_THRESHOLDS[stage + 1])
        )
    else
        Controls.ChuuniNextThresholdLabel:SetText(Lookup("LOC_CHUUNI_STATUS_MAX_STAGE"))
    end
    Controls.ChuuniStatusContainer:SetToolTipString(BuildTooltip(player, value, stage))
    Controls.ChuuniStatusContainer:SetHide(false)
end

local function OnChuuniStatusChanged(playerID)
    if playerID == Game.GetLocalPlayer() then
        Refresh()
    end
end

local function OnPlayerTurnActivated(playerID)
    if playerID == Game.GetLocalPlayer() then
        Refresh()
    end
end

LuaEvents.ChuuniStatusChanged.Add(OnChuuniStatusChanged)
Events.GameCoreEventPublishComplete.Add(Refresh)
Events.LocalPlayerChanged.Add(Refresh)
Events.PlayerTurnActivated.Add(OnPlayerTurnActivated)
Events.LoadGameViewStateDone.Add(Refresh)

Refresh()
