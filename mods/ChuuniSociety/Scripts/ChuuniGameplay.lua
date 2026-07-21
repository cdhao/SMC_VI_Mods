-- Core progression state for the Far East Magic Nap Society.

local CIVILIZATION_CHUUNI_SOCIETY = "CIVILIZATION_CHUUNI_SOCIETY"
local DISTRICT_CHUUNI_SOCIETY = "DISTRICT_CHUUNI_SOCIETY"
local BUILDING_CLUB_MAGIC_CIRCLE = "BUILDING_CLUB_MAGIC_CIRCLE"
local TERRAIN_COAST = "TERRAIN_COAST"

local CHUUNI_VALUE_CAP = 100
local CHUUNI_VALUE = "CHUUNI_VALUE"
local CHUUNI_LAST_VALUE_TICK_TURN = "CHUUNI_LAST_VALUE_TICK_TURN"
local CHUUNI_STAGE = "CHUUNI_STAGE"
local CHUUNI_STAGE_1_UNLOCKED = "CHUUNI_STAGE_1_UNLOCKED"
local CHUUNI_STAGE_2_UNLOCKED = "CHUUNI_STAGE_2_UNLOCKED"
local CHUUNI_STAGE_3_UNLOCKED = "CHUUNI_STAGE_3_UNLOCKED"
local CHUUNI_STAGE_4_UNLOCKED = "CHUUNI_STAGE_4_UNLOCKED"
local CHUUNI_STAGE_1_COMBAT_ATTACHED = "CHUUNI_STAGE_1_COMBAT_ATTACHED"
local CHUUNI_STAGE_2_COMBAT_ATTACHED = "CHUUNI_STAGE_2_COMBAT_ATTACHED"
local CHUUNI_STAGE_3_COMBAT_ATTACHED = "CHUUNI_STAGE_3_COMBAT_ATTACHED"
local CHUUNI_FIRST_COASTAL_CITY_FOUNDED = "CHUUNI_FIRST_COASTAL_CITY_FOUNDED"
local CHUUNI_COASTAL_AMENITY_ATTACHED = "CHUUNI_COASTAL_AMENITY_ATTACHED"
local CHUUNI_COASTAL_AMENITY_MODIFIER = "CHUUNI_RIKKA_COASTAL_CITY_AMENITIES"

local STAGE_MODIFIERS = {
    [1] = "CHUUNI_FANTASY_COMBAT_STAGE_1",
    [2] = "CHUUNI_FANTASY_COMBAT_STAGE_2",
    [3] = "CHUUNI_FANTASY_COMBAT_STAGE_3",
}

local STAGE_ATTACHED_PROPERTIES = {
    [1] = CHUUNI_STAGE_1_COMBAT_ATTACHED,
    [2] = CHUUNI_STAGE_2_COMBAT_ATTACHED,
    [3] = CHUUNI_STAGE_3_COMBAT_ATTACHED,
}

local STAGE_THRESHOLDS = {
    tonumber(GameInfo.GlobalParameters["CHUUNI_STAGE_1_THRESHOLD"].Value) or 1,
    tonumber(GameInfo.GlobalParameters["CHUUNI_STAGE_2_THRESHOLD"].Value) or 20,
    tonumber(GameInfo.GlobalParameters["CHUUNI_STAGE_3_THRESHOLD"].Value) or 50,
    tonumber(GameInfo.GlobalParameters["CHUUNI_STAGE_4_THRESHOLD"].Value) or 100,
}

local VALUE_PER_DISTRICT = tonumber(
    GameInfo.GlobalParameters["CHUUNI_VALUE_PER_DISTRICT"].Value
) or 1
local VALUE_PER_BUILDING = tonumber(
    GameInfo.GlobalParameters["CHUUNI_VALUE_PER_BUILDING"].Value
) or 1

local CHUUNI_DISTRICT_INDEX = GameInfo.Districts[DISTRICT_CHUUNI_SOCIETY].Index
local MAGIC_CIRCLE_INDEX = GameInfo.Buildings[BUILDING_CLUB_MAGIC_CIRCLE].Index
local COAST_TERRAIN_INDEX = GameInfo.Terrains[TERRAIN_COAST].Index

local function Log(message)
    print("[ChuuniSociety] " .. tostring(message))
end

local function GetPlayer(playerID)
    if playerID == nil or Players == nil then
        return nil
    end
    return Players[playerID]
end

local function IsChuuniPlayer(playerID)
    local player = GetPlayer(playerID)
    local config = PlayerConfigurations ~= nil and PlayerConfigurations[playerID] or nil
    return player ~= nil
        and player:IsAlive()
        and config ~= nil
        and config:GetCivilizationTypeName() == CIVILIZATION_CHUUNI_SOCIETY
end

local function HasFoundedReligion(player)
    if player == nil or player.GetReligion == nil then
        return false
    end
    local religion = player:GetReligion()
    if religion == nil or religion.GetReligionTypeCreated == nil then
        return false
    end
    return (tonumber(religion:GetReligionTypeCreated()) or -1) >= 0
end

local function PublishChuuniStatus(playerID)
    if LuaEvents == nil or LuaEvents.ChuuniStatusChanged == nil then
        return
    end
    local player = GetPlayer(playerID)
    local storedStage = player ~= nil and player:GetProperty(CHUUNI_STAGE) or nil
    LuaEvents.ChuuniStatusChanged(
        playerID,
        GetChuuniValue(playerID),
        tonumber(storedStage) or 0
    )
end

local function SendStatus(playerID, localizationKey)
    local text = localizationKey
    if Locale ~= nil and Locale.Lookup ~= nil then
        text = Locale.Lookup(localizationKey)
    end
    if NotificationManager ~= nil and NotificationManager.SendNotification ~= nil
        and NotificationTypes ~= nil and NotificationTypes.USER_DEFINED_4 ~= nil then
        NotificationManager.SendNotification(
            playerID,
            NotificationTypes.USER_DEFINED_4,
            text,
            nil
        )
    end
    Log(text)
end

function GetChuuniValue(playerID)
    local player = GetPlayer(playerID)
    if player == nil then
        return 0
    end
    local storedValue = player:GetProperty(CHUUNI_VALUE)
    local value = tonumber(storedValue) or 0
    return math.max(0, math.min(CHUUNI_VALUE_CAP, value))
end

function ChangeChuuniValue(playerID, amount)
    local player = GetPlayer(playerID)
    local gain = tonumber(amount) or 0
    if not IsChuuniPlayer(playerID) or player == nil or gain <= 0 then
        return GetChuuniValue(playerID)
    end

    local currentValue = GetChuuniValue(playerID)
    local nextValue = math.min(CHUUNI_VALUE_CAP, currentValue + math.floor(gain))
    if nextValue ~= currentValue then
        player:SetProperty(CHUUNI_VALUE, nextValue)
        PublishChuuniStatus(playerID)
    end
    return nextValue
end

local function EnsureStageCombatModifier(player, stage)
    local modifierID = STAGE_MODIFIERS[stage]
    local attachedProperty = STAGE_ATTACHED_PROPERTIES[stage]
    if modifierID == nil or attachedProperty == nil then
        return
    end
    if player:GetProperty(attachedProperty) == 1 then
        return
    end
    player:AttachModifierByID(modifierID)
    player:SetProperty(attachedProperty, 1)
end

local function UnlockStage(player, playerID, stage, propertyName, localizationKey)
    if player:GetProperty(propertyName) ~= 1 then
        EnsureStageCombatModifier(player, stage)
        player:SetProperty(propertyName, 1)
        player:SetProperty(CHUUNI_STAGE, stage)
        SendStatus(playerID, localizationKey)
        PublishChuuniStatus(playerID)
    end
    return stage
end

function UpdateChuuniStage(playerID)
    if not IsChuuniPlayer(playerID) then
        return 0
    end

    local player = GetPlayer(playerID)
    local value = GetChuuniValue(playerID)
    local storedStage = player:GetProperty(CHUUNI_STAGE)
    local stage = tonumber(storedStage) or 0

    if stage < 1 and value >= STAGE_THRESHOLDS[1] then
        stage = UnlockStage(player, playerID, 1, CHUUNI_STAGE_1_UNLOCKED, "LOC_CHUUNI_STAGE_1_UNLOCKED")
    end
    if stage >= 1 and stage < 2 and HasFoundedReligion(player)
        and value >= STAGE_THRESHOLDS[2] then
        stage = UnlockStage(player, playerID, 2, CHUUNI_STAGE_2_UNLOCKED, "LOC_CHUUNI_STAGE_2_UNLOCKED")
    end
    if stage >= 2 and stage < 3 and HasFoundedReligion(player)
        and value >= STAGE_THRESHOLDS[3] then
        stage = UnlockStage(player, playerID, 3, CHUUNI_STAGE_3_UNLOCKED, "LOC_CHUUNI_STAGE_3_UNLOCKED")
    end
    if stage >= 3 and stage < 4 and HasFoundedReligion(player)
        and value >= STAGE_THRESHOLDS[4] then
        stage = UnlockStage(player, playerID, 4, CHUUNI_STAGE_4_UNLOCKED, "LOC_CHUUNI_STAGE_4_UNLOCKED")
    end

    player:SetProperty(CHUUNI_STAGE, stage)
    PublishChuuniStatus(playerID)
    return stage
end

local function CountProgressionSources(player)
    local districtCount = 0
    local buildingCount = 0

    local districts = player:GetDistricts()
    if districts ~= nil then
        for _, district in districts:Members() do
            if district ~= nil and district:IsComplete()
                and district:GetType() == CHUUNI_DISTRICT_INDEX then
                districtCount = districtCount + 1
            end
        end
    end

    local cities = player:GetCities()
    if cities ~= nil then
        for _, city in cities:Members() do
            local buildings = city:GetBuildings()
            if buildings ~= nil and buildings:HasBuilding(MAGIC_CIRCLE_INDEX) then
                buildingCount = buildingCount + 1
            end
        end
    end

    return districtCount, buildingCount
end

local function OnPlayerTurnActivated(playerID, isFirstTime)
    if isFirstTime == false or not IsChuuniPlayer(playerID) then
        return
    end

    local player = GetPlayer(playerID)
    local currentTurn = Game.GetCurrentGameTurn()
    local lastValueTickTurn = player:GetProperty(CHUUNI_LAST_VALUE_TICK_TURN)
    if tonumber(lastValueTickTurn) == currentTurn then
        return
    end
    player:SetProperty(CHUUNI_LAST_VALUE_TICK_TURN, currentTurn)

    local districtCount, buildingCount = CountProgressionSources(player)
    ChangeChuuniValue(
        playerID,
        districtCount * VALUE_PER_DISTRICT + buildingCount * VALUE_PER_BUILDING
    )
    UpdateChuuniStage(playerID)
end

local function OnReligionFounded(playerID)
    UpdateChuuniStage(playerID)
end

local function GetCity(playerID, cityID)
    if CityManager ~= nil and CityManager.GetCity ~= nil then
        local city = CityManager.GetCity(playerID, cityID)
        if city ~= nil then
            return city
        end
    end
    local player = GetPlayer(playerID)
    return player ~= nil and player:GetCities():FindID(cityID) or nil
end

local function IsCoastalCity(cityX, cityY)
    for direction = 0, DirectionTypes.NUM_DIRECTION_TYPES - 1 do
        local adjacentPlot = Map.GetAdjacentPlot(cityX, cityY, direction)
        if adjacentPlot ~= nil and adjacentPlot:GetTerrainType() == COAST_TERRAIN_INDEX then
            return true
        end
    end
    return false
end

local function OnCityAddedToMap(playerID, cityID, cityX, cityY)
    if not IsChuuniPlayer(playerID) then
        return
    end

    local player = GetPlayer(playerID)
    if player:GetProperty(CHUUNI_FIRST_COASTAL_CITY_FOUNDED) == 1 then
        return
    end

    local city = GetCity(playerID, cityID)
    if city == nil or city:GetOwner() ~= playerID or city:GetOriginalOwner() ~= playerID
        or not IsCoastalCity(cityX, cityY) then
        return
    end

    player:SetProperty(CHUUNI_FIRST_COASTAL_CITY_FOUNDED, 1)
    if player:GetProperty(CHUUNI_COASTAL_AMENITY_ATTACHED) ~= 1 then
        player:AttachModifierByID(CHUUNI_COASTAL_AMENITY_MODIFIER)
        player:SetProperty(CHUUNI_COASTAL_AMENITY_ATTACHED, 1)
    end
    ChangeChuuniValue(playerID, 5)
    UpdateChuuniStage(playerID)
    SendStatus(playerID, "LOC_CHUUNI_FIRST_COASTAL_CITY")
end

Events.PlayerTurnActivated.Add(OnPlayerTurnActivated)
Events.ReligionFounded.Add(OnReligionFounded)
Events.CityAddedToMap.Add(OnCityAddedToMap)

Log("Chuuni gameplay progression initialized")
