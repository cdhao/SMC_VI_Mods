# Chuuni Icon and Governor Registration Fixes Design

**Date:** 2026-07-26  
**Status:** Approved design, pending implementation

## Scope

Fix three verified runtime defects in `ChuuniSociety`:

1. Chimera uses an original-game Governor portrait or unresolved city-banner
   icon instead of its custom artwork.
2. Society district and Magic Circle production icons can resolve to stale
   original-game atlas definitions.
3. Chimera can be assigned to other major civilizations instead of only the
   local player's cities.

Also make the Magic Circle icon use the same antialiased circular alpha rule as
the Rikka leader icon, and preserve the investigation as reusable Civ6
documentation.

## Root Causes

### Duplicate icon definitions

`IconDefinitions` has the composite primary key `(Name, Atlas)`. Therefore,
`INSERT OR REPLACE` only replaces a row when both the icon name and atlas name
match.

`ChuuniIcons.sql` first copies original-game definitions for the custom names
and later inserts custom-atlas definitions with the same names. Both rows remain
valid. UI calls such as:

```lua
kInstance.Icon:SetIcon("ICON_" .. kItem.Type)
```

then have more than one atlas mapping for the same logical icon. The production
panel can resolve the stale original-game mapping instead of the custom package.

### Governor UI uses multiple independent image channels

The Governor screens do not rely on one `ICON_GOVERNOR_*` definition:

- `GovernorPanel.lua` and `GovernorDetailsPanel.lua` read
  `Governors.PortraitImage` and `Governors.PortraitImageSelected` as direct
  UITexture entry names.
- `CityPanelCulture.lua` reads `ICON_<GovernorType>`.
- `GovernorAssignmentChooser.lua` and `CityBannerManager.lua` read
  `ICON_<GovernorType>_FILL` and `ICON_<GovernorType>_SLOT`.

The current Chimera row points both portrait columns to the original Builder
Governor textures and only registers `ICON_GOVERNOR_CHIMERA`. The selected,
fill and slot channels are absent.

### `AssignToMajor` expands the assignment list

`GovernorAssignmentChooser.lua` always lists the local player's cities.
`Governors_XP2.AssignToMajor=1` additionally enumerates met major
civilizations and offers their capitals. Chimera currently sets this flag to
`1`.

## Approved Design

### Deterministic icon registration

Before inserting Chuuni atlases and definitions:

1. Delete all Chuuni-owned `IconDefinitions` by icon name.
2. Delete all Chuuni-owned `IconTextureAtlases` by atlas name.
3. Insert the complete current atlas inventory.
4. Insert exactly one definition for every Chuuni icon name.

Do not seed custom icon names by copying original-game definitions. Runtime
fallback aliases are removed because they create ambiguous mappings after the
custom package exists.

Static and schema tests must prove that the Society district and Magic Circle
each have exactly one definition and that it references the expected Chuuni
atlas.

### Circular icon preprocessing

`build_assets.py` applies the existing supersampled circular alpha mask to:

- `Chuuni_Icon_Rikka`;
- `Chuuni_Icon_MagicCircle`.

The RGB artwork remains unchanged inside the circle. Four corners must be fully
transparent and the circular edge must contain partial alpha values for
antialiasing.

The rule is recorded as a reusable UI constraint: artwork displayed in a
circular Civ6 control must contain circular alpha in the texture itself; a
square source cannot rely on the control to mask it.

### Chimera portrait and city icon channels

The existing `奇美拉总督头像.png` remains the only source artwork.

- Generate and cook a 512px `Chuuni_Icon_Chimera_512` UITexture entry.
- Set both `PortraitImage` and `PortraitImageSelected` to that entry.
- Register `ICON_GOVERNOR_CHIMERA`,
  `ICON_GOVERNOR_CHIMERA_FILL`, and
  `ICON_GOVERNOR_CHIMERA_SLOT`.
- The three small-icon names share the current Chimera atlas and artwork in
  this version.

Separate dark Slot and colored Fill artwork is explicitly deferred. It can be
added later if the in-game establishment meter needs more visual distinction.

### Chimera assignment scope

Set `Governors_XP2.AssignToMajor` to `0`.

Keep:

- `Governors.AssignCityState=0`;
- the original one-turn transition design;
- assignment to every city owned by the local player.

Chimera must not list foreign major capitals or city-states.

### Cooker isolation

Only the UI package is recooked:

```powershell
python -B tools/chuuni_society/cook_assets.py --package ui
```

Record the LeaderFallback BLP SHA-256 before and after cooking and require it to
remain unchanged.

## Reusable Documentation

Add a shared Civ6 document under `docs/civ6/` covering:

- the `(Name, Atlas)` `IconDefinitions` key;
- why `INSERT OR REPLACE` does not remove stale atlas mappings;
- delete-then-insert registration;
- production item naming (`ICON_` plus item type);
- Governor portrait, normal icon, Fill and Slot channels;
- circular alpha preprocessing;
- exact-size and BLP inventory checks;
- FireTuner `IconManager:FindIconAtlasNearestSize` probes;
- the need for a full game restart after changing icon SQL or a cooked package.

Link the document from `docs/civ6/README.md`.

## Verification

Automated verification:

1. Tests fail before implementation for duplicate definitions, missing Governor
   channels, square Magic Circle corners, missing Chimera 512 entry and
   `AssignToMajor=1`.
2. Gameplay schema execution confirms:
   - one Society definition using `ICON_ATLAS_CHUUNI_GAMEPLAY`;
   - one Magic Circle definition using
     `ICON_ATLAS_CHUUNI_MAGIC_CIRCLE`;
   - all three Chimera icon definitions;
   - Chimera portrait columns use the custom 512 entry;
   - `AssignCityState=0` and `AssignToMajor=0`.
3. Asset tests confirm circular Rikka and Magic Circle alpha and the Chimera
   512 texture entry.
4. Chuuni gameplay and asset static checks pass.
5. Only `ChuuniUITextureV1.blp` changes during cooking.
6. Deployment file counts and SHA-256 hashes match the repository runtime mod.

In-game verification remains required:

- Society and Magic Circle production rows show their custom icons.
- Magic Circle is circular without square corners.
- Governor panel and details panel show Chimera.
- City panel, assignment chooser and city banner resolve Chimera icons.
- Chimera lists only the player's own cities.

Until those checks pass, affected status-table entries remain
`已实现未实机验证`.
