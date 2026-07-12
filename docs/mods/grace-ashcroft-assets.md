# Grace Ashcroft Asset Notes

## Tool entry points

Canonical commands:

```powershell
python tools/grace_ashcroft/build_assets.py
powershell -ExecutionPolicy Bypass -File tools/grace_ashcroft/cook_assets.ps1
powershell -ExecutionPolicy Bypass -File tools/grace_ashcroft/check_static.ps1
powershell -ExecutionPolicy Bypass -File tools/grace_ashcroft/deploy.ps1
```

Compatibility commands remain available:

```powershell
python tools/build_grace_icon_assets.py
powershell -ExecutionPolicy Bypass -File tools/check_grace_mod_static.ps1
```

## Package responsibilities

### `GraceUITexture.blp`

Contains:

- Grace loading background and foreground assets;
- leader icons;
- project icons;
- other general Grace UI textures.

It must not contain the civilization-emblem or infected-blood texture entries.

### `GraceCivilizationIconsV2.blp`

Contains only the Elpis Protocol civilization emblem at the UI sizes registered by
`ICON_ATLAS_GRACE_CIVILIZATION_V2` and the 22px font-icon entry registered by
`ICON_ATLAS_GRACE_CIVILIZATION_FONT_V2`.

### `GraceResourceIconsV2.blp`

Contains only:

```text
GraceResource_InfectedBlood_V2_22
GraceResource_InfectedBlood_V2_38
GraceResource_InfectedBlood_V2_50
GraceResource_InfectedBlood_V2_64
GraceResource_InfectedBlood_V2_256
```

Ordinary UI atlas:

```text
ICON_ATLAS_GRACE_INFECTED_BLOOD_V2
38 / 50 / 64 / 256
```

Font atlas:

```text
ICON_ATLAS_GRACE_INFECTED_BLOOD_FONT_V2
22px, Baseline 6
```

The resource package version is controlled only by:

```python
INFECTED_BLOOD_ASSET_VERSION = 2
```

The package name and texture entry prefix are derived from this value.

## Obsolete asset cleanup

`cleanup_obsolete_infected_blood_assets()` runs before generation. It removes stale files matching:

```text
GraceAshcroft_Icon_InfectedBlood_*
GraceResource_InfectedBlood_V*_*
GraceResourceIconsV*.xlp
GraceResourceIconsV*.blp
```

Current-version files are preserved. Cleanup covers generated PNG/DDS files, mod TEX files, temporary cooker DDS files, and obsolete versioned resource packages.

## BLP loading

`GraceAshcroft.dep` loads three UITexture packages:

```text
GraceUITexture.blp
GraceCivilizationIconsV2.blp
GraceResourceIconsV2.blp
```

After changing XLP, TEX, BLP, atlas, or entry names, fully restart Civilization VI before testing.

## First front-end icon load investigation

Observed behavior:

- On a fresh Civilization VI launch, the Elpis Protocol emblem can be blank when a save or city-state panel is opened for the first time.
- Selecting another save and returning, or entering a game before opening the same front-end view, makes the emblem appear.
- The colored icon backing is present while the emblem texture is blank.

The static registration chain is complete: the front-end player data references
`ICON_CIVILIZATION_ELPIS_PROTOCOL`, the icon definition points to the civilization atlas,
the atlas points to versioned texture entries, and the XLP, BLP, DEP, and Modinfo contain
those entries. This makes a damaged source image or missing atlas registration unlikely.

The current working hypothesis is that `GraceCivilizationIconsV2.blp` is not yet available
to the first front-end texture lookup. This is not a confirmed root cause. Candidate variables
are front-end action ordering, separate UITexture package registration, and differences between
the hand-maintained Art specification and generated DEP data.

Validation must change one variable at a time:

1. Keep all assets unchanged and explicitly order only the front-end actions: Art `0`, Icons `10`, Config and Colors `20`.
2. If that does not resolve a fresh-process first lookup, merge the civilization entries back into `GraceUITexture.blp` for an A/B test.
3. If the package test does not resolve it, generate a complete DEP with ModBuddy and compare its consumers, libraries, package order, and `LoadsLibraries` values before replacing the current DEP.

Do not lower the in-game `GraceGameplay` action from LoadOrder `1000` as part of this front-end experiment.

## Audio

`Civilizations.artdef` binds `CIVILIZATION_ELPIS_PROTOCOL` to the built-in China civilization audio using:

```xml
<m_Value text="China"/>
<m_ParamName text="XrefName"/>
```

This is independent of the custom UI texture packages.

## Runtime acceptance

The diplomacy trade view requests a 50px resource icon. Final validation should resolve:

```text
ICON_RESOURCE_INFECTED_BLOOD
requestedSize = 50
actualSize = 50
textureName = GraceResource_InfectedBlood_V2_50
```
