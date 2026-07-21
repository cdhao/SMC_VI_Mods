INSERT OR REPLACE INTO IconDefinitions (Name, Atlas, "Index")
SELECT 'ICON_CIVILIZATION_CHUUNI_SOCIETY', Atlas, "Index"
FROM IconDefinitions
WHERE Name = 'ICON_CIVILIZATION_JAPAN';

INSERT OR REPLACE INTO IconDefinitions (Name, Atlas, "Index")
SELECT 'CIVILIZATION_CHUUNI_SOCIETY', Atlas, "Index"
FROM IconDefinitions
WHERE Name = 'CIVILIZATION_JAPAN';

INSERT OR REPLACE INTO IconDefinitions (Name, Atlas, "Index")
SELECT 'ICON_LEADER_RIKKA_TAKANASHI', Atlas, "Index"
FROM IconDefinitions
WHERE Name = 'ICON_LEADER_HOJO';

INSERT OR REPLACE INTO IconDefinitions (Name, Atlas, "Index")
SELECT 'ICON_DISTRICT_CHUUNI_SOCIETY', Atlas, "Index"
FROM IconDefinitions
WHERE Name = 'ICON_DISTRICT_HOLY_SITE';

INSERT OR REPLACE INTO IconDefinitions (Name, Atlas, "Index")
SELECT 'ICON_DISTRICT_CHUUNI_SOCIETY_FOW', Atlas, "Index"
FROM IconDefinitions
WHERE Name = 'ICON_DISTRICT_HOLY_SITE_FOW';

INSERT OR REPLACE INTO IconDefinitions (Name, Atlas, "Index")
SELECT 'ICON_BUILDING_CLUB_MAGIC_CIRCLE', Atlas, "Index"
FROM IconDefinitions
WHERE Name = 'ICON_BUILDING_SHRINE';

INSERT OR REPLACE INTO IconDefinitions (Name, Atlas, "Index")
SELECT 'ICON_CHUUNI_VALUE', Atlas, "Index"
FROM IconDefinitions
WHERE Name = 'ICON_DISTRICT_HOLY_SITE';

-- Custom packages override the original-game aliases above. The aliases remain
-- first so database loading still has deterministic definitions during asset work.
INSERT OR REPLACE INTO IconTextureAtlases
    (Name, IconSize, IconsPerRow, IconsPerColumn, Filename)
VALUES
    ('ICON_ATLAS_CHUUNI_CIVILIZATION_V1', 22, 1, 1, 'ChuuniCivilization_V1_22'),
    ('ICON_ATLAS_CHUUNI_CIVILIZATION_V1', 30, 1, 1, 'ChuuniCivilization_V1_30'),
    ('ICON_ATLAS_CHUUNI_CIVILIZATION_V1', 32, 1, 1, 'ChuuniCivilization_V1_32'),
    ('ICON_ATLAS_CHUUNI_CIVILIZATION_V1', 36, 1, 1, 'ChuuniCivilization_V1_36'),
    ('ICON_ATLAS_CHUUNI_CIVILIZATION_V1', 38, 1, 1, 'ChuuniCivilization_V1_38'),
    ('ICON_ATLAS_CHUUNI_CIVILIZATION_V1', 44, 1, 1, 'ChuuniCivilization_V1_44'),
    ('ICON_ATLAS_CHUUNI_CIVILIZATION_V1', 45, 1, 1, 'ChuuniCivilization_V1_45'),
    ('ICON_ATLAS_CHUUNI_CIVILIZATION_V1', 48, 1, 1, 'ChuuniCivilization_V1_48'),
    ('ICON_ATLAS_CHUUNI_CIVILIZATION_V1', 50, 1, 1, 'ChuuniCivilization_V1_50'),
    ('ICON_ATLAS_CHUUNI_CIVILIZATION_V1', 64, 1, 1, 'ChuuniCivilization_V1_64'),
    ('ICON_ATLAS_CHUUNI_CIVILIZATION_V1', 80, 1, 1, 'ChuuniCivilization_V1_80'),
    ('ICON_ATLAS_CHUUNI_CIVILIZATION_V1', 128, 1, 1, 'ChuuniCivilization_V1_128'),
    ('ICON_ATLAS_CHUUNI_CIVILIZATION_V1', 200, 1, 1, 'ChuuniCivilization_V1_200'),
    ('ICON_ATLAS_CHUUNI_CIVILIZATION_V1', 256, 1, 1, 'ChuuniCivilization_V1_256'),
    ('ICON_ATLAS_CHUUNI_LEADER', 22, 1, 1, 'Chuuni_Icon_Rikka_22'),
    ('ICON_ATLAS_CHUUNI_LEADER', 30, 1, 1, 'Chuuni_Icon_Rikka_30'),
    ('ICON_ATLAS_CHUUNI_LEADER', 32, 1, 1, 'Chuuni_Icon_Rikka_32'),
    ('ICON_ATLAS_CHUUNI_LEADER', 38, 1, 1, 'Chuuni_Icon_Rikka_38'),
    ('ICON_ATLAS_CHUUNI_LEADER', 45, 1, 1, 'Chuuni_Icon_Rikka_45'),
    ('ICON_ATLAS_CHUUNI_LEADER', 48, 1, 1, 'Chuuni_Icon_Rikka_48'),
    ('ICON_ATLAS_CHUUNI_LEADER', 50, 1, 1, 'Chuuni_Icon_Rikka_50'),
    ('ICON_ATLAS_CHUUNI_LEADER', 55, 1, 1, 'Chuuni_Icon_Rikka_55'),
    ('ICON_ATLAS_CHUUNI_LEADER', 64, 1, 1, 'Chuuni_Icon_Rikka_64'),
    ('ICON_ATLAS_CHUUNI_LEADER', 80, 1, 1, 'Chuuni_Icon_Rikka_80'),
    ('ICON_ATLAS_CHUUNI_LEADER', 256, 1, 1, 'Chuuni_Icon_Rikka_256');

INSERT OR REPLACE INTO IconTextureAtlases
    (Name, IconSize, IconsPerRow, IconsPerColumn, Filename)
SELECT 'ICON_ATLAS_CHUUNI_GAMEPLAY', IconSize, 1, 1, 'Chuuni_Icon_SocietyDistrict_' || IconSize
FROM (SELECT 22 IconSize UNION SELECT 30 UNION SELECT 32 UNION SELECT 38 UNION SELECT 50 UNION SELECT 64 UNION SELECT 80 UNION SELECT 256);

INSERT OR REPLACE INTO IconTextureAtlases
    (Name, IconSize, IconsPerRow, IconsPerColumn, Filename)
VALUES
    ('ICON_ATLAS_CHUUNI_MAGIC_CIRCLE', 22, 1, 1, 'Chuuni_Icon_MagicCircle_22'),
    ('ICON_ATLAS_CHUUNI_MAGIC_CIRCLE', 30, 1, 1, 'Chuuni_Icon_MagicCircle_30'),
    ('ICON_ATLAS_CHUUNI_MAGIC_CIRCLE', 32, 1, 1, 'Chuuni_Icon_MagicCircle_32'),
    ('ICON_ATLAS_CHUUNI_MAGIC_CIRCLE', 38, 1, 1, 'Chuuni_Icon_MagicCircle_38'),
    ('ICON_ATLAS_CHUUNI_MAGIC_CIRCLE', 50, 1, 1, 'Chuuni_Icon_MagicCircle_50'),
    ('ICON_ATLAS_CHUUNI_MAGIC_CIRCLE', 64, 1, 1, 'Chuuni_Icon_MagicCircle_64'),
    ('ICON_ATLAS_CHUUNI_MAGIC_CIRCLE', 80, 1, 1, 'Chuuni_Icon_MagicCircle_80'),
    ('ICON_ATLAS_CHUUNI_MAGIC_CIRCLE', 256, 1, 1, 'Chuuni_Icon_MagicCircle_256');

INSERT OR REPLACE INTO IconTextureAtlases
    (Name, IconSize, IconsPerRow, IconsPerColumn, Filename)
SELECT 'ICON_ATLAS_CHUUNI_CHIMERA', IconSize, 1, 1, 'Chuuni_Icon_Chimera_' || IconSize
FROM (SELECT 22 IconSize UNION SELECT 30 UNION SELECT 32 UNION SELECT 38 UNION SELECT 50 UNION SELECT 64 UNION SELECT 80 UNION SELECT 256);

INSERT OR REPLACE INTO IconTextureAtlases
    (Name, IconSize, IconsPerRow, IconsPerColumn, Filename)
SELECT 'ICON_ATLAS_CHUUNI_BOUNDARY', IconSize, 1, 1, 'Chuuni_Icon_InvisibleBoundary_' || IconSize
FROM (SELECT 22 IconSize UNION SELECT 30 UNION SELECT 32 UNION SELECT 38 UNION SELECT 50 UNION SELECT 64 UNION SELECT 80 UNION SELECT 256);

INSERT OR REPLACE INTO IconTextureAtlases
    (Name, IconSize, IconsPerRow, IconsPerColumn, Filename)
VALUES
    ('ICON_ATLAS_CHUUNI_VALUE', 22, 1, 1, 'Chuuni_Icon_ChuuniValue_22'),
    ('ICON_ATLAS_CHUUNI_VALUE', 38, 1, 1, 'Chuuni_Icon_ChuuniValue_38'),
    ('ICON_ATLAS_CHUUNI_VALUE', 50, 1, 1, 'Chuuni_Icon_ChuuniValue_50'),
    ('ICON_ATLAS_CHUUNI_VALUE', 64, 1, 1, 'Chuuni_Icon_ChuuniValue_64'),
    ('ICON_ATLAS_CHUUNI_VALUE', 256, 1, 1, 'Chuuni_Icon_ChuuniValue_256');

INSERT OR REPLACE INTO IconTextureAtlases
    (Name, Baseline, IconSize, IconsPerRow, IconsPerColumn, Filename)
VALUES
    ('ICON_ATLAS_CHUUNI_CIVILIZATION_FONT_V1', 6, 22, 1, 1, 'ChuuniCivilization_V1_22');

INSERT OR REPLACE INTO IconDefinitions (Name, Atlas, "Index") VALUES
    ('ICON_CIVILIZATION_CHUUNI_SOCIETY', 'ICON_ATLAS_CHUUNI_CIVILIZATION_V1', 0),
    ('CIVILIZATION_CHUUNI_SOCIETY', 'ICON_ATLAS_CHUUNI_CIVILIZATION_FONT_V1', 0),
    ('ICON_LEADER_RIKKA_TAKANASHI', 'ICON_ATLAS_CHUUNI_LEADER', 0),
    ('ICON_DISTRICT_CHUUNI_SOCIETY', 'ICON_ATLAS_CHUUNI_GAMEPLAY', 0),
    ('ICON_DISTRICT_CHUUNI_SOCIETY_FOW', 'ICON_ATLAS_CHUUNI_GAMEPLAY', 0),
    ('ICON_BUILDING_CLUB_MAGIC_CIRCLE', 'ICON_ATLAS_CHUUNI_MAGIC_CIRCLE', 0),
    ('ICON_CHUUNI_VALUE', 'ICON_ATLAS_CHUUNI_VALUE', 0),
    ('ICON_GOVERNOR_CHIMERA', 'ICON_ATLAS_CHUUNI_CHIMERA', 0),
    ('ICON_IMPROVEMENT_INVISIBLE_BOUNDARY', 'ICON_ATLAS_CHUUNI_BOUNDARY', 0),
    ('ICON_CHUUNI_TELEPORT_ACTION', 'ICON_ATLAS_CHUUNI_MAGIC_CIRCLE', 0);
