-- Fantasy combat modifiers are permanently attached once by ChuuniGameplay.lua
-- when their corresponding stage unlocks. Chuuni Value itself is a player
-- Property and does not use the resource system.

INSERT INTO Modifiers (ModifierId, ModifierType, Permanent)
VALUES
    ('CHUUNI_FANTASY_COMBAT_STAGE_1', 'MODIFIER_PLAYER_UNITS_ADJUST_COMBAT_STRENGTH', 1),
    ('CHUUNI_FANTASY_COMBAT_STAGE_2', 'MODIFIER_PLAYER_UNITS_ADJUST_COMBAT_STRENGTH', 1),
    ('CHUUNI_FANTASY_COMBAT_STAGE_3', 'MODIFIER_PLAYER_UNITS_ADJUST_COMBAT_STRENGTH', 1);

INSERT INTO ModifierArguments (ModifierId, Name, Value)
VALUES
    ('CHUUNI_FANTASY_COMBAT_STAGE_1', 'Amount', 3),
    ('CHUUNI_FANTASY_COMBAT_STAGE_2', 'Amount', 2),
    ('CHUUNI_FANTASY_COMBAT_STAGE_3', 'Amount', 3);

INSERT INTO ModifierStrings (ModifierId, Context, Text)
VALUES
    ('CHUUNI_FANTASY_COMBAT_STAGE_1', 'Preview', 'LOC_CHUUNI_FANTASY_COMBAT_STAGE_1_PREVIEW'),
    ('CHUUNI_FANTASY_COMBAT_STAGE_2', 'Preview', 'LOC_CHUUNI_FANTASY_COMBAT_STAGE_2_PREVIEW'),
    ('CHUUNI_FANTASY_COMBAT_STAGE_3', 'Preview', 'LOC_CHUUNI_FANTASY_COMBAT_STAGE_3_PREVIEW');
