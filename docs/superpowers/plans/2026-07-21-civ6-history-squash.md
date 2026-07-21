# Civ6 History Squash Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace every local `main` commit after `7b70d08e2ca303b6f6e5b6a6258d05bfd0030b64` with one commit while preserving the exact final tree.

**Architecture:** Create a local backup branch at the current HEAD, then soft-reset `main` to the remote baseline and recommit the already-final tree as one snapshot. Compare Git tree IDs before and after the rewrite, then run the repository's unified Civ6 validation. No remote refs are updated.

**Tech Stack:** Git, PowerShell, Python-based Civ6 validation.

## Global Constraints

- Baseline commit is exactly `7b70d08e2ca303b6f6e5b6a6258d05bfd0030b64`.
- `origin/main` must still equal the baseline before rewriting history.
- The working tree and index must be clean before creating the backup branch.
- Backup branch is exactly `backup/pre-squash-20260721` and remains local.
- Final commit message is exactly `feat: add shared Civ6 tooling and Chuuni Society mod`.
- The pre-squash and post-squash tree IDs must be identical.
- Do not push, force-push, delete the backup branch, expire reflogs, or run Git garbage collection.

---

### Task 1: Guard and Snapshot the Existing History

**Files:**
- Verify: `.git/refs/remotes/origin/main`
- Create: local ref `.git/refs/heads/backup/pre-squash-20260721`

**Interfaces:**
- Consumes: clean local `main`, exact remote baseline.
- Produces: a local recovery branch and recorded pre-squash tree ID.

- [ ] **Step 1: Verify every rewrite precondition**

Run:

```powershell
$baseline = '7b70d08e2ca303b6f6e5b6a6258d05bfd0030b64'
if ((git branch --show-current) -ne 'main') { throw 'Expected branch main.' }
if ((git rev-parse origin/main) -ne $baseline) { throw 'origin/main moved from the approved baseline.' }
if (git status --porcelain) { throw 'Working tree or index is not clean.' }
git show-ref --verify --quiet refs/heads/backup/pre-squash-20260721
if ($LASTEXITCODE -eq 0) { throw 'Backup branch already exists.' }
```

Expected: no output and exit code `0`. Any thrown message stops execution before history changes.

- [ ] **Step 2: Create the local backup branch**

Run:

```powershell
git branch backup/pre-squash-20260721 HEAD
```

Expected: branch creation succeeds without changing `main` or the working tree.

- [ ] **Step 3: Record the exact source tree**

Run:

```powershell
$beforeTree = git rev-parse 'backup/pre-squash-20260721^{tree}'
"BEFORE_TREE=$beforeTree"
```

Expected: one 40-character tree ID. Preserve it for Task 2.

---

### Task 2: Replace the Post-Baseline History with One Commit

**Files:**
- Rewrite: local `main` commits after `7b70d08e2ca303b6f6e5b6a6258d05bfd0030b64`
- Preserve: complete working tree represented by `backup/pre-squash-20260721`

**Interfaces:**
- Consumes: backup branch and `$beforeTree` from Task 1.
- Produces: one new commit whose parent is the baseline and whose tree equals `$beforeTree`.

- [ ] **Step 1: Soft-reset only the current branch pointer**

Run:

```powershell
git reset --soft 7b70d08e2ca303b6f6e5b6a6258d05bfd0030b64
```

Expected: all final differences since the baseline are staged; the working-tree files remain unchanged.

- [ ] **Step 2: Confirm the staged snapshot equals the backup tree**

Run:

```powershell
$stagedTree = git write-tree
$beforeTree = git rev-parse 'backup/pre-squash-20260721^{tree}'
"STAGED_TREE=$stagedTree"
"BEFORE_TREE=$beforeTree"
if ($stagedTree -ne $beforeTree) { throw 'Staged tree differs from backup tree; stop before commit.' }
```

Expected: both tree IDs are identical.

- [ ] **Step 3: Create the single replacement commit**

Run:

```powershell
git commit -m "feat: add shared Civ6 tooling and Chuuni Society mod"
```

Expected: exactly one new commit is created on `main`.

- [ ] **Step 4: Verify graph and tree invariants**

Run:

```powershell
$baseline = '7b70d08e2ca303b6f6e5b6a6258d05bfd0030b64'
$beforeTree = git rev-parse 'backup/pre-squash-20260721^{tree}'
$afterTree = git rev-parse 'main^{tree}'
$commitCount = git rev-list --count "$baseline..main"
$parent = git rev-parse 'main^'
"BEFORE_TREE=$beforeTree"
"AFTER_TREE=$afterTree"
"COMMITS_AFTER_BASELINE=$commitCount"
"MAIN_PARENT=$parent"
if ($afterTree -ne $beforeTree) { throw 'Post-squash tree differs from backup tree.' }
if ($commitCount -ne '1') { throw 'Expected exactly one commit after baseline.' }
if ($parent -ne $baseline) { throw 'Replacement commit parent is not the approved baseline.' }
git diff --exit-code backup/pre-squash-20260721 main
```

Expected: identical tree IDs, commit count `1`, parent equal to the baseline, and no diff output.

---

### Task 3: Validate the Rewritten Branch

**Files:**
- Verify: repository working tree and all Civ6 mod/tooling files.

**Interfaces:**
- Consumes: rewritten `main` from Task 2.
- Produces: test evidence and a push-ready fast-forward branch.

- [ ] **Step 1: Run the unified Civ6 validation**

Run:

```powershell
powershell -ExecutionPolicy Bypass -File tools/run_civ6_tool_tests.ps1
```

Expected: all unit tests, Grace validation, Chuuni asset validation, and Chuuni gameplay validation pass; temporary cache directories are removed.

- [ ] **Step 2: Verify final repository state**

Run:

```powershell
git diff --check
git status --short
git rev-list --left-right --count origin/main...main
git log --oneline --decorate -3
```

Expected: no whitespace errors, clean status, divergence `0 1`, and `main` containing one replacement commit directly above `origin/main`.

- [ ] **Step 3: Report without pushing**

Report the new commit ID, backup branch name, unchanged tree ID, passing test count, and that ordinary `git push origin main` is available but was not run.
