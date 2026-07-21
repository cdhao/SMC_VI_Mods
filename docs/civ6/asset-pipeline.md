# Asset Pipeline

## Ownership boundaries

`assets/<Mod>/source` stores editable PNG and source art. `generated` stores
derived review PNG/DDS. `cooker` stores DDS/TEX/XLP inputs, logs, and temporary
Cooked BLP output. `projects/<Mod>` stores optional ModBuddy files. Only
`mods/<Mod>` is deployed to Civilization VI.

The runtime folder may contain BLP, ArtDefs, SQL, Lua, `.dep`, and `.modinfo`.
It must not contain `Images`, `XLPs`, `Logs`, `.tex`, `.xlp`, source art, or
ModBuddy project files. `tools/common/civ6_static_checks.py` enforces this.

## Manifest and versions

Each Mod uses `assets/<Mod>/mod-build.toml`. It is the source of truth for:

* Mod release version.
* Asset revision.
* Asset/runtime/project paths.
* Cooked BLP package names.

Use an integer asset revision when a static resource needs cache separation.
New packages must include the Mod namespace and revision, for example
`MyModResourceIconsV2`. Do not manually repeat this version in Python,
PowerShell, SQL, XLP, or checks.

Computer-specific paths are not stored in TOML. Set `CIV6_SDK_ROOT` or
`CIV6_ASSET_COOKER` in the shell environment, or pass the explicit command-line
argument to the Cook script.

## Texture contract

The shared DDS writer emits uncompressed RGBA DDS matching the TEX declaration
`PF_R8G8B8A8_UNORM`. A BGRA DDS with an RGBA TEX declaration can tint a full
screen blue. Verify the actual DDS masks, not only the image appearance.

For custom resource icons, supply the exact sizes requested by each consumer.
Grace uses a normal UI atlas including 38/50/64/256 and a separate 22px font
atlas with the correct baseline. The diplomacy trade UI specifically exposed a
missing exact 50px mapping.

## Cook and runtime verification

The pipeline is:

```text
PNG -> generated DDS + TEX -> XLP -> Asset Cooker -> BLP -> .dep -> Icon atlas SQL
```

Use `python tools/<mod>/cook_assets.py --dry-run` before running the SDK. It
must print exactly the BLP packages expected by the manifest. After Cook,
validate the runtime folder and test the actual UI. `IconManager` can resolve a
name while a consumer still uses a fallback image, so test the precise requested
size:

```lua
local x,y,t,s=IconManager:FindIconAtlasNearestSize("ICON_RESOURCE_INFECTED_BLOOD",50,true)
print("requested=50 actual=",s,"texture=",t,"x=",x,"y=",y)
```

Expected behavior is `actual=50`, not a fallback 256px texture.
