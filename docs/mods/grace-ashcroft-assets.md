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
- civilization and leader icons;
- project icons;
- other general Grace UI textures.

It must not contain the infected-blood texture entries.

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

`GraceAshcroft.dep` loads both UITexture packages:

```text
GraceUITexture.blp
GraceResourceIconsV2.blp
```

After changing XLP, TEX, BLP, atlas, or entry names, fully restart Civilization VI before testing.

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
