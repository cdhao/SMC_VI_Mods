# Civilization VI Mod Foundation

This is the current, reusable process for a custom civilization plus leader.
Read it before copying Grace Ashcroft or starting a new Mod.

1. [Asset pipeline](asset-pipeline.md): source artwork through Cooked BLP files.
2. [Runtime patterns](runtime-patterns.md): SQL/Lua ownership and multiplayer scope.
3. [Troubleshooting](troubleshooting.md): known Civ6 failure modes and probes.
4. [Release checklist](release-checklist.md): repeatable pre-test and release checks.

The Grace documents under `docs/mods/` are the detailed incident record. The
older RE9 design and historical plans under `docs/superpowers/` preserve design
history; they are not the current implementation contract.

For a new workspace use:

```powershell
python tools/scaffold_civ6_leader_mod.py MyNewMod "My New Civilization"
```

The scaffold creates `assets/`, `mods/`, `projects/`, and `tools/` ownership
roots. It does not invent gameplay SQL, leader artwork, or BLP content; those
remain design-specific work.

For routine shared-tool regression checks, run:

```powershell
powershell -ExecutionPolicy Bypass -File tools/run_civ6_tool_tests.ps1
```

This entry point uses `python -B` and performs the restricted cache cleanup in
`finally`; normal test runs therefore do not need a separate `-WhatIf` step.
