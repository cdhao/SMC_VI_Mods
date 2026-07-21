# Chuuni Property and Popup HUD Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Chuuni Value's strategic-resource storage with persistent player Properties, attach staged combat modifiers once at permanent unlock, and replace the large HUD panel with a compact LaunchBar-style button that opens a native in-game popup.

**Architecture:** `CHUUNI_VALUE` and `CHUUNI_STAGE` are the only live progression values. Gameplay Lua owns value changes and one-time modifier attachment; SQL only defines the three permanent `+3/+2/+3` combat modifiers. The independent UI context reads Properties, visually sits below the original LaunchBar hooks without replacing `TopPanel` or `LaunchBar`, and builds a fresh `PopupDialogInGame` on every click.

**Tech Stack:** Civilization VI Gathering Storm SQL/XML/Lua, native `PopupDialogInGame`, Python 3.11 `unittest` static contracts.

## Global Constraints

- Do not migrate old development saves from `RESOURCE_CHUUNI_VALUE`; new games start from `CHUUNI_VALUE=0`.
- Never use `tonumber(player:GetProperty(...))`; assign `GetProperty` results to locals first.
- Preserve stage thresholds `1/20/50/100`, religion gates for stages 2-4, and combat totals `3/5/8/8`.
- Preserve modifier IDs, `+3/+2/+3` arguments and Preview strings.
- Do not replace or copy `TopPanel` or `LaunchBar`; reuse only original sizes and textures.
- Hide the button for non-Chuuni, observers and invalid local players.

---

### Task 1: Property progression and one-time combat attachment

**Files:**
- Modify: `tools/far_east_magic_nap_society/tests/test_check_static.py`
- Modify: `mods/ChuuniSociety/Scripts/ChuuniGameplay.lua`
- Modify: `mods/ChuuniSociety/Data/Core.sql`
- Modify: `mods/ChuuniSociety/Data/StageCombat.sql`
- Modify: `tools/far_east_magic_nap_society/check_static.py`

**Interfaces:**
- Produces: `CHUUNI_VALUE`, `CHUUNI_LAST_VALUE_TICK_TURN`, `CHUUNI_STAGE_n_COMBAT_ATTACHED` player Properties.
- Produces: idempotent `EnsureStageCombatModifier(player, stage)`.

- [ ] Add failing contracts requiring Property reads/writes, three attachment guards, permanent modifiers, and forbidding the old resource/requirements/trait attachments.
- [ ] Run the focused tests and verify failure against the current resource implementation.
- [ ] Remove the resource type, resource consumption and resource-count parameters from `Core.sql`; add `CHUUNI_VALUE_PER_DISTRICT/BUILDING`.
- [ ] Change Gameplay Lua to clamp and persist `CHUUNI_VALUE`, rename the tick Property, and attach each stage modifier exactly once before marking its attachment Property.
- [ ] Reduce `StageCombat.sql` to three permanent modifiers, arguments and Preview strings.
- [ ] Run the focused tests and Expansion2 schema execution.

### Task 2: Compact LaunchBar-style button

**Files:**
- Modify: `tools/far_east_magic_nap_society/tests/test_check_static.py`
- Modify: `mods/ChuuniSociety/UI/ChuuniStatusHUD.xml`
- Modify: `mods/ChuuniSociety/UI/ChuuniStatusHUD.lua`
- Modify: `mods/ChuuniSociety/Icons/ChuuniIcons.sql`

**Interfaces:**
- Produces controls: `ChuuniStatusRoot`, `ChuuniStatusButton`, `ChuuniStatusIcon`, `ChuuniValueBadge`, `ChuuniValueText`.
- Consumes: local-player `CHUUNI_VALUE` and `CHUUNI_STAGE` Properties.

- [ ] Add failing contracts for the five compact controls, `ICON_CHUUNI_VALUE`, Property reads and absence of the old large HUD controls/resource reads.
- [ ] Run the focused UI contract and verify failure.
- [ ] Replace the large panel with one independent 49px button using original LaunchBar hook dimensions/textures and a small value badge.
- [ ] Anchor the independent root visually below the original LaunchBar hooks without importing or replacing their context.
- [ ] Refresh only visibility, badge text and compact tooltip on existing UI events.
- [ ] Run focused tests and XML parsing.

### Task 3: Native status popup

**Files:**
- Modify: `tools/far_east_magic_nap_society/tests/test_check_static.py`
- Modify: `mods/ChuuniSociety/UI/ChuuniStatusHUD.lua`
- Modify: `mods/ChuuniSociety/Text/Chuuni_zh_Hans_CN.sql`

**Interfaces:**
- Produces: `GetStatusModel(player)`, `BuildPopupText(status)`, `OpenChuuniPopup()`.
- Uses: `PopupDialogInGame:new`, `AddTitle`, `AddText`, `AddConfirmButton`, `Open`.

- [ ] Add failing contracts for the native Popup API, click callback, dynamic Property model, four-stage overview and close text.
- [ ] Run the focused popup contract and verify failure.
- [ ] Build a fresh status model and popup body on every click; never cache player values or append to an already-open popup.
- [ ] Register the button click and mouse-over callbacks and retain all existing visibility/refresh events.
- [ ] Replace resource localization with button, popup, condition and stage-overview localization.
- [ ] Run focused tests and the Chuuni static checker.

### Task 4: Documentation, deployment and in-game gate

**Files:**
- Modify: `docs/superpowers/plans/2026-07-19-chuuni-society-v0.1.md`

- [ ] Mark Property/Popup HUD as `已实现未实机验证` and record that old resource-based development saves are unsupported.
- [ ] Run all 17+ Chuuni-focused tests, schema execution, static checker, XML parsing and `git diff --check`.
- [ ] Commit the isolated refactor and deploy only `mods/ChuuniSociety`.
- [ ] Verify deployed hashes for Gameplay Lua, StageCombat SQL, HUD XML/Lua and localization.
- [ ] In game, verify button placement with BBG, popup repeat-open behavior, coastal `0→5`, per-turn gain, stage combat `3/5/8/8`, and save/reload without duplicate modifiers.
