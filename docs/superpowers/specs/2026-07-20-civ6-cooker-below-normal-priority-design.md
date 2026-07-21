# Civ6 Asset Cooker Below-Normal Priority Design

## Goal

On Windows, launch only the official `Civ6AssetCooker_FinalRelease.exe` process with `BELOW_NORMAL_PRIORITY_CLASS` so interactive input remains responsive while assets cook.

## Scope

- Apply the priority flag in the shared `cook_xlp` launcher so Grace and Chuuni behave consistently.
- Keep package ordering, output paths, validation, and failure propagation unchanged.
- Do not lower the priority of Python asset generation or static checks.
- Keep non-Windows behavior unchanged.
- Do not add package selection, parallelism, or locking.

## Verification

- A focused unit test records the `subprocess.run` call and verifies the Windows creation flag.
- Existing cooker-plan and unified Civ6 tool tests continue to pass.
