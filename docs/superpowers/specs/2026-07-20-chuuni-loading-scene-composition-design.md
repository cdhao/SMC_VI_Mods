# Chuuni Loading Scene Composition Design

## Goal

Move Rikka to the right side of the loading screen and reduce her size slightly, while preserving the working in-game leader presentation.

## Composition

- Change only the precomposited `Chuuni_LoadingScene` image.
- Resize the `1024x2048` tracked foreground source to `480x960` with LANCZOS resampling.
- Alpha-composite it onto the `2048x1024` loading background at `(1280, 32)`.
- Do not sharpen the first revision; avoid introducing halos around translucent hair and hand edges.

The foreground's visible alpha region will occupy approximately `x=1331..1745` and `y=33..990`, keeping it clear of the central loading text panel.

## Preserved Behavior

- Keep `Chuuni_Foreground` at `1024x2048` for the in-game player screen and leader fallback.
- Keep loading, fallback, TEX/XLP identifiers, BLP package names, and gameplay data unchanged.
- Rebuild, cook with the official SDK, validate, and redeploy `ChuuniSociety` after the composition change.

## Verification

- Add a regression test for the exact loading-scene scale and placement.
- Verify the standalone foreground output remains byte-identical to the tracked source pixels.
- Run the unified Civ6 tests and static checks.
- Cook both Chuuni packages with the official SDK and deploy the verified runtime mod.
