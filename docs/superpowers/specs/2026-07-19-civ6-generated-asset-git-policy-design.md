# Civ6 可再生资产 Git 管理设计

## 目标

Git 只管理资产源文件、构建定义和模组运行时实际使用的结果文件。由构建脚本稳定重建的中间资源不再进入版本历史，以减少仓库体积、重复二进制和素材更新时的机械变更。

本次同时适用于 `GraceAshcroft` 与 `ChuuniSociety`，并采用通配规则覆盖后续同结构模组。

## 文件边界

继续由 Git 管理：

- `assets/<Mod>/source/` 或资产根目录中的原始图片；
- `assets/<Mod>/mod-build.toml`；
- `tools/<mod>/` 下的构建、烹制和检查脚本；
- `projects/<Mod>/` 下不可由当前脚本重建的项目定义；
- `mods/<Mod>/` 下游戏实际加载的 `.blp`、`.dep`、`.artdef`、SQL、Lua、文本和 ModInfo。

不再由 Git 管理：

- `assets/*/cooker/`；
- `assets/*/generated/`；
- `assets/*/leader-art/`；
- `assets/*/processed/`。

这些目录中的现有文件只从 Git 索引移除，本地副本不删除。用户素材编辑工程及其他未跟踪源文件不纳入本次提交。

## 构建与验证流程

统一验证入口 `tools/run_civ6_tool_tests.ps1` 在执行测试和静态检查前，分别使用 `python -B` 运行 GraceAshcroft 与 ChuuniSociety 的 `build_assets.py`。因此全新检出只依赖源文件即可重建静态检查所需的 PNG、DDS、TEX 和 XLP。

官方 SDK 烹制仍由各自 `cook_assets.py` 负责。Cooker 产生的中间 BLP 位于被忽略的资产目录，最终供游戏加载的 BLP 复制到 `mods/<Mod>/Platforms/Windows/BLPs/` 并继续提交。

## Git 迁移

`.gitignore` 使用整目录通配规则表达资产生命周期，不再为两个模组维护零散扩展名规则。迁移使用仅影响索引的 Git 操作，将四类目录下已跟踪文件标记为删除，但保留工作区文件。

迁移完成后的成功标准：

1. `git ls-files` 不再返回四类过程目录中的文件；
2. 源图片、manifest、项目定义和运行时 BLP 仍受 Git 管理；
3. 在过程目录缺失的临时副本上运行统一验证入口能够重建资源并通过；
4. 重建完成后过程目录不会出现在 `git status`；
5. 用户已有的未跟踪素材文件保持原样。

## 测试策略

- 扩展统一入口契约测试，要求两个资产构建器在静态检查前运行且使用 `python -B`；
- 执行完整统一验证，覆盖两套构建器、资产清单、运行时布局和玩法 SQL；
- 使用 `git check-ignore` 与 `git ls-files` 验证忽略和索引迁移；
- 执行 `git diff --check`，并核对最终工作区仅保留用户原有的未跟踪素材。
