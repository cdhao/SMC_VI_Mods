# Release Checklist

1. Update only `assets/<Mod>/mod-build.toml` for release and asset revisions.
2. Run `powershell -ExecutionPolicy Bypass -File tools/run_civ6_tool_tests.ps1`.
   It uses `python -B` to avoid creating `__pycache__` and always runs the
   restricted workspace cleanup in `finally`, including on test failure.
3. Run `python tools/<mod>/cook_assets.py --dry-run`; confirm every package is namespaced and versioned where needed.
4. Cook with a configured `CIV6_SDK_ROOT` or explicit Cooker path.
5. Run `python tools/<mod>/check_static.py` and the PowerShell compatibility wrapper if one is kept.
6. Confirm `mods/<Mod>` has no source assets, DDS/TEX/XLP, cooker logs, or ModBuddy project files.
7. Start a new game and create a new save after asset changes. Do not use old test saves as the only icon test.
8. Test leader select, world ranking, city-state relationship, technology/civic trees, resource tooltip, diplomacy trade, loading screen, and diplomacy scene.
9. For resource icons, probe every important size with FireTuner and record `actual` size and texture name.
10. Check `Database.log`, `Modding.log`, and Lua runtime errors before calling a feature complete.
