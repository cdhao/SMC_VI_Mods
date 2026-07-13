# Civilization VI Mod Asset Workflow

This repository uses **one dedicated tool directory per mod** and keeps the shared layer intentionally small.

## Repository layout

```text
assets/<ModName>/
  source/       editable source images
  generated/    generated PNG/DDS intermediates
  cooker/       Asset Cooker pantry, TEX, XLP, logs, and temporary BLP output

projects/<ModName>/
  *.civ6sln     ModBuddy solution
  *.civ6proj    ModBuddy project linked to assets/ and mods/
  *.Art.xml     ModBuddy art specification

mods/<ModName>/
  ArtDefs/      runtime ArtDef files
  Platforms/Windows/BLPs/  cooked runtime packages
  Data/ Icons/ Scripts/ Text/  runtime database, Lua, and localization
  *.dep *.modinfo            runtime manifests

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
3. The build script generates PNG/DDS intermediates plus cooker TEX/XLP inputs under `assets/<ModName>/cooker`.
4. Cook from `assets/<ModName>/cooker`; never use `mods/<ModName>` as the pantry.
5. Confirm the expected BLP files were created in the cooker output and copy only those BLP files into `mods/<ModName>/Platforms/Windows/BLPs`.
6. Remove temporary cooker DDS inputs from the cooker workspace.
7. Confirm the runtime mod contains no TEX, XLP, cooker logs, or ModBuddy project files.
8. Run the mod-specific Python static checker. The PowerShell command remains a
   compatibility wrapper for existing local workflows.
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
8. Add only the cooked BLP files to `.modinfo`; TEX and XLP are build inputs and stay outside the runtime mod.
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

## Tool ownership

Use Python for deterministic validation: reading text contracts, inspecting DDS
headers, checking BLP entry strings, and confirming the runtime directory has no
build inputs. Keep PowerShell for Windows-specific orchestration: running Asset
Cooker, deploying a Mod directory, and cleaning temporary workspace files.

For Grace Ashcroft, the canonical validation command is:

```powershell
python tools/grace_ashcroft/check_static.py
```

`tools/grace_ashcroft/check_static.ps1` and the root-level checker are retained
only as compatibility entry points; they forward to the Python checker.
