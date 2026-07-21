# Chuuni Society Asset Pipeline Design

## Scope

Build a self-contained Civilization VI asset pipeline for the ten approved files in `assets/ChuuniSociety`. The Chuuni mod may reuse Grace Ashcroft's proven build architecture, but it must not reference Grace icon atlases, BLPs, ArtDefs, or runtime files.

## Source and generated boundaries

- The ten user-supplied PNGs and `素材文件 记录用/` remain source/reference files and are never overwritten.
- `processed/` contains normalized master PNGs such as the transparent white civilization emblem.
- `generated/` contains size-specific PNG and DDS outputs.
- `cooker/` contains temporary DDS inputs plus TEX and XLP definitions for the official Asset Cooker.
- `mods/ChuuniSociety/` contains only runtime SQL, ArtDefs, DEP and cooked BLP packages.

## Image preparation

- Convert `文明 Logo.png` from black background to a white RGBA emblem using luminance as alpha; retain anti-aliased edges and add 8 percent safe padding.
- Preserve the shared image for the Magic Circle building and teleport action.
- Preserve the deliberate white outline on the Rikka loading foreground.
- Normalize transparent gameplay icons onto an 8 percent safe canvas before size generation.
- Keep leader and governor portraits as full square compositions.
- Convert the loading background to opaque RGBA and compose a 2048x1024 loading scene with Rikka on the left, leaving the bright magic circle visible on the right.

## Runtime packages

- `ChuuniUITextureV1.blp` contains loading art and every UI/icon texture.
- `ChuuniLeaderFallbacks.blp` contains the diplomacy fallback foreground.
- `ChuuniSociety.dep` registers the UITexture and LeaderFallback libraries.
- `FallbackLeaders.artdef` maps `LEADER_RIKKA_TAKANASHI` to `FALLBACK_NEUTRAL_RIKKA_TAKANASHI`.
- Original Japan, Hojo, Holy Site, Shrine and Niter mappings remain the pre-cook safety fallback; cooked custom definitions replace them in the same icon update.

## Verification

- Unit tests cover black-to-alpha extraction, icon safe padding, manifest-driven package names, expected icon entries and loading composition dimensions.
- Static checks validate source inventory, generated DDS RGBA headers, XLP entries, DEP/ArtDef registrations, manifest file inventory and BLP entry presence.
- The build command must be repeatable and must not modify source PNG timestamps or contents.
