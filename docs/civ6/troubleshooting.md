# Troubleshooting Record

| Symptom | Evidence to collect | Usual cause | Rule going forward |
| --- | --- | --- | --- |
| First load screen is blue | Inspect DDS channel masks and loading XML controls | BGRA DDS paired with RGBA TEX, or game tint on foreground | Use shared RGBA DDS writer; loading screen uses composed scene background plus transparent foreground when needed. |
| Resource huge in trade UI | `FindIconAtlasNearestSize(..., 50, true)` | No exact 50px UI entry or stale Atlas mapping | Cook the exact size; split 22px font Atlas; delete old icon mappings before inserting current definitions. |
| Civilization or leader icon is a question mark | FireTuner in FrontEnd and in-game; inspect actual requested size | UI Atlas/BLP not loaded, wrong entry name, or stale save metadata | Verify `.dep`, BLP, atlas SQL, and a newly created save. Do not diagnose current registration from old iteration saves. |
| Icon works in one UI but not another | Compare consumer requested size and Atlas package | Different UIs ask for different icon sizes or use separate async paths | Register all required sizes, then test consumers separately. |
| Static checker cannot import `tools.common` | Run checker as `python tools/<mod>/check_static.py` | Repository root missing from `sys.path` | Script entry points add repository root before shared imports. |
| Mod fails during database load | Search `Database.log` for first Gameplay error | Invalid SQL, often a null inserted into non-null field | Fix the first database error; general UI messages are not sufficient evidence. |

FireTuner has separate `FrontEnd` and `InGame` Lua states. A top-level
`Controls.CivIcon` is normally nil in FireTuner because it is not executing
inside the nested Load Game context. `IconManager` probes remain useful, but
they do not prove that a specific control has refreshed.
