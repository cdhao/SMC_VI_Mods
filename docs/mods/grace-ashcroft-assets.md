# Grace Ashcroft Asset Notes

## Tool entry points

Canonical commands:

```powershell
python tools/grace_ashcroft/build_assets.py
powershell -ExecutionPolicy Bypass -File tools/grace_ashcroft/cook_assets.ps1
python tools/grace_ashcroft/check_static.py
powershell -ExecutionPolicy Bypass -File tools/grace_ashcroft/deploy.ps1
```

Compatibility commands remain available:

```powershell
python tools/build_grace_icon_assets.py
powershell -ExecutionPolicy Bypass -File tools/check_grace_mod_static.ps1
```

## Directory responsibilities

```text
assets/GraceAshcroft/source       editable source images
assets/GraceAshcroft/generated    generated review PNG/DDS files
assets/GraceAshcroft/cooker       cooker Images, TEX, XLP, logs, and temporary BLP output
projects/GraceAshcroft            ModBuddy solution, project, and Art specification
mods/GraceAshcroft                deployable runtime files only
```

`mods/GraceAshcroft` intentionally contains no `Images`, `XLPs`, cooker logs,
`.tex`, `.xlp`, `.civ6proj`, `.civ6sln`, or `.Art.xml`. Runtime texture loading uses
the cooked BLP packages listed in `GraceAshcroft.dep` and `GraceAshcroft.modinfo`.

The PowerShell checker remains valid for compatibility, but only forwards to the
Python checker:

```powershell
powershell -ExecutionPolicy Bypass -File tools/grace_ashcroft/check_static.ps1
```

## Package responsibilities

### `GraceUITexture.blp`

Contains:

- Grace loading background and foreground assets;
- civilization emblem entries;
- leader icons;
- project icons;
- other general Grace UI textures.

It must not contain the infected-blood texture entries. The civilization emblem is
kept in this main package.

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

Current-version files are preserved. Cleanup covers generated PNG/DDS files, cooker TEX/DDS files, and obsolete versioned runtime packages.

## BLP loading

`GraceAshcroft.dep` loads two UITexture packages:

```text
GraceUITexture.blp
GraceResourceIconsV2.blp
```

After changing XLP, TEX, BLP, atlas, or entry names, fully restart Civilization VI before testing.

## Icon registration and save-list behavior

Verified in game after replacing `INSERT OR REPLACE INTO IconTextureAtlases` with
explicit atlas deletion followed by ordinary insertion:

- world-ranking civilization emblems resolve correctly;
- city-state relationship leader icons resolve correctly;
- exact 50px runtime atlas lookups resolve after a cold game start.

The temporary first-click save-list blank icon was reproduced only with saves created
before the current resource and civilization icon packages were finalized. New saves made
with the current V2 asset set load their civilization emblem and leader icon normally on a
cold front-end start. Treat an old save as stale metadata during asset-package iteration;
do not change atlas SQL or action LoadOrder based only on that old-save symptom.

Use `IconManager:FindIconAtlasNearestSize` in FireTuner to distinguish an actual
registration problem from save metadata. The current runtime contract requires the
infected-blood trade icon to resolve exactly to the V2 50px entry.

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
