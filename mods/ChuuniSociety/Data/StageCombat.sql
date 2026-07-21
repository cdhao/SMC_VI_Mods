INSERT INTO Modifiers (ModifierId, ModifierType)
VALUES
    ('CHUUNI_STAGE_1_COMBAT', 'MODIFIER_PLAYER_UNITS_ADJUST_COMBAT_STRENGTH');

INSERT INTO ModifierArguments (ModifierId, Name, Value)
VALUES
    ('CHUUNI_STAGE_1_COMBAT', 'Amount', 3);

INSERT INTO ModifierStrings (ModifierId, Context, Text)
VALUES
    ('CHUUNI_STAGE_1_COMBAT', 'Preview', 'LOC_CHUUNI_STAGE_1_COMBAT_PREVIEW');
