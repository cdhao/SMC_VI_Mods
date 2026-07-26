# Chuuni District, Magic Circle, Adjacency and Portrait Fixes

**Date:** 2026-07-26  
**Status:** Approved design, pending implementation plan

## Goal

Fix the four gameplay and presentation defects confirmed in the current
`ChuuniSociety` runtime:

1. the Far East Magic Nap Society district has no world model;
2. the Clubroom Magic Circle replaces the Shrine but does not unlock
   Missionaries;
3. the Society adjacency breakdown uses obsolete rules and hides one bonus in
   description text instead of the normal adjacency UI;
4. Rikka's leader icon is packed as an opaque square rather than a circular
   portrait.

The Chuuni Value popup layout is explicitly outside this change.

## Confirmed Root Causes

### District model

`ChuuniSociety` currently registers only `FallbackLeaders.artdef`. Its art
project and `.dep` contain no `Districts.artdef` consumer or dependency, so the
custom district database row has no world-view or strategic-view art mapping.

### Missionary prerequisite

The base game unlocks `UNIT_MISSIONARY` through:

```text
Unit_BuildingPrereqs:
UNIT_MISSIONARY -> BUILDING_SHRINE
```

`BuildingReplaces` does not make a unique replacement satisfy that separate
table automatically. The Magic Circle therefore needs its own prerequisite
row while remaining a Shrine replacement.

### Adjacency display

The current SQL still implements an obsolete rule:

```text
adjacent to at least one Campus -> fixed +3 Faith Modifier
```

That Modifier is not a native per-neighbor adjacency entry, so it is described
in text rather than represented correctly in the adjacency breakdown. The same
file also grants obsolete bonuses to Commercial Hubs, Harbors and Holy Sites.
Because the Holy Site receiver query includes Holy Site replacements, it makes
Society-to-Society adjacency incorrectly display an extra +2 Faith.

### Leader portrait

`tools/chuuni_society/build_assets.py` explicitly marks
`Chuuni_Icon_Rikka` as `square`. The generated PNG and DDS therefore retain
opaque pixels in all four corners. The official Cooker packages the supplied
texture correctly; the defect is in preprocessing, not BLP cooking.

## Selected Design

### 1. Inherit the Holy Site model

Add `mods/ChuuniSociety/ArtDefs/Districts.artdef` following the proven
`GraceAshcroft` district-reference pattern, but cross-reference the base Holy
Site assets:

```text
Landmark: DISTRICT_HOLY_SITE
StrategicView completed: HolySite
StrategicView pillaged: HolySite_Pillaged
StrategicView construction: HolySite_UnderConstruction
Audio: Build_District_HolySite
Ambience: PLAY/STOP_AMBIENCE_DISTRICT_HOLYSITE
```

Register the ArtDef for `Audio`, `StrategicView_Translate` and
`WorldView_Translate` in `ChuuniSociety.Art.xml`, and synchronize the matching
consumer and dependency entries in `ChuuniSociety.dep`. Add the ArtDef to
`ChuuniSociety.modinfo`.

No new 3D asset or BLP package is required for this inheritance.

### 2. Keep the Magic Circle as a Shrine replacement

Preserve:

```text
BUILDING_CLUB_MAGIC_CIRCLE replaces BUILDING_SHRINE
```

Add:

```text
UNIT_MISSIONARY -> BUILDING_CLUB_MAGIC_CIRCLE
```

by copying the base Missionary/Shrine `NumSupported` value into
`Unit_BuildingPrereqs`. Do not turn the Magic Circle into an additional
standalone building.

### 3. Replace obsolete adjacency logic with native adjacency rows

Keep every original Holy Site adjacency rule already copied to
`DISTRICT_CHUUNI_SOCIETY`, including Natural Wonders, Mountains, Woods,
district-count adjacency, Government Plaza and other Gathering Storm rules.

Remove the fixed +3 Campus Modifier and its Requirement objects.

Add native `Adjacency_YieldChanges` entries so the Society receives:

```text
each adjacent Campus or Campus replacement: +2 Faith
each adjacent World Wonder: +2 Faith
```

Use one native row per exact Campus district type where necessary so unique
Campus replacements count and every neighbor is represented in the standard
adjacency UI.

Add reciprocal native adjacency entries:

```text
Campus and Campus replacements: +2 Science
Theater Square and replacements: +2 Culture
Entertainment Complex and replacements: +2 Culture
Water Park and replacements: +2 Culture
Industrial Zone and replacements: +2 Production
```

Do not grant extra adjacency to:

```text
Commercial Hub
Harbor
Holy Site
Far East Magic Nap Society
```

Another Society may still count as an ordinary district for the inherited
Holy Site rule “every two adjacent districts: +1 Faith”, but it must not
trigger a new per-Society +2 Faith entry.

Update the district description and adjacency localization so the text matches
the native breakdown.

### 4. Generate a circular Rikka icon and cook only the UI package

Add a dedicated leader-circle preprocessing mode:

1. fit the existing leader source to a square without changing its composition;
2. apply an antialiased circular alpha mask;
3. leave all four corner pixels fully transparent;
4. preserve the portrait inside the circle without adding a decorative ring.

Regenerate every registered Rikka leader-icon size.

Extend `tools/chuuni_society/cook_assets.py` with a package selector so this
change cooks only `ChuuniUITextureV1`. Do not recook
`ChuuniLeaderFallbacks`, because neither loading art nor its XLP changes.

## Validation

### Automated

Add or update contracts that verify:

- `Districts.artdef` exists and references the exact Holy Site world,
  strategic, audio and ambience entries;
- `.Art.xml`, `.dep` and `.modinfo` register the new ArtDef;
- the Magic Circle Missionary prerequisite exists;
- the fixed +3 Modifier and obsolete Requirement set are absent;
- native Campus/Wonder and reciprocal adjacency rows are present;
- Commercial Hub, Harbor and Holy Site do not receive the new reciprocal
  entries;
- SQL executes against the installed Gathering Storm schema;
- generated Rikka PNG corner alpha values are zero and the center remains
  visible;
- the selective Cooker plan targets only `ChuuniUITextureV1`;
- the resulting runtime BLP contains every registered Rikka icon entry.

### In-game

Use a new game or a fresh test save and verify:

1. completed, under-construction and pillaged Societies display the Holy Site
   model/strategic view;
2. a city with a Magic Circle can faith-purchase a Missionary;
3. original Holy Site adjacency remains;
4. one and two adjacent Campuses give +2 and +4 Faith respectively;
5. each adjacent World Wonder gives +2 Faith;
6. Campus, Theater Square, Entertainment Complex, Water Park and Industrial
   Zone receive their corresponding +2;
7. Commercial Hub, Harbor and Holy Site receive no new bonus;
8. Society-to-Society adjacency has no per-neighbor +2 Faith line;
9. Rikka appears circular in the top panel and other leader-icon consumers;
10. loading-screen and in-game fallback art remain unchanged.

## Delivery Boundary

This change does not redesign the Chuuni Value popup, add new custom 3D art,
alter Chuuni stage balance, or implement later Chimera abilities. Any UI popup
cleanup remains a separate follow-up.
