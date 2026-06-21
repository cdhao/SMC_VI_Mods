local CIVILIZATION_ELPIS_PROTOCOL = "CIVILIZATION_ELPIS_PROTOCOL"
local RESOURCE_INFECTED_BLOOD = "RESOURCE_INFECTED_BLOOD"
local WRITING_BOOST_GRANTED = "GRACE_WRITING_BOOST_GRANTED"

local STEROID_LEVEL = "GRACE_STEROID_LEVEL"
local STEROID_LAST_HEAL_TURN = "GRACE_STEROID_LAST_HEAL_TURN"

local PROJECT_HEMOLYTIC_1 = "PROJECT_GRACE_HEMOLYTIC_1"
local PROJECT_HEMOLYTIC_2 = "PROJECT_GRACE_HEMOLYTIC_2"
local PROJECT_HEMOLYTIC_3 = "PROJECT_GRACE_HEMOLYTIC_3"
local PROJECT_STABILIZER_1 = "PROJECT_GRACE_STABILIZER_1"
local PROJECT_STABILIZER_2 = "PROJECT_GRACE_STABILIZER_2"
local PROJECT_STABILIZER_3 = "PROJECT_GRACE_STABILIZER_3"
local PROJECT_STEROID_1 = "PROJECT_GRACE_STEROID_1"
local PROJECT_STEROID_2 = "PROJECT_GRACE_STEROID_2"
local PROJECT_STEROID_3 = "PROJECT_GRACE_STEROID_3"
local PROJECT_BLOOD_SAMPLE = "PROJECT_GRACE_BLOOD_SAMPLE_ANALYSIS"
local PROJECT_PATHOLOGY = "PROJECT_GRACE_ABNORMAL_PATHOLOGY"
local PROJECT_STRATEGIC = "PROJECT_GRACE_STRATEGIC_MATERIAL_SYNTHESIS"

local ENHANCER_PROJECTS = {
    [PROJECT_HEMOLYTIC_1] = { maxParam = "GRACE_MAX_HEMOLYTIC_LEVEL", nameTagPrefix = "LOC_ABILITY_GRACE_HEMOLYTIC_", level = 1 },
    [PROJECT_HEMOLYTIC_2] = { maxParam = "GRACE_MAX_HEMOLYTIC_LEVEL", nameTagPrefix = "LOC_ABILITY_GRACE_HEMOLYTIC_", level = 2 },
    [PROJECT_HEMOLYTIC_3] = { maxParam = "GRACE_MAX_HEMOLYTIC_LEVEL", nameTagPrefix = "LOC_ABILITY_GRACE_HEMOLYTIC_", level = 3 },
    [PROJECT_STABILIZER_1] = { maxParam = "GRACE_MAX_STABILIZER_LEVEL", nameTagPrefix = "LOC_ABILITY_GRACE_STABILIZER_", level = 1 },
    [PROJECT_STABILIZER_2] = { maxParam = "GRACE_MAX_STABILIZER_LEVEL", nameTagPrefix = "LOC_ABILITY_GRACE_STABILIZER_", level = 2 },
    [PROJECT_STABILIZER_3] = { maxParam = "GRACE_MAX_STABILIZER_LEVEL", nameTagPrefix = "LOC_ABILITY_GRACE_STABILIZER_", level = 3 },
    [PROJECT_STEROID_1] = { propertyName = STEROID_LEVEL, maxParam = "GRACE_MAX_STEROID_LEVEL", nameTagPrefix = "LOC_ABILITY_GRACE_STEROID_", level = 1 },
    [PROJECT_STEROID_2] = { propertyName = STEROID_LEVEL, maxParam = "GRACE_MAX_STEROID_LEVEL", nameTagPrefix = "LOC_ABILITY_GRACE_STEROID_", level = 2 },
    [PROJECT_STEROID_3] = { propertyName = STEROID_LEVEL, maxParam = "GRACE_MAX_STEROID_LEVEL", nameTagPrefix = "LOC_ABILITY_GRACE_STEROID_", level = 3 }
}

local BLOOD_PROJECTS = {
    [PROJECT_BLOOD_SAMPLE] = true,
    [PROJECT_PATHOLOGY] = true,
    [PROJECT_STRATEGIC] = true
}

for projectType, _ in pairs(ENHANCER_PROJECTS) do
    BLOOD_PROJECTS[projectType] = true
end

local recentBloodAwards = {}
local recentCampAwards = {}
local recentAwardTurn = nil
local ClearAwardCachesForCurrentTurn = nil

local TECH_WRITING_INDEX = nil
if GameInfo.Technologies["TECH_WRITING"] ~= nil then
    TECH_WRITING_INDEX = GameInfo.Technologies["TECH_WRITING"].Index
end

local RESOURCE_INFECTED_BLOOD_INDEX = nil
if GameInfo.Resources[RESOURCE_INFECTED_BLOOD] ~= nil then
    RESOURCE_INFECTED_BLOOD_INDEX = GameInfo.Resources[RESOURCE_INFECTED_BLOOD].Index
end

local BARBARIAN_CAMP_IMPROVEMENT_INDEX = nil
if GameInfo.Improvements["IMPROVEMENT_BARBARIAN_CAMP"] ~= nil then
    BARBARIAN_CAMP_IMPROVEMENT_INDEX = GameInfo.Improvements["IMPROVEMENT_BARBARIAN_CAMP"].Index
end

local function Log(message)
    print("[GraceAshcroft] " .. tostring(message))
end

local function GetParam(name, defaultValue)
    local row = GameInfo.GlobalParameters[name]
    if row == nil or row.Value == nil then
        return defaultValue
    end

    return tonumber(row.Value) or defaultValue
end

local function GetPlayer(playerID)
    if playerID == nil or Players[playerID] == nil then
        return nil
    end

    return Players[playerID]
end

local function IsGracePlayer(playerID)
    if playerID == nil or PlayerConfigurations[playerID] == nil then
        return false
    end

    return PlayerConfigurations[playerID]:GetCivilizationTypeName() == CIVILIZATION_ELPIS_PROTOCOL
end

local function IsBarbarianPlayer(playerID)
    local player = GetPlayer(playerID)
    if player ~= nil and player.IsBarbarian ~= nil and player:IsBarbarian() then
        return true
    end

    if playerID ~= nil and PlayerConfigurations[playerID] ~= nil then
        return PlayerConfigurations[playerID]:GetCivilizationTypeName() == "CIVILIZATION_BARBARIAN"
    end

    return false
end

local function IsBarbarianCampImprovement(improvementType)
    if improvementType == nil then
        return false
    end

    if BARBARIAN_CAMP_IMPROVEMENT_INDEX == nil and GameInfo.Improvements["IMPROVEMENT_BARBARIAN_CAMP"] ~= nil then
        BARBARIAN_CAMP_IMPROVEMENT_INDEX = GameInfo.Improvements["IMPROVEMENT_BARBARIAN_CAMP"].Index
    end

    if BARBARIAN_CAMP_IMPROVEMENT_INDEX ~= nil and improvementType == BARBARIAN_CAMP_IMPROVEMENT_INDEX then
        return true
    end

    local improvement = GameInfo.Improvements[improvementType]
    if improvement ~= nil then
        return improvement.BarbarianCamp == true or improvement.BarbarianCamp == 1 or improvement.ImprovementType == "IMPROVEMENT_BARBARIAN_CAMP"
    end

    return false
end

local function HasBloodSampler(playerID)
    if not IsGracePlayer(playerID) then
        return false
    end

    local player = GetPlayer(playerID)
    if player == nil then
        return false
    end

    if TECH_WRITING_INDEX == nil then
        return true
    end

    local techs = player:GetTechs()
    if techs == nil or techs.HasTech == nil then
        return true
    end

    return techs:HasTech(TECH_WRITING_INDEX)
end

local function GetBlood(playerID)
    local player = GetPlayer(playerID)
    if player == nil then
        return 0
    end

    local resources = player:GetResources()
    if resources == nil or resources.GetResourceAmount == nil then
        return 0
    end

    if RESOURCE_INFECTED_BLOOD_INDEX == nil and GameInfo.Resources[RESOURCE_INFECTED_BLOOD] ~= nil then
        RESOURCE_INFECTED_BLOOD_INDEX = GameInfo.Resources[RESOURCE_INFECTED_BLOOD].Index
    end

    if RESOURCE_INFECTED_BLOOD_INDEX == nil then
        return 0
    end

    return tonumber(resources:GetResourceAmount(RESOURCE_INFECTED_BLOOD_INDEX)) or 0
end

local function LookupText(tag, ...)
    if Locale ~= nil and Locale.Lookup ~= nil then
        return Locale.Lookup(tag, ...)
    end

    return tag
end

local function PublishStatus(playerID, message)
    if message ~= nil and message ~= "" then
        Log(message)
    end
end

local function GetNumericPlayerProperty(player, propertyName)
    if player == nil then
        return 0
    end

    local value = player:GetProperty(propertyName) or 0
    return tonumber(value) or 0
end

local function TryGrantOpeningWritingEureka(playerID)
    local player = GetPlayer(playerID)
    if player == nil or TECH_WRITING_INDEX == nil then
        return
    end

    if GetNumericPlayerProperty(player, WRITING_BOOST_GRANTED) > 0 then
        return
    end

    local techs = player:GetTechs()
    if techs == nil then
        return
    end

    if techs.HasTech ~= nil and techs:HasTech(TECH_WRITING_INDEX) then
        player:SetProperty(WRITING_BOOST_GRANTED, 1)
        return
    end

    if techs.HasBoostBeenTriggered ~= nil and techs:HasBoostBeenTriggered(TECH_WRITING_INDEX) then
        player:SetProperty(WRITING_BOOST_GRANTED, 1)
        return
    end

    if techs.CanTriggerBoost ~= nil and not techs:CanTriggerBoost(TECH_WRITING_INDEX) then
        return
    end

    if techs.TriggerBoost ~= nil then
        techs:TriggerBoost(TECH_WRITING_INDEX)
        player:SetProperty(WRITING_BOOST_GRANTED, 1)
        PublishStatus(playerID, LookupText("LOC_GRACE_NOTIFICATION_WRITING_EUREKA"))
        Log("Triggered opening Writing boost.")
    end
end

local function ChangeBlood(playerID, amount, suppressNotification)
    local player = GetPlayer(playerID)
    if player == nil or amount == 0 then
        return GetBlood(playerID)
    end

    local resources = player:GetResources()
    if resources == nil or resources.ChangeResourceAmount == nil then
        Log("Player resource API unavailable; cannot change infected blood.")
        return GetBlood(playerID)
    end

    if RESOURCE_INFECTED_BLOOD_INDEX == nil and GameInfo.Resources[RESOURCE_INFECTED_BLOOD] ~= nil then
        RESOURCE_INFECTED_BLOOD_INDEX = GameInfo.Resources[RESOURCE_INFECTED_BLOOD].Index
    end

    if RESOURCE_INFECTED_BLOOD_INDEX == nil then
        Log("Resource index unavailable for " .. RESOURCE_INFECTED_BLOOD .. ".")
        return GetBlood(playerID)
    end

    local actualAmount = amount
    if amount < 0 then
        local currentAmount = GetBlood(playerID)
        if currentAmount <= 0 then
            return currentAmount
        end

        actualAmount = -math.min(-amount, currentAmount)
    end

    resources:ChangeResourceAmount(RESOURCE_INFECTED_BLOOD_INDEX, actualAmount)
    local newAmount = GetBlood(playerID)

    local message = nil
    if actualAmount > 0 then
        message = LookupText("LOC_GRACE_NOTIFICATION_BLOOD_GAINED", actualAmount, newAmount)
    elseif actualAmount < 0 then
        message = LookupText("LOC_GRACE_NOTIFICATION_BLOOD_SPENT", -actualAmount, newAmount)
    end

    if not suppressNotification then
        PublishStatus(playerID, message)
    end

    return newAmount
end

local function GetProjectType(projectID)
    if type(projectID) == "string" then
        return projectID
    end

    if type(projectID) == "number" then
        local row = GameInfo.Projects[projectID]
        if row ~= nil then
            return row.ProjectType
        end

        if DB ~= nil and DB.MakeHash ~= nil then
            for project in GameInfo.Projects() do
                if DB.MakeHash(project.ProjectType) == projectID then
                    return project.ProjectType
                end
            end
        end
    end

    return nil
end

local function GetCityByID(playerID, cityID)
    local player = GetPlayer(playerID)
    if player == nil or player.GetCities == nil or cityID == nil then
        return nil
    end

    local cities = player:GetCities()
    if cities == nil or cities.FindID == nil then
        return nil
    end

    return cities:FindID(cityID)
end

local function GetEraIndex()
    if Game ~= nil and Game.GetEras ~= nil then
        local eras = Game.GetEras()
        if eras ~= nil and eras.GetCurrentEra ~= nil then
            return eras:GetCurrentEra()
        end
    end

    return 0
end

local function GetEnhancerTargetLevel(projectConfig)
    if projectConfig == nil then
        return 0, 0
    end

    local maxLevel = GetParam(projectConfig.maxParam, 3)
    local targetLevel = tonumber(projectConfig.level) or 0
    return math.min(targetLevel, maxLevel), maxLevel
end

local function CanSetEnhancerLevel(playerID, projectConfig)
    local player = GetPlayer(playerID)
    if player == nil then
        return false
    end

    if projectConfig.propertyName == nil then
        return true
    end

    local targetLevel = GetEnhancerTargetLevel(projectConfig)
    if targetLevel <= 0 then
        return false
    end

    return GetNumericPlayerProperty(player, projectConfig.propertyName) < targetLevel
end

local function SetEnhancerLevel(playerID, projectConfig)
    local player = GetPlayer(playerID)
    if player == nil then
        return
    end

    local targetLevel, maxLevel = GetEnhancerTargetLevel(projectConfig)
    if targetLevel <= 0 then
        return
    end

    if projectConfig.propertyName ~= nil then
        local level = GetNumericPlayerProperty(player, projectConfig.propertyName)
        if level >= targetLevel then
            PublishStatus(playerID, LookupText("LOC_GRACE_NOTIFICATION_PROJECT_CAPPED"))
            return
        end

        player:SetProperty(projectConfig.propertyName, targetLevel)
    end

    local nameTag = projectConfig.nameTagPrefix .. tostring(targetLevel) .. "_NAME"
    PublishStatus(playerID, LookupText("LOC_GRACE_NOTIFICATION_ENHANCER_GAINED", LookupText(nameTag), targetLevel, maxLevel, GetBlood(playerID)))
end

local function ForceHealUnit(unit, healAmount)
    if unit == nil or healAmount == nil or healAmount <= 0 then
        return 0
    end

    if unit.GetDamage == nil or unit.ChangeDamage == nil then
        return 0
    end

    local currentDamage = tonumber(unit:GetDamage()) or 0
    if currentDamage <= 0 then
        return 0
    end

    local actualHeal = math.min(healAmount, currentDamage)
    unit:ChangeDamage(-actualHeal)

    return actualHeal
end

local function GrantScience(playerID, amount, suppressNotification)
    local player = GetPlayer(playerID)
    if player == nil or amount <= 0 then
        return false
    end

    if player.GrantYield ~= nil and GameInfo.Yields["YIELD_SCIENCE"] ~= nil then
        player:GrantYield(GameInfo.Yields["YIELD_SCIENCE"].Index, amount)
        Log("Granted " .. tostring(amount) .. " Science through GrantYield.")
        if not suppressNotification then
            PublishStatus(playerID, LookupText("LOC_GRACE_NOTIFICATION_SCIENCE_GAINED", amount, GetBlood(playerID)))
        end
        return true
    end

    local techs = player:GetTechs()
    if techs ~= nil and techs.ChangeCurrentResearchProgress ~= nil then
        techs:ChangeCurrentResearchProgress(amount)
        Log("Granted " .. tostring(amount) .. " Science through current research progress.")
        if not suppressNotification then
            PublishStatus(playerID, LookupText("LOC_GRACE_NOTIFICATION_SCIENCE_GAINED", amount, GetBlood(playerID)))
        end
        return true
    end

    Log("Unable to grant Science to player " .. tostring(playerID) .. ".")
    return false
end

local function GrantGreatScientistPoints(playerID, amount, suppressNotification)
    local player = GetPlayer(playerID)
    if player == nil or amount <= 0 then
        return false
    end

    if player.GetGreatPeoplePoints == nil or GameInfo.GreatPersonClasses["GREAT_PERSON_CLASS_SCIENTIST"] == nil then
        Log("Great Scientist point API unavailable.")
        return false
    end

    local points = player:GetGreatPeoplePoints()
    if points == nil or points.ChangePointsTotal == nil then
        Log("Great Scientist point mutator unavailable.")
        return false
    end

    points:ChangePointsTotal(GameInfo.GreatPersonClasses["GREAT_PERSON_CLASS_SCIENTIST"].Index, amount)
    Log("Granted " .. tostring(amount) .. " Great Scientist points.")
    if not suppressNotification then
        PublishStatus(playerID, LookupText("LOC_GRACE_NOTIFICATION_SCIENTIST_POINTS_GAINED", amount, GetBlood(playerID)))
    end
    return true
end

local function GetCityScienceYield(city)
    if city == nil or city.GetYield == nil then
        return 0
    end

    if YieldTypes ~= nil and YieldTypes.SCIENCE ~= nil then
        return tonumber(city:GetYield(YieldTypes.SCIENCE)) or 0
    end

    if GameInfo.Yields["YIELD_SCIENCE"] ~= nil then
        return tonumber(city:GetYield(GameInfo.Yields["YIELD_SCIENCE"].Index)) or 0
    end

    return 0
end

local function GetCityGreatScientistPointsPerTurn(city)
    if city == nil then
        return 0
    end

    if city.GetGreatPeoplePoints ~= nil then
        local cityPoints = city:GetGreatPeoplePoints()
        if cityPoints ~= nil and cityPoints.GetPointsPerTurn ~= nil and GameInfo.GreatPersonClasses["GREAT_PERSON_CLASS_SCIENTIST"] ~= nil then
            return tonumber(cityPoints:GetPointsPerTurn(GameInfo.GreatPersonClasses["GREAT_PERSON_CLASS_SCIENTIST"].Index)) or 0
        end
    end

    local amount = 0
    local cityDistricts = nil
    if city.GetDistricts ~= nil then
        cityDistricts = city:GetDistricts()
    end

    if cityDistricts ~= nil and cityDistricts.HasDistrict ~= nil then
        for row in GameInfo.District_GreatPersonPoints() do
            if row.GreatPersonClassType == "GREAT_PERSON_CLASS_SCIENTIST" then
                local district = GameInfo.Districts[row.DistrictType]
                if district ~= nil and cityDistricts:HasDistrict(district.Index, true) then
                    amount = amount + (tonumber(row.PointsPerTurn) or 0)
                end
            end
        end
    end

    local cityBuildings = nil
    if city.GetBuildings ~= nil then
        cityBuildings = city:GetBuildings()
    end

    if cityBuildings ~= nil and cityBuildings.HasBuilding ~= nil then
        for row in GameInfo.Building_GreatPersonPoints() do
            if row.GreatPersonClassType == "GREAT_PERSON_CLASS_SCIENTIST" then
                local building = GameInfo.Buildings[row.BuildingType]
                if building ~= nil and cityBuildings:HasBuilding(building.Index) then
                    amount = amount + (tonumber(row.PointsPerTurn) or 0)
                end
            end
        end
    end

    return amount
end

local function CalculatePathologyRewardPerBlood(city)
    local percent = GetParam("GRACE_PATHOLOGY_CITY_YIELD_PERCENT", 50) / 100
    local minimumReward = GetParam("GRACE_PATHOLOGY_MIN_REWARD_PER_BLOOD", 5)
    local currentEra = GetEraIndex()
    local scientistPoints = math.max(minimumReward, math.floor((GetCityGreatScientistPointsPerTurn(city) * percent) + currentEra))
    local science = math.max(minimumReward, math.floor((GetCityScienceYield(city) * percent) + (currentEra * 2)))

    return scientistPoints, science
end

local function GrantPathologyFundingRewards(playerID, city, processedBlood)
    local scientistPointsPerBlood, sciencePerBlood = CalculatePathologyRewardPerBlood(city)
    local scientistPoints = processedBlood * scientistPointsPerBlood
    local science = processedBlood * sciencePerBlood

    GrantGreatScientistPoints(playerID, scientistPoints, true)
    GrantScience(playerID, science, true)

    return scientistPoints, science
end

local function IsResourceUnlockedForPlayer(player, resource)
    if player == nil or resource == nil then
        return false
    end

    if resource.PrereqTech == nil then
        return true
    end

    local tech = GameInfo.Technologies[resource.PrereqTech]
    if tech == nil then
        return true
    end

    local techs = player:GetTechs()
    if techs == nil or techs.HasTech == nil then
        return false
    end

    return techs:HasTech(tech.Index)
end

local function GetResourceEra(resource)
    if resource == nil then
        return 0
    end

    local revealedEra = tonumber(resource.RevealedEra)
    if revealedEra ~= nil then
        return revealedEra
    end

    if resource.PrereqTech ~= nil and GameInfo.Technologies[resource.PrereqTech] ~= nil then
        local tech = GameInfo.Technologies[resource.PrereqTech]
        if tech.EraType ~= nil and GameInfo.Eras[tech.EraType] ~= nil then
            return GameInfo.Eras[tech.EraType].Index
        end
    end

    return 0
end

local function GetPlayerResourceAmount(resources, resource)
    if resources == nil or resources.GetResourceAmount == nil or resource == nil then
        return 0
    end

    return tonumber(resources:GetResourceAmount(resource.Index)) or 0
end

local function GetResourceStockpileCap(resources, resource)
    if resources ~= nil and resources.GetResourceStockpileCap ~= nil and resource ~= nil then
        local cap = tonumber(resources:GetResourceStockpileCap(resource.Index))
        if cap ~= nil and cap > 0 then
            return cap
        end
    end

    if GameInfo.Resource_Consumption ~= nil then
        for consumption in GameInfo.Resource_Consumption() do
            if consumption.ResourceType == resource.ResourceType and consumption.StockpileCap ~= nil then
                return tonumber(consumption.StockpileCap) or 999
            end
        end
    end

    return 999
end

local function FindStrategicSynthesisTarget(playerID, resourcePerBlood)
    local player = GetPlayer(playerID)
    if player == nil or player.GetResources == nil then
        return nil
    end

    local resources = player:GetResources()
    if resources == nil then
        return nil
    end

    local candidates = {}
    for resource in GameInfo.Resources() do
        if resource.ResourceClassType == "RESOURCECLASS_STRATEGIC" and resource.ResourceType ~= RESOURCE_INFECTED_BLOOD and IsResourceUnlockedForPlayer(player, resource) then
            local amount = GetPlayerResourceAmount(resources, resource)
            local cap = GetResourceStockpileCap(resources, resource)
            local remaining = cap - amount
            if remaining >= resourcePerBlood then
                table.insert(candidates, {
                    index = resource.Index,
                    resourceType = resource.ResourceType,
                    name = resource.Name,
                    amount = amount,
                    era = GetResourceEra(resource),
                    capacityBlood = math.floor(remaining / resourcePerBlood)
                })
            end
        end
    end

    if #candidates == 0 then
        return nil
    end

    table.sort(candidates, function(a, b)
        if a.amount ~= b.amount then
            return a.amount < b.amount
        end

        if a.era ~= b.era then
            return a.era > b.era
        end

        return a.resourceType < b.resourceType
    end)

    return candidates[1]
end

local function RandomIndex(maxValue)
    if maxValue <= 0 then
        return 0
    end

    if Game ~= nil and Game.GetRandNum ~= nil then
        return Game.GetRandNum(maxValue, "Grace Ashcroft Eureka") + 1
    end

    if TerrainBuilder ~= nil and TerrainBuilder.GetRandomNumber ~= nil then
        return TerrainBuilder.GetRandomNumber(maxValue, "Grace Ashcroft Eureka") + 1
    end

    return math.random(maxValue)
end

local function TryTriggerCurrentEraEureka(playerID)
    local player = GetPlayer(playerID)
    if player == nil or player.GetTechs == nil then
        return false
    end

    local techs = player:GetTechs()
    if techs == nil or techs.TriggerBoost == nil then
        return false
    end

    local currentEra = GetEraIndex()
    local candidates = {}

    for tech in GameInfo.Technologies() do
        local eraMatches = true
        if tech.EraType ~= nil and GameInfo.Eras[tech.EraType] ~= nil then
            eraMatches = GameInfo.Eras[tech.EraType].Index == currentEra
        end

        local hasTech = techs.HasTech ~= nil and techs:HasTech(tech.Index)
        local hasBoost = techs.HasBoostBeenTriggered ~= nil and techs:HasBoostBeenTriggered(tech.Index)
        local canBoost = techs.CanTriggerBoost == nil or techs:CanTriggerBoost(tech.Index)

        if eraMatches and not hasTech and not hasBoost and canBoost then
            table.insert(candidates, tech)
        end
    end

    if #candidates == 0 then
        return false
    end

    local chosen = candidates[RandomIndex(#candidates)]
    if chosen == nil then
        return false
    end

    techs:TriggerBoost(chosen.Index)
    Log("Triggered boost for " .. tostring(chosen.TechnologyType) .. ".")
    PublishStatus(playerID, LookupText("LOC_GRACE_NOTIFICATION_EUREKA_TRIGGERED", LookupText(chosen.Name), GetBlood(playerID)))
    return true
end

local function HandleBloodSampleAnalysis(playerID, city)
    if TryTriggerCurrentEraEureka(playerID) then
        return
    end

    local scientistPoints, science = GrantPathologyFundingRewards(playerID, city, 1)
    PublishStatus(playerID, LookupText("LOC_GRACE_NOTIFICATION_EUREKA_FALLBACK_PATHOLOGY", scientistPoints, science, GetBlood(playerID)))
end

local function HandlePathologyFunding(playerID, city)
    local maxBlood = math.max(1, math.min(GetParam("GRACE_PATHOLOGY_MAX_BLOOD_PER_PROJECT", 4), 4))
    local extraBlood = math.min(maxBlood - 1, GetBlood(playerID))
    local processedBlood = 1 + extraBlood

    if extraBlood > 0 then
        ChangeBlood(playerID, -extraBlood, true)
    end

    local scientistPoints, science = GrantPathologyFundingRewards(playerID, city, processedBlood)
    PublishStatus(playerID, LookupText("LOC_GRACE_NOTIFICATION_PATHOLOGY_DONE", processedBlood, extraBlood, scientistPoints, science, GetBlood(playerID)))
end

local function HandleStrategicMaterialSynthesis(playerID)
    local player = GetPlayer(playerID)
    if player == nil or player.GetResources == nil then
        return
    end

    local resources = player:GetResources()
    if resources == nil or resources.ChangeResourceAmount == nil then
        return
    end

    local resourcePerBlood = math.max(1, GetParam("GRACE_STRATEGIC_RESOURCE_PER_BLOOD", 2))
    local target = FindStrategicSynthesisTarget(playerID, resourcePerBlood)
    if target == nil then
        ChangeBlood(playerID, 1, true)
        PublishStatus(playerID, LookupText("LOC_GRACE_NOTIFICATION_STRATEGIC_SYNTHESIS_NO_TARGET", GetBlood(playerID)))
        return
    end

    local maxBlood = math.max(1, math.min(GetParam("GRACE_STRATEGIC_MAX_BLOOD_PER_PROJECT", 5), 5))
    local processedBlood = math.min(maxBlood, 1 + GetBlood(playerID), target.capacityBlood)
    if processedBlood <= 0 then
        ChangeBlood(playerID, 1, true)
        PublishStatus(playerID, LookupText("LOC_GRACE_NOTIFICATION_STRATEGIC_SYNTHESIS_NO_TARGET", GetBlood(playerID)))
        return
    end

    local extraBlood = processedBlood - 1
    if extraBlood > 0 then
        ChangeBlood(playerID, -extraBlood, true)
    end

    local resourceGained = processedBlood * resourcePerBlood
    resources:ChangeResourceAmount(target.index, resourceGained)
    PublishStatus(playerID, LookupText("LOC_GRACE_NOTIFICATION_STRATEGIC_SYNTHESIS_DONE", processedBlood, extraBlood, LookupText(target.name), resourceGained, GetBlood(playerID)))
end

local function GetCurrentTurn()
    if Game ~= nil and Game.GetCurrentGameTurn ~= nil then
        return Game.GetCurrentGameTurn()
    end

    return 0
end

function ClearAwardCachesForCurrentTurn()
    local currentTurn = GetCurrentTurn()
    if recentAwardTurn ~= currentTurn then
        recentBloodAwards = {}
        recentCampAwards = {}
        recentAwardTurn = currentTurn
    end

    return currentTurn
end

local function TryReadField(source, key)
    if source == nil or key == nil then
        return nil
    end

    local success, value = pcall(function()
        return source[key]
    end)

    if success then
        return value
    end

    return nil
end

local function ReadCombatField(source, keys)
    if source == nil or keys == nil then
        return nil
    end

    for _, key in ipairs(keys) do
        local value = TryReadField(source, key)
        if value ~= nil then
            return value
        end

        if CombatResultParameters ~= nil then
            local indexedKey = TryReadField(CombatResultParameters, key)
            if indexedKey ~= nil then
                value = TryReadField(source, indexedKey)
                if value ~= nil then
                    return value
                end
            end
        end
    end

    return nil
end

local function ExtractCombatParticipant(combatResult, role)
    if combatResult == nil then
        return nil
    end

    if role == "attacker" then
        return ReadCombatField(combatResult, {"ATTACKER", "Attacker", "attacker"})
    end

    return ReadCombatField(combatResult, {"DEFENDER", "Defender", "defender"})
end

local function ExtractParticipantPlayerID(participant)
    return tonumber(ReadCombatField(participant, {"PLAYER", "PLAYER_ID", "PLAYERID", "Player", "PlayerID", "player", "playerID", "Owner", "OwnerID", "owner", "ownerID"}))
end

local function ExtractParticipantUnitID(participant)
    return tonumber(ReadCombatField(participant, {"UNIT", "UNIT_ID", "UNITID", "Unit", "UnitID", "unit", "unitID"}))
end

local function IsParticipantDead(participant)
    local explicitDead = ReadCombatField(participant, {"DEAD", "IS_DEAD", "IsDead", "isDead", "Dead", "dead", "Killed", "killed"})
    if explicitDead ~= nil then
        return explicitDead == true or explicitDead == 1
    end

    local finalDamage = tonumber(ReadCombatField(participant, {"FINAL_DAMAGE", "FINAL_DAMAGE_TO", "DAMAGE_TO", "DamageTo", "FinalDamage", "finalDamage", "damageTo", "damage"}))
    if finalDamage ~= nil then
        return finalDamage >= 100
    end

    return false
end

local function TryAwardBloodForKill(killedPlayerID, killedUnitID, killerPlayerID)
    if killedPlayerID == nil or killerPlayerID == nil then
        return
    end

    if not IsBarbarianPlayer(killedPlayerID) then
        return
    end

    if not HasBloodSampler(killerPlayerID) then
        return
    end

    local currentTurn = ClearAwardCachesForCurrentTurn()
    local awardKey = tostring(currentTurn) .. ":" .. tostring(killedPlayerID) .. ":" .. tostring(killedUnitID) .. ":" .. tostring(killerPlayerID)
    if recentBloodAwards[awardKey] then
        return
    end

    recentBloodAwards[awardKey] = true
    ChangeBlood(killerPlayerID, GetParam("GRACE_BLOOD_PER_BARBARIAN_KILL", 1))
end

local function TryAwardBloodForBarbarianCamp(playerID, unitID, locationX, locationY, improvementType)
    if playerID == nil or not HasBloodSampler(playerID) then
        return
    end

    if not IsBarbarianCampImprovement(improvementType) then
        return
    end

    local currentTurn = ClearAwardCachesForCurrentTurn()
    local plotKey = tostring(locationX) .. "," .. tostring(locationY)
    if Map ~= nil and Map.GetPlotIndex ~= nil then
        local plotIndex = Map.GetPlotIndex(locationX, locationY)
        if plotIndex ~= nil then
            plotKey = tostring(plotIndex)
        end
    end

    local awardKey = tostring(currentTurn) .. ":" .. plotKey .. ":" .. tostring(playerID)
    if recentCampAwards[awardKey] then
        return
    end

    recentCampAwards[awardKey] = true
    ChangeBlood(playerID, GetParam("GRACE_BLOOD_PER_BARBARIAN_CAMP", 2))
end

local function OnCombat(combatResult)
    local attacker = ExtractCombatParticipant(combatResult, "attacker")
    local defender = ExtractCombatParticipant(combatResult, "defender")
    local attackerPlayerID = ExtractParticipantPlayerID(attacker)
    local defenderPlayerID = ExtractParticipantPlayerID(defender)

    if IsParticipantDead(defender) then
        local defenderUnitID = ExtractParticipantUnitID(defender)
        TryAwardBloodForKill(defenderPlayerID, defenderUnitID, attackerPlayerID)
    end

    if IsParticipantDead(attacker) then
        local attackerUnitID = ExtractParticipantUnitID(attacker)
        TryAwardBloodForKill(attackerPlayerID, attackerUnitID, defenderPlayerID)
    end
end

local function OnUnitKilledInCombat(killedPlayerID, killedUnitID, killerPlayerID, killerUnitID)
    TryAwardBloodForKill(killedPlayerID, killedUnitID, killerPlayerID)
end

local function OnImprovementActivated(locationX, locationY, unitOwner, unitID, improvementType, improvementOwner, activationType, activationValue)
    TryAwardBloodForBarbarianCamp(unitOwner, unitID, locationX, locationY, improvementType)
end

local function OnCityProjectCompleted(playerID, cityID, projectID, buildingIndex, x, y, bCancelled)
    if bCancelled == true then
        return
    end

    if not IsGracePlayer(playerID) then
        return
    end

    local projectType = GetProjectType(projectID)
    if projectType == nil then
        return
    end

    if not BLOOD_PROJECTS[projectType] then
        return
    end

    local enhancerProject = ENHANCER_PROJECTS[projectType]
    if enhancerProject ~= nil then
        if not CanSetEnhancerLevel(playerID, enhancerProject) then
            PublishStatus(playerID, LookupText("LOC_GRACE_NOTIFICATION_PROJECT_CAPPED"))
            return
        end

        SetEnhancerLevel(playerID, enhancerProject)
        return
    end

    local city = GetCityByID(playerID, cityID)
    if projectType == PROJECT_BLOOD_SAMPLE then
        HandleBloodSampleAnalysis(playerID, city)
    elseif projectType == PROJECT_PATHOLOGY then
        HandlePathologyFunding(playerID, city)
    elseif projectType == PROJECT_STRATEGIC then
        HandleStrategicMaterialSynthesis(playerID)
    end
end

local function OnPlayerTurnActivated(playerID, bIsFirstTime)
    if bIsFirstTime == false then
        return
    end

    if not IsGracePlayer(playerID) then
        return
    end

    local player = GetPlayer(playerID)
    if player == nil then
        return
    end

    TryGrantOpeningWritingEureka(playerID)

    if player.GetUnits == nil then
        return
    end

    local steroidLevel = GetNumericPlayerProperty(player, STEROID_LEVEL)
    if steroidLevel <= 0 then
        return
    end

    local currentTurn = GetCurrentTurn()
    local lastSteroidHealTurn = player:GetProperty(STEROID_LAST_HEAL_TURN)
    if tonumber(lastSteroidHealTurn) == currentTurn then
        return
    end

    player:SetProperty(STEROID_LAST_HEAL_TURN, currentTurn)

    local healAmount = steroidLevel * GetParam("GRACE_STEROID_HEALING", 5)
    local totalHealed = 0
    for _, unit in player:GetUnits():Members() do
        totalHealed = totalHealed + ForceHealUnit(unit, healAmount)
    end

    Log("Steroid healing applied: level=" .. tostring(steroidLevel) .. ", healPerUnit=" .. tostring(healAmount) .. ", totalHealed=" .. tostring(totalHealed))
end

local function Initialize()
    if Events.UnitKilledInCombat ~= nil then
        Events.UnitKilledInCombat.Add(OnUnitKilledInCombat)
    elseif Events.Combat ~= nil then
        Events.Combat.Add(OnCombat)
        Log("Events.UnitKilledInCombat is unavailable; Events.Combat will handle barbarian kill blood gain as fallback.")
    else
        Log("No compatible combat kill event is available; barbarian kill blood gain is inactive.")
    end

    if Events.CityProjectCompleted ~= nil then
        Events.CityProjectCompleted.Add(OnCityProjectCompleted)
    else
        Log("Events.CityProjectCompleted is unavailable; project rewards are inactive.")
    end

    if Events.ImprovementActivated ~= nil then
        Events.ImprovementActivated.Add(OnImprovementActivated)
    else
        Log("Events.ImprovementActivated is unavailable; barbarian camp blood gain is inactive.")
    end

    if Events.PlayerTurnActivated ~= nil then
        Events.PlayerTurnActivated.Add(OnPlayerTurnActivated)
    else
        Log("Events.PlayerTurnActivated is unavailable; steroid healing is inactive.")
    end

    Log("Grace Ashcroft gameplay script initialized.")
end

Initialize()
