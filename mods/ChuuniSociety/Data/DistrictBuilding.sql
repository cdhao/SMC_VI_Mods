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

INSERT INTO TraitModifiers (TraitType, ModifierId)
VALUES
    ('TRAIT_DISTRICT_CHUUNI_SOCIETY', 'CHUUNI_SOCIETY_ADJACENT_CAMPUS_FAITH');

INSERT INTO Modifiers
    (ModifierId, ModifierType, SubjectRequirementSetId)
VALUES
    ('CHUUNI_SOCIETY_ADJACENT_CAMPUS_FAITH', 'MODIFIER_PLAYER_DISTRICTS_ADJUST_YIELD_CHANGE', 'CHUUNI_SOCIETY_ADJACENT_CAMPUS_REQUIREMENTS');

INSERT INTO ModifierArguments (ModifierId, Name, Value) VALUES
    ('CHUUNI_SOCIETY_ADJACENT_CAMPUS_FAITH', 'YieldType', 'YIELD_FAITH'),
    ('CHUUNI_SOCIETY_ADJACENT_CAMPUS_FAITH', 'Amount', 3);

INSERT INTO Requirements (RequirementId, RequirementType) VALUES
    ('CHUUNI_REQUIRES_DISTRICT_IS_SOCIETY', 'REQUIREMENT_DISTRICT_TYPE_MATCHES'),
    ('CHUUNI_REQUIRES_PLOT_ADJACENT_CAMPUS', 'REQUIREMENT_PLOT_ADJACENT_DISTRICT_TYPE_MATCHES');

INSERT INTO RequirementArguments (RequirementId, Name, Value) VALUES
    ('CHUUNI_REQUIRES_DISTRICT_IS_SOCIETY', 'DistrictType', 'DISTRICT_CHUUNI_SOCIETY'),
    ('CHUUNI_REQUIRES_PLOT_ADJACENT_CAMPUS', 'DistrictType', 'DISTRICT_CAMPUS');

INSERT INTO RequirementSets (RequirementSetId, RequirementSetType)
VALUES
    ('CHUUNI_SOCIETY_ADJACENT_CAMPUS_REQUIREMENTS', 'REQUIREMENTSET_TEST_ALL');

INSERT INTO RequirementSetRequirements (RequirementSetId, RequirementId) VALUES
    ('CHUUNI_SOCIETY_ADJACENT_CAMPUS_REQUIREMENTS', 'CHUUNI_REQUIRES_DISTRICT_IS_SOCIETY'),
    ('CHUUNI_SOCIETY_ADJACENT_CAMPUS_REQUIREMENTS', 'CHUUNI_REQUIRES_PLOT_ADJACENT_CAMPUS');

INSERT OR REPLACE INTO Adjacency_YieldChanges
    (ID, Description, YieldType, YieldChange, TilesRequired, AdjacentDistrict)
VALUES
    ('CHUUNI_SOCIETY_TO_SCIENCE', 'LOC_CHUUNI_SOCIETY_TO_SCIENCE_DESCRIPTION', 'YIELD_SCIENCE', 2, 1, 'DISTRICT_CHUUNI_SOCIETY'),
    ('CHUUNI_SOCIETY_TO_CULTURE', 'LOC_CHUUNI_SOCIETY_TO_CULTURE_DESCRIPTION', 'YIELD_CULTURE', 2, 1, 'DISTRICT_CHUUNI_SOCIETY'),
    ('CHUUNI_SOCIETY_TO_GOLD', 'LOC_CHUUNI_SOCIETY_TO_GOLD_DESCRIPTION', 'YIELD_GOLD', 2, 1, 'DISTRICT_CHUUNI_SOCIETY'),
    ('CHUUNI_SOCIETY_TO_PRODUCTION', 'LOC_CHUUNI_SOCIETY_TO_PRODUCTION_DESCRIPTION', 'YIELD_PRODUCTION', 2, 1, 'DISTRICT_CHUUNI_SOCIETY'),
    ('CHUUNI_SOCIETY_TO_FAITH', 'LOC_CHUUNI_SOCIETY_TO_FAITH_DESCRIPTION', 'YIELD_FAITH', 2, 1, 'DISTRICT_CHUUNI_SOCIETY');

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
WHERE DistrictType = 'DISTRICT_THEATER'
UNION
SELECT CivUniqueDistrictType, 'CHUUNI_SOCIETY_TO_CULTURE'
FROM DistrictReplaces
WHERE ReplacesDistrictType = 'DISTRICT_THEATER';

INSERT OR REPLACE INTO District_Adjacencies (DistrictType, YieldChangeId)
SELECT DistrictType, 'CHUUNI_SOCIETY_TO_GOLD'
FROM Districts
WHERE DistrictType IN ('DISTRICT_COMMERCIAL_HUB', 'DISTRICT_HARBOR')
UNION
SELECT CivUniqueDistrictType, 'CHUUNI_SOCIETY_TO_GOLD'
FROM DistrictReplaces
WHERE ReplacesDistrictType IN ('DISTRICT_COMMERCIAL_HUB', 'DISTRICT_HARBOR');

INSERT OR REPLACE INTO District_Adjacencies (DistrictType, YieldChangeId)
SELECT DistrictType, 'CHUUNI_SOCIETY_TO_PRODUCTION'
FROM Districts
WHERE DistrictType = 'DISTRICT_INDUSTRIAL_ZONE'
UNION
SELECT CivUniqueDistrictType, 'CHUUNI_SOCIETY_TO_PRODUCTION'
FROM DistrictReplaces
WHERE ReplacesDistrictType = 'DISTRICT_INDUSTRIAL_ZONE';

INSERT OR REPLACE INTO District_Adjacencies (DistrictType, YieldChangeId)
SELECT DistrictType, 'CHUUNI_SOCIETY_TO_FAITH'
FROM Districts
WHERE DistrictType = 'DISTRICT_HOLY_SITE'
UNION
SELECT CivUniqueDistrictType, 'CHUUNI_SOCIETY_TO_FAITH'
FROM DistrictReplaces
WHERE ReplacesDistrictType = 'DISTRICT_HOLY_SITE';
