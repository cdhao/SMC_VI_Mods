INSERT INTO DistrictReplaces (CivUniqueDistrictType, ReplacesDistrictType)
VALUES
    ('DISTRICT_CHUUNI_SOCIETY', 'DISTRICT_HOLY_SITE');

INSERT INTO Districts (
    DistrictType,
    Name,
    PrereqTech,
    PrereqCivic,
    Coast,
    Description,
    Cost,
    RequiresPlacement,
    RequiresPopulation,
    NoAdjacentCity,
    CityCenter,
    Aqueduct,
    InternalOnly,
    ZOC,
    FreeEmbark,
    HitPoints,
    CaptureRemovesBuildings,
    CaptureRemovesCityDefenses,
    PlunderType,
    PlunderAmount,
    TradeEmbark,
    MilitaryDomain,
    CostProgressionModel,
    CostProgressionParam1,
    TraitType,
    Appeal,
    Housing,
    Entertainment,
    OnePerCity,
    AllowsHolyCity,
    Maintenance,
    AirSlots,
    CitizenSlots,
    TravelTime,
    CityStrengthModifier,
    AdjacentToLand,
    CanAttack,
    AdvisorType,
    CaptureRemovesDistrict,
    MaxPerPlayer
)
SELECT
    'DISTRICT_CHUUNI_SOCIETY',
    'LOC_DISTRICT_CHUUNI_SOCIETY_NAME',
    PrereqTech,
    PrereqCivic,
    Coast,
    'LOC_DISTRICT_CHUUNI_SOCIETY_DESCRIPTION',
    Cost,
    RequiresPlacement,
    RequiresPopulation,
    NoAdjacentCity,
    CityCenter,
    Aqueduct,
    InternalOnly,
    ZOC,
    FreeEmbark,
    HitPoints,
    CaptureRemovesBuildings,
    CaptureRemovesCityDefenses,
    PlunderType,
    PlunderAmount,
    TradeEmbark,
    MilitaryDomain,
    CostProgressionModel,
    CostProgressionParam1,
    'TRAIT_DISTRICT_CHUUNI_SOCIETY',
    Appeal,
    Housing,
    Entertainment,
    OnePerCity,
    AllowsHolyCity,
    Maintenance,
    AirSlots,
    CitizenSlots,
    TravelTime,
    CityStrengthModifier,
    AdjacentToLand,
    CanAttack,
    AdvisorType,
    CaptureRemovesDistrict,
    MaxPerPlayer
FROM Districts
WHERE DistrictType = 'DISTRICT_HOLY_SITE';

INSERT OR REPLACE INTO District_GreatPersonPoints
    (DistrictType, GreatPersonClassType, PointsPerTurn)
VALUES
    ('DISTRICT_CHUUNI_SOCIETY', 'GREAT_PERSON_CLASS_PROPHET', 2);

INSERT OR REPLACE INTO District_CitizenGreatPersonPoints
    (DistrictType, GreatPersonClassType, PointsPerTurn)
SELECT 'DISTRICT_CHUUNI_SOCIETY', GreatPersonClassType, PointsPerTurn
FROM District_CitizenGreatPersonPoints
WHERE DistrictType = 'DISTRICT_HOLY_SITE';

INSERT OR REPLACE INTO District_CitizenYieldChanges
    (DistrictType, YieldType, YieldChange)
SELECT 'DISTRICT_CHUUNI_SOCIETY', YieldType, YieldChange
FROM District_CitizenYieldChanges
WHERE DistrictType = 'DISTRICT_HOLY_SITE';

INSERT OR REPLACE INTO District_TradeRouteYields
    (DistrictType, YieldType, YieldChangeAsOrigin, YieldChangeAsDomesticDestination, YieldChangeAsInternationalDestination)
SELECT
    'DISTRICT_CHUUNI_SOCIETY',
    YieldType,
    YieldChangeAsOrigin,
    YieldChangeAsDomesticDestination,
    YieldChangeAsInternationalDestination
FROM District_TradeRouteYields
WHERE DistrictType = 'DISTRICT_HOLY_SITE';

INSERT OR REPLACE INTO District_Adjacencies (DistrictType, YieldChangeId)
SELECT 'DISTRICT_CHUUNI_SOCIETY', YieldChangeId
FROM District_Adjacencies
WHERE DistrictType = 'DISTRICT_HOLY_SITE';

INSERT INTO BuildingReplaces (CivUniqueBuildingType, ReplacesBuildingType)
VALUES
    ('BUILDING_CLUB_MAGIC_CIRCLE', 'BUILDING_SHRINE');

INSERT INTO Buildings (
    BuildingType,
    Name,
    Description,
    PrereqTech,
    PrereqDistrict,
    PurchaseYield,
    Cost,
    AdvisorType,
    Maintenance,
    CitizenSlots,
    Entertainment,
    TraitType
)
SELECT
    'BUILDING_CLUB_MAGIC_CIRCLE',
    'LOC_BUILDING_CLUB_MAGIC_CIRCLE_NAME',
    'LOC_BUILDING_CLUB_MAGIC_CIRCLE_DESCRIPTION',
    PrereqTech,
    'DISTRICT_HOLY_SITE',
    'YIELD_FAITH',
    Cost,
    AdvisorType,
    0,
    CitizenSlots,
    1,
    'TRAIT_BUILDING_CLUB_MAGIC_CIRCLE'
FROM Buildings
WHERE BuildingType = 'BUILDING_SHRINE';

UPDATE Buildings
SET Entertainment = 1,
    Maintenance = 0
WHERE BuildingType = 'BUILDING_CLUB_MAGIC_CIRCLE';

INSERT OR REPLACE INTO Building_YieldChanges
    (BuildingType, YieldType, YieldChange)
VALUES
    ('BUILDING_CLUB_MAGIC_CIRCLE', 'YIELD_FAITH', 2);

INSERT OR REPLACE INTO Building_GreatPersonPoints
    (BuildingType, GreatPersonClassType, PointsPerTurn)
VALUES
    ('BUILDING_CLUB_MAGIC_CIRCLE', 'GREAT_PERSON_CLASS_PROPHET', 1);

-- Building replacements do not satisfy the separate unit prerequisite table.
-- Copy the Shrine prerequisite so the Magic Circle unlocks Missionaries.
INSERT OR REPLACE INTO Unit_BuildingPrereqs
    (Unit, PrereqBuilding, NumSupported)
SELECT Unit, 'BUILDING_CLUB_MAGIC_CIRCLE', NumSupported
FROM Unit_BuildingPrereqs
WHERE Unit = 'UNIT_MISSIONARY'
  AND PrereqBuilding = 'BUILDING_SHRINE';

-- Give the Society +2 Faith for each exact Campus district type, including
-- unique Campus replacements already loaded by the Gathering Storm ruleset.
INSERT OR REPLACE INTO Adjacency_YieldChanges
    (ID, Description, YieldType, YieldChange, TilesRequired, AdjacentDistrict)
SELECT
    'CHUUNI_SOCIETY_CAMPUS_FAITH_' || CampusDistrictType,
    'LOC_CHUUNI_SOCIETY_FROM_CAMPUS_FAITH_DESCRIPTION',
    'YIELD_FAITH',
    2,
    1,
    CampusDistrictType
FROM (
    SELECT DistrictType AS CampusDistrictType
    FROM Districts
    WHERE DistrictType = 'DISTRICT_CAMPUS'
    UNION
    SELECT CivUniqueDistrictType
    FROM DistrictReplaces
    WHERE ReplacesDistrictType = 'DISTRICT_CAMPUS'
);

INSERT OR REPLACE INTO District_Adjacencies (DistrictType, YieldChangeId)
SELECT 'DISTRICT_CHUUNI_SOCIETY', ID
FROM Adjacency_YieldChanges
WHERE ID LIKE 'CHUUNI_SOCIETY_CAMPUS_FAITH_%';

INSERT OR REPLACE INTO Adjacency_YieldChanges
    (ID, Description, YieldType, YieldChange, TilesRequired, AdjacentWonder)
VALUES
    ('CHUUNI_SOCIETY_WONDER_FAITH',
     'LOC_CHUUNI_SOCIETY_FROM_WONDER_FAITH_DESCRIPTION',
     'YIELD_FAITH', 2, 1, 1);

INSERT OR REPLACE INTO District_Adjacencies (DistrictType, YieldChangeId)
VALUES
    ('DISTRICT_CHUUNI_SOCIETY', 'CHUUNI_SOCIETY_WONDER_FAITH');

INSERT OR REPLACE INTO Adjacency_YieldChanges
    (ID, Description, YieldType, YieldChange, TilesRequired, AdjacentDistrict)
VALUES
    ('CHUUNI_SOCIETY_TO_SCIENCE', 'LOC_CHUUNI_SOCIETY_TO_SCIENCE_DESCRIPTION', 'YIELD_SCIENCE', 2, 1, 'DISTRICT_CHUUNI_SOCIETY'),
    ('CHUUNI_SOCIETY_TO_CULTURE', 'LOC_CHUUNI_SOCIETY_TO_CULTURE_DESCRIPTION', 'YIELD_CULTURE', 2, 1, 'DISTRICT_CHUUNI_SOCIETY'),
    ('CHUUNI_SOCIETY_TO_PRODUCTION', 'LOC_CHUUNI_SOCIETY_TO_PRODUCTION_DESCRIPTION', 'YIELD_PRODUCTION', 2, 1, 'DISTRICT_CHUUNI_SOCIETY');

INSERT OR REPLACE INTO District_Adjacencies (DistrictType, YieldChangeId)
SELECT DistrictType, 'CHUUNI_SOCIETY_TO_SCIENCE'
FROM Districts
WHERE DistrictType = 'DISTRICT_CAMPUS'
UNION
SELECT CivUniqueDistrictType, 'CHUUNI_SOCIETY_TO_SCIENCE'
FROM DistrictReplaces
WHERE ReplacesDistrictType = 'DISTRICT_CAMPUS';

INSERT OR REPLACE INTO District_Adjacencies (DistrictType, YieldChangeId)
SELECT DistrictType, 'CHUUNI_SOCIETY_TO_CULTURE'
FROM Districts
WHERE DistrictType IN (
    'DISTRICT_THEATER',
    'DISTRICT_ENTERTAINMENT_COMPLEX',
    'DISTRICT_WATER_ENTERTAINMENT_COMPLEX'
)
UNION
SELECT CivUniqueDistrictType, 'CHUUNI_SOCIETY_TO_CULTURE'
FROM DistrictReplaces
WHERE ReplacesDistrictType IN (
    'DISTRICT_THEATER',
    'DISTRICT_ENTERTAINMENT_COMPLEX',
    'DISTRICT_WATER_ENTERTAINMENT_COMPLEX'
);

INSERT OR REPLACE INTO District_Adjacencies (DistrictType, YieldChangeId)
SELECT DistrictType, 'CHUUNI_SOCIETY_TO_PRODUCTION'
FROM Districts
WHERE DistrictType = 'DISTRICT_INDUSTRIAL_ZONE'
UNION
SELECT CivUniqueDistrictType, 'CHUUNI_SOCIETY_TO_PRODUCTION'
FROM DistrictReplaces
WHERE ReplacesDistrictType = 'DISTRICT_INDUSTRIAL_ZONE';
