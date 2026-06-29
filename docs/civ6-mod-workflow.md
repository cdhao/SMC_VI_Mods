# Civilization VI Mod Asset Workflow

This repository uses **one dedicated tool directory per mod** and keeps the shared layer intentionally small.

## Repository layout

```text
assets/<ModName>/
  source/       editable source images
  generated/    generated PNG/DDS intermediates

mods/<ModName>/
  ArtDefs/      runtime ArtDef files
  Images/       TextureInstance files and temporary cooker DDS inputs
  XLPs/         XLP package definitions
  Platforms/Windows/BLPs/  cooked runtime packages

tools/common/   low-level helpers without mod-specific names
tools/<mod>/    build, validation, cook, and deploy scripts for one mod
docs/mods/      mod-specific asset notes
```

Do not put source PNG files or generated cooker intermediates in the final mod directory unless the game actually loads them.

## What belongs in `tools/common`

Only stable, mod-independent operations belong in the common layer, for example:

- writing RGBA DDS files;
- alpha-bound cropping and icon resizing;
- generating a generic TextureInstance XML document.

Civilization names, leader names, package names, atlas names, icon lists, and cleanup rules stay in the dedicated mod tool directory.

## Standard asset flow

1. Put editable images under `assets/<ModName>/source`.
2. Run the mod-specific `build_assets.py`.
3. The build script generates PNG/DDS intermediates, TextureInstance `.tex` files, and XLP entries.
4. Keep required DDS inputs in `mods/<ModName>/Images` while cooking.
5. Cook the XLP packages with `Civ6AssetCooker_FinalRelease.exe`.
6. Confirm the expected BLP files were created.
7. Remove temporary cooker DDS inputs.
8. Run the mod-specific static checker.
9. Deploy by deleting the old installed mod directory and copying the complete new directory.
10. Fully restart Civilization VI when icon SQL, XLP, BLP, or package names change.

## Adding a resource icon package

A custom resource normally needs two icon paths:

- ordinary UI atlas sizes such as `38/50/64/256`;
- a separate 22px font atlas with an appropriate `Baseline`.

Recommended sequence:

1. Choose a unique integer asset version.
2. Derive the XLP package name, BLP name, texture entry prefix, and atlas names from that version.
3. Generate every required size as an actual image of that size.
4. Put the ordinary sizes in one atlas.
5. Put the 22px entry in a separate font atlas.
6. Delete old `IconDefinitions` before inserting the new mapping because the icon database key includes both icon name and atlas.
7. Add the new BLP to the mod `.dep` UITexture library.
8. Add the XLP, BLP, and TEX files to `.modinfo`.
9. Verify every texture entry name exists inside the cooked BLP.
10. Verify runtime selection with `IconManager:FindIconAtlasNearestSize` when diagnosing size fallback.

## Naming rules

The following values must be unique between mods:

- Mod GUID;
- `CIVILIZATION_*` and `LEADER_*` types;
- XLP `PackageName` and BLP filename;
- texture entry names;
- icon atlas names;
- fallback leader entry names.

Use integer resource versions such as `V1`, `V2`, and `V3`. Do not mix decimal-style resource names such as `1.1` with the Civ VI mod version field.

## Compatibility entry points

Older root-level tool commands may remain as thin wrappers while scripts move into `tools/<mod>/`. New documentation and automation should use the mod-specific paths.
