# Civ6 Asset Cooker Below-Normal Priority Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Launch the official Civ6 Asset Cooker below normal priority on Windows without changing any other build behavior.

**Architecture:** Keep Grace and Chuuni orchestration unchanged. Add the Windows creation flag only at the shared `cook_xlp` subprocess boundary, which is the single place both mods launch `Civ6AssetCooker_FinalRelease.exe`.

**Tech Stack:** Python 3 standard library (`subprocess`, `unittest`, `unittest.mock`), PowerShell validation wrapper.

## Global Constraints

- Only the official Asset Cooker process receives `BELOW_NORMAL_PRIORITY_CLASS`.
- Python generation and static-check subprocesses retain their current priority.
- Package ordering, package selection, locking, output paths, and non-Windows behavior do not change.

---

### Task 1: Lower the official Cooker process priority on Windows

**Files:**
- Create: `tools/common/tests/test_civ6_asset_cooker.py`
- Modify: `tools/common/civ6_asset_cooker.py:71`

**Interfaces:**
- Consumes: `cook_xlp(paths: AssetCookerPaths, *, cooker_root: Path, xlp_name: str) -> None`
- Produces: the same interface, with a Windows-only subprocess creation flag.

- [ ] **Step 1: Write the failing test**

```python
@unittest.skipUnless(os.name == "nt", "Windows priority contract")
def test_cooker_starts_below_normal_priority_on_windows(self) -> None:
    paths = AssetCookerPaths(Path("Civ6AssetCooker_FinalRelease.exe"), Path("Civ6.cfg"))
    with mock.patch("tools.common.civ6_asset_cooker.subprocess.run") as run:
        cook_xlp(paths, cooker_root=Path("cooker"), xlp_name="UI.xlp")
    self.assertEqual(
        run.call_args.kwargs["creationflags"],
        subprocess.BELOW_NORMAL_PRIORITY_CLASS,
    )
```

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```powershell
python -B -m unittest tools.common.tests.test_civ6_asset_cooker -v
```

Expected: failure because the current `subprocess.run` call has no `creationflags` keyword.

- [ ] **Step 3: Add the minimal Windows creation flag**

```python
creationflags = subprocess.BELOW_NORMAL_PRIORITY_CLASS if os.name == "nt" else 0
subprocess.run(
    command,
    cwd=cooker_root,
    check=True,
    creationflags=creationflags,
)
```

- [ ] **Step 4: Run focused and unified verification**

Run:

```powershell
python -B -m unittest tools.common.tests.test_civ6_asset_cooker -v
powershell -ExecutionPolicy Bypass -File tools\run_civ6_tool_tests.ps1
git diff --check
```

Expected: focused test passes, unified Civ6 tests and static checks exit `0`, and diff check emits no errors.

- [ ] **Step 5: Commit**

```powershell
git add tools/common/civ6_asset_cooker.py tools/common/tests/test_civ6_asset_cooker.py
git commit -m "fix(civ6): lower asset cooker priority"
```
