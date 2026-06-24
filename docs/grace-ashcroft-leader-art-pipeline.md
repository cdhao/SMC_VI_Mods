# Grace Ashcroft Leader Art Pipeline

本文记录 `mods/GraceAshcroft` 的领袖图片资源链。重点是《文明 VI》的开始加载界面和外交界面不是同一条渲染路径，不能简单共用同一张贴图。

## 资源分工

当前使用五类图片资源：

- `Images/GraceAshcroft_Background.png/dds`
  - 干净背景图，尺寸 `2048x1024`。
  - 用于外交背景和玩家选择界面的 `PortraitBackground`。

- `Images/GraceAshcroft_Foreground.png/dds`
  - 透明人物前景，尺寸 `1024x2048`。
  - 用于玩家选择界面的 `Portrait`，以及外交 fallback 人物。

- `Images/GraceAshcroft_LoadingScene.png/dds`
  - 开始加载界面专用合成图，尺寸 `2048x1024`。
  - 内容是背景加人物合成后的整张图。

- `Images/GraceAshcroft_LoadingBlank.png/dds`
  - 开始加载界面专用透明占位图，尺寸 `8x8`。
  - 用来占用 `LoadingInfo.ForegroundImage`，避免原版开始界面对前景层染色。

- `Images/Textures/*.tex`
  - Asset Cooker 使用的纹理实例描述文件。

## 开始加载界面

开始加载界面读取 `Gameplay.sql` 中的 `LoadingInfo`：

```sql
ForegroundImage = IMG_LOADING_FOREGROUND_BLANK_GRACE_ASHCROFT
BackgroundImage = IMG_LOADING_SCENE_GRACE_ASHCROFT
```

这样做的原因是原版 `Base/Assets/UI/FrontEnd/LoadScreen.xml` 中，人物前景位于 `PortraitContainer` 内，而该容器写死了蓝色：

```xml
<Container ID="PortraitContainer" ... Color="0,0,255,200">
```

如果把正常人物放在 `LoadingInfo.ForegroundImage`，人物会被染蓝。现在改为：

1. `BackgroundImage` 显示已经合成好的人物加背景。
2. `ForegroundImage` 使用全透明占位图。

因此开始加载界面不再依赖原版人物前景层。

## 外交界面

外交界面读取两部分：

- `Gameplay.sql` 的 `DiplomacyInfo.BackgroundImage`
- `ArtDefs/FallbackLeaders.artdef` + `XLPs/leaderfallbacks.xlp`

当前映射为：

```text
DiplomacyInfo.BackgroundImage = IMG_LOADING_BACKGROUND_GRACE_ASHCROFT
FALLBACK_NEUTRAL_GRACE_ASHCROFT = GraceAshcroft_Foreground_Fallback
```

外交 fallback 不走开始加载界面的 `PortraitContainer`，所以可以使用正常透明人物，不需要合成图。

## 玩家选择界面

前端玩家选择界面读取 `Config.sql` 的 `Players`：

```sql
Portrait = IMG_LOADING_FOREGROUND_GRACE_ASHCROFT
PortraitBackground = IMG_LOADING_BACKGROUND_GRACE_ASHCROFT
```

这里也不走开始加载界面的蓝色 `PortraitContainer`，所以继续使用正常透明人物和干净背景。

## BLP 注册

`XLPs/GraceUITexture.xlp` 注册 UI 贴图：

```text
IMG_LOADING_BACKGROUND_GRACE_ASHCROFT -> GraceAshcroft_Background_UI
IMG_LOADING_FOREGROUND_GRACE_ASHCROFT -> GraceAshcroft_Foreground_UI
IMG_LOADING_SCENE_GRACE_ASHCROFT -> GraceAshcroft_LoadingScene_UI
IMG_LOADING_FOREGROUND_BLANK_GRACE_ASHCROFT -> GraceAshcroft_LoadingBlank_UI
```

`XLPs/leaderfallbacks.xlp` 注册外交 fallback：

```text
FALLBACK_NEUTRAL_GRACE_ASHCROFT -> GraceAshcroft_Foreground_Fallback
```

修改 `.xlp` 或 `.tex` 后，需要重新 cook 对应 BLP：

```powershell
& "C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization VI SDK\AssetModTools\Cooker\Civ6AssetCooker_FinalRelease.exe" --mode XLP --platform Windows --config "C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization VI SDK\AssetModTools\Cooker\Civ6.cfg" --pantry Images --stewpot Platforms\Windows\BLPs --log_path Logs XLPs\GraceUITexture.xlp
& "C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization VI SDK\AssetModTools\Cooker\Civ6AssetCooker_FinalRelease.exe" --mode XLP --platform Windows --config "C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization VI SDK\AssetModTools\Cooker\Civ6.cfg" --pantry Images --stewpot Platforms\Windows\BLPs --log_path Logs XLPs\leaderfallbacks.xlp
```

## 换图时的建议

如果只换人物立绘：

1. 替换 `GraceAshcroft_Foreground.png`。
2. 重新生成 `GraceAshcroft_Foreground.dds`。
3. 重新生成 `GraceAshcroft_LoadingScene.png/dds`。
4. 重新 cook `GraceUITexture.blp` 和 `LeaderFallbacks.blp`。

如果只换背景：

1. 替换 `GraceAshcroft_Background.png`。
2. 重新生成 `GraceAshcroft_Background.dds`。
3. 重新生成 `GraceAshcroft_LoadingScene.png/dds`。
4. 重新 cook `GraceUITexture.blp`。
