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
local CHUUNI_CHIMERA_UNLOCKED = "CHUUNI_CHIMERA_UNLOCKED"
local CHUUNI_CHIMERA_TITLE_ATTACHED = "CHUUNI_CHIMERA_TITLE_ATTACHED"
local CHUUNI_CHIMERA_FAITH_TIER = "CHUUNI_CHIMERA_FAITH_TIER"
local CHUUNI_CHIMERA_CULTURE_TIER = "CHUUNI_CHIMERA_CULTURE_TIER"
local CHUUNI_CHIMERA_SCIENCE_TIER = "CHUUNI_CHIMERA_SCIENCE_TIER"
local CHUUNI_FIRST_COASTAL_CITY_FOUNDED = "CHUUNI_FIRST_COASTAL_CITY_FOUNDED"
local CHUUNI_COASTAL_AMENITY_ATTACHED = "CHUUNI_COASTAL_AMENITY_ATTACHED"
local CHUUNI_COASTAL_AMENITY_MODIFIER = "CHUUNI_RIKKA_COASTAL_CITY_AMENITIES"
local CHUUNI_CHIMERA_GOVERNOR_POINT = "CHUUNI_CHIMERA_GOVERNOR_POINT"
local CHIMERA_REST_DAMAGE = "CHUUNI_CHIMERA_REST_DAMAGE"
local CHIMERA_REST_TURN = "CHUUNI_CHIMERA_REST_TURN"
local CHIMERA_REST_UNIT_TYPE = "CHUUNI_CHIMERA_REST_UNIT_TYPE"
local CHIMERA_REST_PLOT = "CHUUNI_CHIMERA_REST_PLOT"
local CHIMERA_REST_CITY = "CHUUNI_CHIMERA_REST_CITY"
local CHIMERA_REST_ELIGIBLE = "CHUUNI_CHIMERA_REST_ELIGIBLE"
local CHIMERA_COMBAT_ABILITY = "ABILITY_CHUUNI_CHIMERA_COMBAT"
local CHIMERA_MOBILITY_ABILITY = "ABILITY_CHUUNI_CHIMERA_MOBILITY"
local CHUUNI_TELEPORT_TURN = "CHUUNI_TELEPORT_TURN"

local CHIMERA_FAITH_MODIFIERS = {
    [1] = "CHUUNI_CHIMERA_FAITH_TIER_1",
    [2] = "CHUUNI_CHIMERA_FAITH_TIER_2",
    [3] = "CHUUNI_CHIMERA_FAITH_TIER_3",
    [4] = "CHUUNI_CHIMERA_FAITH_TIER_4",
    [5] = "CHUUNI_CHIMERA_FAITH_TIER_5",
    [6] = "CHUUNI_CHIMERA_FAITH_TIER_6",
    [7] = "CHUUNI_CHIMERA_FAITH_TIER_7",
    [8] = "CHUUNI_CHIMERA_FAITH_TIER_8",
    [9] = "CHUUNI_CHIMERA_FAITH_TIER_9",
    [10] = "CHUUNI_CHIMERA_FAITH_TIER_10",
}

local function BuildTierModifierTable(prefix)
    local modifiers = {}
    for tier = 1, 10 do
        modifiers[tier] = prefix .. tostring(tier)
    end
    return modifiers
end

local CHIMERA_CULTURE_MODIFIERS =
    BuildTierModifierTable("CHUUNI_CHIMERA_CULTURE_TIER_")
local CHIMERA_SCIENCE_MODIFIERS =
    BuildTierModifierTable("CHUUNI_CHIMERA_SCIENCE_TIER_")

local STAGE_MARKER_RESOURCE_TYPES = {
    [1] = "RESOURCE_CHUUNI_STAGE_MARKER_1",
    [2] = "RESOURCE_CHUUNI_STAGE_MARKER_2",
    [3] = "RESOURCE_CHUUNI_STAGE_MARKER_3",
    [4] = "RESOURCE_CHUUNI_STAGE_MARKER_4",
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
local CHIMERA_GOVERNOR_DEFINITION = GameInfo.Governors["GOVERNOR_CHIMERA"]
local STAGE_MARKER_RESOURCE_INDICES = {}
for stage, resourceType in pairs(STAGE_MARKER_RESOURCE_TYPES) do
    local resourceDefinition = GameInfo.Resources[resourceType]
    STAGE_MARKER_RESOURCE_INDICES[stage] =
        resourceDefinition ~= nil and resourceDefinition.Index or nil
end

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

local function GetStoredStage(player)
    if player == nil then
        return 0
    end
    local storedStage = player:GetProperty(CHUUNI_STAGE)
    return math.max(0, math.min(4, tonumber(storedStage) or 0))
end

local function EnsureChimeraYieldTier(
    playerID, propertyName, modifierIDs, minimumStage
)
    local player = GetPlayer(playerID)
    if player == nil or GetStoredStage(player) < minimumStage then
        return 0
    end
    local storedTier = player:GetProperty(propertyName)
    local attachedTier = math.max(0, math.min(10, tonumber(storedTier) or 0))
    local targetTier = math.min(10, math.floor(GetChuuniValue(playerID) / 10))
    for tier = attachedTier + 1, targetTier do
        local yieldModifierID = modifierIDs[tier]
        if yieldModifierID ~= nil then
            player:AttachModifierByID(yieldModifierID)
            player:SetProperty(propertyName, tier)
            attachedTier = tier
        end
    end
    return attachedTier
end

local function EnsureChimeraYieldTiers(playerID)
    EnsureChimeraYieldTier(
        playerID, CHUUNI_CHIMERA_FAITH_TIER, CHIMERA_FAITH_MODIFIERS, 1
    )
    EnsureChimeraYieldTier(
        playerID, CHUUNI_CHIMERA_CULTURE_TIER,
        CHIMERA_CULTURE_MODIFIERS, 2
    )
    EnsureChimeraYieldTier(
        playerID, CHUUNI_CHIMERA_SCIENCE_TIER,
        CHIMERA_SCIENCE_MODIFIERS, 3
    )
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
        EnsureChimeraYieldTiers(playerID)
        PublishChuuniStatus(playerID)
    end
    return nextValue
end

local function EnsureStageMarkerResource(player, resourceIndex)
    if player == nil or resourceIndex == nil or player.GetResources == nil then
        return false
    end
    local resources = player:GetResources()
    if resources == nil or resources.GetResourceAmount == nil
        or resources.ChangeResourceAmount == nil then
        return false
    end
    local storedAmount = resources:GetResourceAmount(resourceIndex)
    local currentAmount = tonumber(storedAmount) or 0
    if currentAmount < 1 then
        resources:ChangeResourceAmount(resourceIndex, 1 - currentAmount)
        return true
    end
    return false
end

local function EnsureStageMarkerResources(player, stage)
    local maximumStage = math.max(0, math.min(4, tonumber(stage) or 0))
    for markerStage = 1, maximumStage do
        EnsureStageMarkerResource(
            player,
            STAGE_MARKER_RESOURCE_INDICES[markerStage]
        )
    end
end

local function EnsureChimeraUnlocked(player)
    player:SetProperty(CHUUNI_CHIMERA_UNLOCKED, 1)
    if player:GetProperty(CHUUNI_CHIMERA_TITLE_ATTACHED) == 1 then
        return
    end
    player:AttachModifierByID(CHUUNI_CHIMERA_GOVERNOR_POINT)
    player:SetProperty(CHUUNI_CHIMERA_TITLE_ATTACHED, 1)
    Log("奇美拉已解锁：已补发专用总督点，等待自动任命。")
end

local function UnlockStage(player, playerID, stage, propertyName, localizationKey)
    if player:GetProperty(propertyName) ~= 1 then
        if stage == 1 then
            EnsureChimeraUnlocked(player)
        end
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

    if stage >= 1 then
        EnsureChimeraUnlocked(player)
    end

    EnsureChimeraYieldTiers(playerID)
    player:SetProperty(CHUUNI_STAGE, stage)
    EnsureStageMarkerResources(player, stage)
    PublishChuuniStatus(playerID)
    return stage
end

local function GetEstablishedChimeraCity(player)
    if player == nil or CHIMERA_GOVERNOR_DEFINITION == nil
        or player.GetGovernors == nil then
        return nil
    end
    local governors = player:GetGovernors()
    if governors == nil or governors.GetGovernor == nil then
        return nil
    end
    local chimera = governors:GetGovernor(CHIMERA_GOVERNOR_DEFINITION.Hash)
    if chimera == nil or chimera.IsEstablished == nil
        or not chimera:IsEstablished() or chimera.GetAssignedCity == nil then
        return nil
    end
    return chimera:GetAssignedCity()
end

local function GetUnitPlot(unit)
    if unit == nil or Map == nil or Map.GetPlot == nil then
        return nil
    end
    return Map.GetPlot(unit:GetX(), unit:GetY())
end

local function IsUnitInChimeraCity(unit, chimeraCity)
    if unit == nil or chimeraCity == nil or Cities == nil
        or Cities.GetPlotPurchaseCity == nil then
        return false, nil
    end
    local plot = GetUnitPlot(unit)
    if plot == nil then
        return false, nil
    end
    local owningCity = Cities.GetPlotPurchaseCity(plot)
    if owningCity == nil then
        return false, plot
    end
    return owningCity:GetOwner() == chimeraCity:GetOwner()
        and owningCity:GetID() == chimeraCity:GetID(), plot
end

local function SetUnitAbilityCount(unit, abilityType, shouldHave)
    if unit == nil or unit.GetAbility == nil then
        return
    end
    local abilities = unit:GetAbility()
    if abilities == nil or abilities.GetAbilityCount == nil
        or abilities.ChangeAbilityCount == nil then
        return
    end
    local storedCount = abilities:GetAbilityCount(abilityType)
    local currentCount = tonumber(storedCount) or 0
    if shouldHave and currentCount < 1 then
        abilities:ChangeAbilityCount(abilityType, 1 - currentCount)
    elseif not shouldHave and currentCount > 0 then
        abilities:ChangeAbilityCount(abilityType, -currentCount)
    end
end

local function RefreshChimeraCombatAbilityForUnit(playerID, unit)
    local player = GetPlayer(playerID)
    local chimeraCity = GetEstablishedChimeraCity(player)
    local inChimeraCity = IsUnitInChimeraCity(unit, chimeraCity)
    SetUnitAbilityCount(
        unit,
        CHIMERA_COMBAT_ABILITY,
        IsChuuniPlayer(playerID)
            and GetStoredStage(player) >= 2
            and inChimeraCity == true
    )
end

local function RefreshChimeraUnitAbilities(playerID)
    if not IsChuuniPlayer(playerID) then
        return
    end
    local player = GetPlayer(playerID)
    if player == nil or player.GetUnits == nil then
        return
    end
    local chimeraCity = GetEstablishedChimeraCity(player)
    local stage = GetStoredStage(player)
    for _, unit in player:GetUnits():Members() do
        local inChimeraCity = IsUnitInChimeraCity(unit, chimeraCity)
        SetUnitAbilityCount(
            unit, CHIMERA_COMBAT_ABILITY,
            stage >= 2 and inChimeraCity == true
        )
        -- This refresh runs at turn activation. The mobility ability then
        -- remains for the turn even if the unit leaves Chimera's territory.
        SetUnitAbilityCount(
            unit, CHIMERA_MOBILITY_ABILITY,
            stage >= 3 and inChimeraCity == true
        )
    end
end

local function ShouldGrantChimeraRestBonus(snapshot, currentState)
    if snapshot == nil or currentState == nil then
        return false
    end
    return snapshot.eligible == true
        and snapshot.turn + 1 == currentState.turn
        and snapshot.unitType == currentState.unitType
        and snapshot.plotIndex == currentState.plotIndex
        and snapshot.cityID == currentState.cityID
        and snapshot.damage > currentState.damage
        and currentState.damage > 0
        and currentState.inChimeraCity == true
end

local function SnapshotChimeraRestCandidates(playerID)
    if not IsChuuniPlayer(playerID) then
        return
    end
    local player = GetPlayer(playerID)
    local chimeraCity = GetEstablishedChimeraCity(player)
    if player == nil or player.GetUnits == nil then
        return
    end
    local currentTurn = Game.GetCurrentGameTurn()
    for _, unit in player:GetUnits():Members() do
        local inChimeraCity, plot = IsUnitInChimeraCity(unit, chimeraCity)
        local damage = unit:GetDamage()
        local eligible = inChimeraCity and damage > 0
            and unit.GetMovesRemaining ~= nil and unit.GetMaxMoves ~= nil
            and unit:GetMovesRemaining() >= unit:GetMaxMoves()
        unit:SetProperty(CHIMERA_REST_DAMAGE, damage)
        unit:SetProperty(CHIMERA_REST_TURN, currentTurn)
        unit:SetProperty(CHIMERA_REST_UNIT_TYPE, unit:GetType())
        unit:SetProperty(
            CHIMERA_REST_PLOT,
            plot ~= nil and plot:GetIndex() or -1
        )
        unit:SetProperty(
            CHIMERA_REST_CITY,
            chimeraCity ~= nil and chimeraCity:GetID() or -1
        )
        unit:SetProperty(CHIMERA_REST_ELIGIBLE, eligible and 1 or 0)
    end
end

local function ApplyChimeraRestBonuses(playerID)
    if not IsChuuniPlayer(playerID) then
        return
    end
    local player = GetPlayer(playerID)
    local chimeraCity = GetEstablishedChimeraCity(player)
    if player == nil or player.GetUnits == nil or chimeraCity == nil then
        return
    end
    local currentTurn = Game.GetCurrentGameTurn()
    for _, unit in player:GetUnits():Members() do
        local inChimeraCity, plot = IsUnitInChimeraCity(unit, chimeraCity)
        local storedDamage = unit:GetProperty(CHIMERA_REST_DAMAGE)
        local storedTurn = unit:GetProperty(CHIMERA_REST_TURN)
        local storedUnitType = unit:GetProperty(CHIMERA_REST_UNIT_TYPE)
        local storedPlot = unit:GetProperty(CHIMERA_REST_PLOT)
        local storedCity = unit:GetProperty(CHIMERA_REST_CITY)
        local storedEligible = unit:GetProperty(CHIMERA_REST_ELIGIBLE)
        local snapshot = {
            damage = tonumber(storedDamage) or -1,
            turn = tonumber(storedTurn) or -1,
            unitType = tonumber(storedUnitType) or -1,
            plotIndex = tonumber(storedPlot) or -1,
            cityID = tonumber(storedCity) or -1,
            eligible = tonumber(storedEligible) == 1,
        }
        local currentDamage = unit:GetDamage()
        local currentState = {
            damage = currentDamage,
            turn = currentTurn,
            unitType = unit:GetType(),
            plotIndex = plot ~= nil and plot:GetIndex() or -1,
            cityID = chimeraCity:GetID(),
            inChimeraCity = inChimeraCity,
        }
        if ShouldGrantChimeraRestBonus(snapshot, currentState) then
            local actualHeal = math.min(20, currentDamage)
            unit:ChangeDamage(-actualHeal)
            Log("奇美拉休整 +" .. tostring(actualHeal)
                .. " unit=" .. tostring(unit:GetID()))
        end
    end
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

    ApplyChimeraRestBonuses(playerID)
    local player = GetPlayer(playerID)
    RefreshChimeraUnitAbilities(playerID)
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
    RefreshChimeraUnitAbilities(playerID)
end

local function OnReligionFounded(playerID)
    UpdateChuuniStage(playerID)
    RefreshChimeraUnitAbilities(playerID)
end

local function OnUnitMoved(playerID, unitID)
    if not IsChuuniPlayer(playerID) or UnitManager == nil
        or UnitManager.GetUnit == nil then
        return
    end
    RefreshChimeraCombatAbilityForUnit(
        playerID, UnitManager.GetUnit(playerID, unitID)
    )
end

local function OnUnitAddedToMap(playerID, unitID)
    OnUnitMoved(playerID, unitID)
end

local function CityHasMagicCircle(city)
    if city == nil or city.GetBuildings == nil then
        return false
    end
    local buildings = city:GetBuildings()
    return buildings ~= nil and buildings:HasBuilding(MAGIC_CIRCLE_INDEX)
end

local function IsValidTeleportUnit(playerID, unit)
    if unit == nil or unit:GetOwner() ~= playerID then
        return false
    end
    local unitInfo = GameInfo.Units[unit:GetType()]
    return unitInfo ~= nil
        and unitInfo.Domain == "DOMAIN_LAND"
        and unitInfo.UnitType ~= "UNIT_TRADER"
        and unitInfo.UnitType ~= "UNIT_SPY"
end

local function GetTeleportSourceCity(playerID, unit)
    local plot = GetUnitPlot(unit)
    if plot == nil or plot:GetOwner() ~= playerID
        or plot:GetDistrictType() ~= CHUUNI_DISTRICT_INDEX then
        return nil, plot
    end
    local city = Cities.GetPlotPurchaseCity(plot)
    if city == nil or not CityHasMagicCircle(city) then
        return nil, plot
    end
    local hasCompletedSociety = false
    if city.GetDistricts ~= nil then
        for _, district in city:GetDistricts():Members() do
            if district:IsComplete()
                and district:GetType() == CHUUNI_DISTRICT_INDEX
                and district:GetX() == plot:GetX()
                and district:GetY() == plot:GetY() then
                hasCompletedSociety = true
                break
            end
        end
    end
    if not hasCompletedSociety then
        return nil, plot
    end
    return city, plot
end

local function IsTeleportTargetPlotAvailable(plot)
    if plot == nil or Map.GetUnitsAt == nil then
        return false
    end
    local units = Map.GetUnitsAt(plot)
    return units == nil or #units == 0
end

local function FindNearestTeleportTarget(player, sourcePlot)
    if player == nil or sourcePlot == nil or player.GetCities == nil then
        return nil
    end
    local bestPlot = nil
    local bestDistance = nil
    for _, city in player:GetCities():Members() do
        if CityHasMagicCircle(city) and city.GetDistricts ~= nil then
            local districts = city:GetDistricts()
            for _, district in districts:Members() do
                if district:IsComplete()
                    and district:GetType() == CHUUNI_DISTRICT_INDEX then
                    local targetPlot = Map.GetPlot(
                        district:GetX(), district:GetY()
                    )
                    if targetPlot ~= nil
                        and targetPlot:GetIndex() ~= sourcePlot:GetIndex()
                        and IsTeleportTargetPlotAvailable(targetPlot) then
                        local distance = Map.GetPlotDistance(
                            sourcePlot:GetX(), sourcePlot:GetY(),
                            targetPlot:GetX(), targetPlot:GetY()
                        )
                        if bestDistance == nil or distance < bestDistance then
                            bestDistance = distance
                            bestPlot = targetPlot
                        end
                    end
                end
            end
        end
    end
    return bestPlot
end

local function OnChuuniTeleport(playerID, parameters)
    if not IsChuuniPlayer(playerID) or parameters == nil
        or GetStoredStage(GetPlayer(playerID)) < 1 then
        return
    end
    local unitID = tonumber(parameters.UnitID)
    local unit = unitID ~= nil and UnitManager.GetUnit(playerID, unitID) or nil
    if not IsValidTeleportUnit(playerID, unit) then
        return
    end
    local currentTurn = Game.GetCurrentGameTurn()
    local storedTeleportTurn = unit:GetProperty(CHUUNI_TELEPORT_TURN)
    if tonumber(storedTeleportTurn) == currentTurn then
        return
    end
    local sourceCity, sourcePlot = GetTeleportSourceCity(playerID, unit)
    if sourceCity == nil then
        return
    end
    local targetPlot = FindNearestTeleportTarget(
        GetPlayer(playerID), sourcePlot
    )
    if targetPlot == nil then
        return
    end
    UnitManager.PlaceUnit(unit, targetPlot:GetX(), targetPlot:GetY())
    local moves = unit:GetMovesRemaining()
    if moves > 0 then
        UnitManager.ChangeMovesRemaining(unit, -moves)
    end
    unit:SetProperty(CHUUNI_TELEPORT_TURN, currentTurn)
    Log("魔法阵传送完成 unit=" .. tostring(unitID))
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
Events.PlayerTurnDeactivated.Add(SnapshotChimeraRestCandidates)
Events.ReligionFounded.Add(OnReligionFounded)
Events.CityAddedToMap.Add(OnCityAddedToMap)
Events.UnitMoved.Add(OnUnitMoved)
Events.UnitAddedToMap.Add(OnUnitAddedToMap)
GameEvents.ChuuniTeleport.Add(OnChuuniTeleport)

Log("Chuuni gameplay progression initialized")
