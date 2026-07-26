# Civilization VI Icon Registration and Circular UI

Use this checklist when a custom production, leader, building, district or
Governor icon resolves to original artwork, appears square inside a round
control, or disappears after cooking.

## Register one logical icon deterministically

`IconDefinitions` is keyed by both `Name` and `Atlas`. An
`INSERT OR REPLACE` with a new atlas therefore does not remove an older row
using the same logical icon name. The UI may then choose either mapping.

For Mod-owned icons:

1. Delete existing `IconDefinitions` rows by the complete owned-name list.
2. Delete existing `IconTextureAtlases` rows by the complete owned-atlas list.
3. Insert the current atlas inventory.
4. Insert exactly one definition for every logical icon name.

Production rows request `"ICON_" .. item.Type`. For example,
`BUILDING_CLUB_MAGIC_CIRCLE` needs one unambiguous
`ICON_BUILDING_CLUB_MAGIC_CIRCLE` definition.

## Register every Governor channel

Governors use several independent channels:

- `Governors.PortraitImage`;
- `Governors.PortraitImageSelected`;
- `ICON_<GovernorType>`;
- `ICON_<GovernorType>_FILL`;
- `ICON_<GovernorType>_SLOT`.

The direct portrait entries normally need a cooked 512px UITexture. Small
normal, Fill and Slot definitions may share artwork for an initial version,
but all names must exist.

## Bake circular alpha into circular artwork

Civ6 round controls do not reliably mask a square texture. Generate the
texture with transparent corners and an antialiased circular alpha edge.
Validate both:

- all four corner alpha values are zero;
- the alpha channel contains partial values between 0 and 255.

This applies to leader portraits and building or action icons shown inside
round controls.

## Verify the cooked package

- Every XLP entry has exactly one TEX and one source DDS.
- Required sizes are present, including 512px Governor portraits.
- The BLP contains every expected entry ID.
- An isolated UI recook changes only the UI BLP; compare SHA-256 for unrelated
  packages before and after.
- Restart Civilization VI completely after icon SQL or BLP changes.

For live diagnosis, use FireTuner to probe
`IconManager:FindIconAtlasNearestSize(iconName, size)` for each logical name
and size used by the failing UI.
