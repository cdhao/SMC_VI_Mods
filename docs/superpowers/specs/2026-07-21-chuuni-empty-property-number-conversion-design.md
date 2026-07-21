# Chuuni 未初始化属性数值转换修复设计

## 问题

`ChuuniGameplay.lua` 将 `Player:GetProperty()` 直接作为 `tonumber()` 的参数。Civ6 在属性尚未写入时可能让该绑定返回零个值，导致 Lua 实际执行零参数 `tonumber()`，并抛出 `bad argument #1 to 'tonumber' (value expected)`。

当前脚本有两个同型位置：阶段属性读取，以及每回合资源结算标记读取。只修复报错行会让执行随后在另一个位置再次失败。

## 设计

在两个调用点先将 `GetProperty()` 的结果赋给局部变量，再调用 `tonumber(localValue)`。零返回值在局部变量赋值时会变成 `nil`，而 `tonumber(nil)` 会安全返回 `nil`，现有的比较与 `or 0` 回退逻辑继续生效。

不新增辅助函数，不改变事件注册、阶段阈值、资源产量或存档属性名称。

## 测试与部署

先添加静态回归测试，拒绝 `tonumber(player:GetProperty(...))` 这种直接嵌套形式，并要求两个属性读取采用局部变量转换。确认测试在现有实现上失败后，实施最小修复并验证测试转绿。

随后运行统一 Civ6 工具测试和 Chuuni 静态检查；验证通过后，通过现有极东部署脚本更新 Civilization VI Mods 目录中的 `ChuuniSociety`。
