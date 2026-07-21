# Civ6 开发历史压缩设计

## 目标

将远端基点 `7b70d08e2ca303b6f6e5b6a6258d05bfd0030b64` 之后的本地开发历史压缩为一个提交，在保持最终工作树完全一致的前提下，使已删除的 Cooker、generated、leader-art、processed 等中间资源不进入首次远端推送历史。

## 边界

`origin/main` 当前正好指向指定基点，本地 `main` 领先 26 个提交。压缩只改写本地 `main` 的基点后历史，不修改基点及更早提交，也不在本轮推送远端。

最终树继续保留当前受 Git 管理的源文件、文明六运行时文件、BLP 结果文件、文档和 `.af` 编辑源文件。已经从最终树删除且被 `.gitignore` 覆盖的可再生过程文件不会进入新提交。

## 安全步骤

1. 要求工作树除已知忽略项外保持干净，并确认 `origin/main` 仍等于指定基点。
2. 在当前 HEAD 建立仅本地备份分支 `backup/pre-squash-20260721`。
3. 记录备份分支的 tree ID。
4. 将 `main` soft reset 到指定基点，把最终差异作为一个暂存集合。
5. 创建单一提交 `feat: add shared Civ6 tooling and Chuuni Society mod`。
6. 验证新 `main` 的 tree ID 与备份分支完全一致，并确认基点之后只有一个提交。
7. 运行统一 Civ6 工具测试、静态检查和工作区清理。

## 远端与恢复

本轮不 push。因为新提交直接以 `origin/main` 为父提交，后续推送可以使用普通 `git push origin main`，无需 `--force`。

若树比较或测试失败，立即将 `main` 恢复到本地备份分支。备份分支不会自动删除；在用户确认远端结果后再决定是否清理旧本地历史和运行 Git 垃圾回收。

## 成功标准

- `git rev-list --count 7b70d08e..main` 返回 `1`。
- 压缩前后 tree ID 完全一致。
- 统一测试和静态检查全部通过。
- `origin/main` 保持在 `7b70d08e…`。
- 没有执行 force push，也没有上传本地备份分支。
