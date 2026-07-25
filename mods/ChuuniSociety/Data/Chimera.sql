-- Chimera governor technical prototype.
--
-- Stage one grants one dedicated Governor point from gameplay Lua. The local
-- UI immediately appoints Chimera, so the player's ordinary available title
-- count is unchanged. The four-stage governed-city effects are intentionally
-- deferred until this real Governor survives the in-game spike.

INSERT INTO Types (Type, Kind) VALUES
    ('GOVERNOR_CHIMERA', 'KIND_GOVERNOR'),
    ('GOVERNOR_PROMOTION_CHIMERA_BASE', 'KIND_GOVERNOR_PROMOTION');

INSERT INTO Governors
    (GovernorType, Name, Description, IdentityPressure, Title, ShortTitle,
     TransitionStrength, AssignCityState, Image, PortraitImage,
     PortraitImageSelected, TraitType)
VALUES
    ('GOVERNOR_CHIMERA',
     'LOC_GOVERNOR_CHIMERA_NAME',
     'LOC_GOVERNOR_CHIMERA_DESCRIPTION',
     8,
     'LOC_GOVERNOR_CHIMERA_TITLE',
     'LOC_GOVERNOR_CHIMERA_SHORT_TITLE',
     500,
     0,
     'GOVERNOR_DISTRICT_PRODUCTION_MANAGER',
     'GovernorNormal_Builder',
     'GovernorSelected_Builder',
     'TRAIT_CIVILIZATION_CHUUNI_SOCIETY');

INSERT INTO Governors_XP2 (GovernorType, AssignToMajor)
VALUES ('GOVERNOR_CHIMERA', 1);

INSERT INTO GovernorPromotions
    (GovernorPromotionType, Name, Description, Level, Column, BaseAbility)
VALUES
    ('GOVERNOR_PROMOTION_CHIMERA_BASE',
     'LOC_GOVERNOR_PROMOTION_CHIMERA_BASE_NAME',
     'LOC_GOVERNOR_PROMOTION_CHIMERA_BASE_DESCRIPTION',
     0, 1, 1);

INSERT INTO GovernorPromotionSets (GovernorType, GovernorPromotion)
VALUES ('GOVERNOR_CHIMERA', 'GOVERNOR_PROMOTION_CHIMERA_BASE');

INSERT INTO Modifiers
    (ModifierId, ModifierType, RunOnce, Permanent)
VALUES
    ('CHUUNI_CHIMERA_GOVERNOR_POINT',
     'MODIFIER_PLAYER_ADJUST_GOVERNOR_POINTS',
     1,
     1);

INSERT INTO ModifierArguments (ModifierId, Name, Value)
VALUES ('CHUUNI_CHIMERA_GOVERNOR_POINT', 'Delta', 1);
