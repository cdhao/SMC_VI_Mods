# Grace Ashcroft Troubleshooting Record

This note records the failure modes already investigated for the Grace Ashcroft
mod. It distinguishes a runtime registration defect from stale save metadata so
future changes do not reintroduce speculative fixes.

## Icon atlas registration

Symptoms included a `?` civilization emblem in world ranking, a missing
civilization icon in the city-state panel, and an oversized infected-blood
texture in the trade panel.

The final registration rules are:

1. Use a real image for every requested atlas size. The trade view requests
   50px; a 256px-only icon is not an acceptable fallback.
2. Delete old `IconTextureAtlases` and `IconDefinitions` for a custom icon
   before inserting the current mapping. `INSERT OR REPLACE` does not remove
   mappings under a different atlas name.
3. Keep the 22px resource font atlas separate from ordinary UI atlas sizes.
4. When changing a resource package, advance the integer asset version and use
   that version in the BLP name, XLP package name, texture entry prefix, and
   icon atlas names.

FireTuner confirms the runtime lookup rather than only proving that an SQL row
exists:

```lua
local x,y,t,s=IconManager:FindIconAtlasNearestSize("ICON_RESOURCE_INFECTED_BLOOD",50,true)
print("[Grace] requested=50 actual=",s,"texture=",t,"x=",x,"y=",y)
```

Expected result: `actual=50` and
`GraceResource_InfectedBlood_V2_50`.

## Front-end save selection

Old saves made while the civilization icon package was being iterated could show
blank emblem and leader images on their first selection in the Load Game screen.
Selecting another save caused the old view to refresh, which initially looked
like an atlas load-order problem.

Current evidence rules that out for the released V2 resources:

- FireTuner resolves the exact 50px emblem and leader entries even while an old
  save is blank.
- New saves made after the finalized package load correctly on their first
  selection after a full game restart.
- Civilization VI's base `LoadSaveMenu_Shared.lua` uses
  `UI.ApplyFileQueryLeaderImage` and `UI.ApplyFileQueryCivImage` before its
  static `SetIcon` fallback. This path consumes save-file metadata.

Therefore, do not change `LoadOrder`, BLP library registrations, or icon SQL to
work around an old-save-only symptom. Re-save the game after an icon package
version change and verify the current package with `IconManager`.

## FireTuner scope

The generic `[Lua State = FrontEnd]` console can inspect `IconManager`, but it
cannot access `Controls.CivIcon` or `Controls.LeaderIcon` from the nested
`LoadGameMenu` LuaContext. A `nil` `Controls.CivIcon` from that console is an
expected context boundary, not evidence that the icon is missing.

To inspect the return values of `ApplyFileQuery...` itself would require a
temporary replacement or instrumentation of the base `LoadGameMenu` UI script.
Do not add that invasive diagnostic unless a current-version save reproduces the
problem.

## DDS color channels

The Cooker TEX files use `PF_R8G8B8A8_UNORM`. Input DDS files must therefore
use matching RGBA channel order. A BGRA DDS can make a leader background appear
blue even when the PNG source is correct. The Python texture helper writes the
required RGBA format and the static checker verifies the leader-art DDS headers.
