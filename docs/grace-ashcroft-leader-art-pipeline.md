# Grace Ashcroft Leader Art Pipeline

本文记录 `mods/GraceAshcroft` 的领袖图片资源链。重点是《文明 VI》的开始加载界面和外交界面不是同一条渲染路径，不能简单共用同一张贴图。

源图和中间图放在 `assets/GraceAshcroft`，不要留在 `mods/GraceAshcroft`。Mod 目录只保留运行和注册需要的 `.sql/.tex/.xlp/.artdef/.dep/.blp` 等文件。

另一个独立问题是 DDS 像素通道顺序。`Images/Textures/*.tex` 当前统一声明：

```xml
<ePixelformat>PF_R8G8B8A8_UNORM</ePixelformat>
```

因此 DDS 必须是 legacy RGBA masks：

```text
R = 0x000000FF
G = 0x0000FF00
B = 0x00FF0000
A = 0xFF000000
```

或 DX10 `DXGI_FORMAT_R8G8B8A8_UNORM`。Pillow 的 `Image.save(..., ".dds")` 会为这些图写出 BGRA masks：

```text
R = 0x00FF0000
G = 0x0000FF00
B = 0x000000FF
A = 0xFF000000
```

这会让游戏里背景出现典型的红蓝通道交换。不要通过预先交换 PNG 红蓝通道来规避，应保持 PNG 颜色正常，并生成与 TEX 声明一致的 RGBA DDS。

## 资源分工

当前领袖大图使用五类图片资源，源文件位于 `assets/GraceAshcroft/leader-art`：

- `leader-art/png/GraceAshcroft_Background.png` 与 `leader-art/dds/GraceAshcroft_Background.dds`
  - 干净背景图，尺寸 `2048x1024`。
  - 用于外交背景和玩家选择界面的 `PortraitBackground`。

- `leader-art/png/GraceAshcroft_Foreground.png` 与 `leader-art/dds/GraceAshcroft_Foreground.dds`
  - 透明人物前景，尺寸 `1024x2048`。
  - 用于玩家选择界面的 `Portrait`，以及外交 fallback 人物。

- `leader-art/png/GraceAshcroft_LoadingScene.png` 与 `leader-art/dds/GraceAshcroft_LoadingScene.dds`
  - 开始加载界面专用合成图，尺寸 `2048x1024`。
  - 内容是背景加人物合成后的整张图。

- `leader-art/png/GraceAshcroft_LoadingBlank.png` 与 `leader-art/dds/GraceAshcroft_LoadingBlank.dds`
  - 开始加载界面专用透明占位图，尺寸 `8x8`。
  - 用来占用 `LoadingInfo.ForegroundImage`，避免原版开始界面对前景层染色。

- `Images/Textures/*.tex`
  - Asset Cooker 使用的纹理实例描述文件。

图标源文件位于 `assets/GraceAshcroft/source/icons`，生成文件位于 `assets/GraceAshcroft/generated/icons`。`tools/build_grace_icon_assets.py` 会生成图标 PNG/DDS、写入对应 `.tex`，并把图标 texture entries 加入 `XLPs/GraceUITexture.xlp`。

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

注意：这个蓝色容器只能解释“独立 ForegroundImage 人物变蓝”。如果背景图或 `GraceAshcroft_LoadingScene` 整体偏蓝，原因不是 `PortraitContainer`，而是 DDS 的 RGBA/BGRA 通道顺序与 TEX 声明不一致。

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

## DDS 生成

优先使用 Microsoft DirectXTex `texconv.exe`：

```powershell
texconv.exe -y -m 1 -f R8G8B8A8_UNORM -o Images Images\GraceAshcroft_Background.png
texconv.exe -y -m 1 -f R8G8B8A8_UNORM -o Images Images\GraceAshcroft_Foreground.png
texconv.exe -y -m 1 -f R8G8B8A8_UNORM -o Images Images\GraceAshcroft_LoadingScene.png
texconv.exe -y -m 1 -f R8G8B8A8_UNORM -o Images Images\GraceAshcroft_LoadingBlank.png
```

如果本机没有 `texconv.exe`，使用项目脚本写出 legacy RGBA DDS：

```powershell
python tools\write_rgba_dds.py --out-dir assets\GraceAshcroft\leader-art\dds assets\GraceAshcroft\leader-art\png\GraceAshcroft_Background.png assets\GraceAshcroft\leader-art\png\GraceAshcroft_Foreground.png assets\GraceAshcroft\leader-art\png\GraceAshcroft_LoadingScene.png assets\GraceAshcroft\leader-art\png\GraceAshcroft_LoadingBlank.png
```

该脚本只读取正常 PNG 的 RGBA 像素，直接写出匹配 `PF_R8G8B8A8_UNORM` 的 DDS header 和像素数据。

## 图标生成

五张图标源图：

```text
assets/GraceAshcroft/source/icons/GraceAshcroft_Hemolytic.png
assets/GraceAshcroft/source/icons/GraceAshcroft_Stabilizer.png
assets/GraceAshcroft/source/icons/GraceAshcroft_Steroid.png
assets/GraceAshcroft/source/icons/GraceAshcroft_InfectedBlood.png
assets/GraceAshcroft/source/icons/GraceAshcroft_LeaderIcon.png
```

生成命令：

```powershell
python tools\build_grace_icon_assets.py
```

该命令会生成 `22/30/32/38/50/64/80/256` 八个尺寸，并更新：

```text
assets/GraceAshcroft/generated/icons/png
assets/GraceAshcroft/generated/icons/dds
mods/GraceAshcroft/Images/Textures/GraceAshcroft_Icon_*.tex
mods/GraceAshcroft/XLPs/GraceUITexture.xlp
```

Cook 前需要把 `assets/GraceAshcroft/leader-art/dds` 和生成的图标 DDS 作为 cooker 输入放到 `mods/GraceAshcroft/Images`。Cook 完后，`mods/GraceAshcroft/Images` 根目录应清空，只保留 `Images/Textures` 子目录。

## 换图时的建议

如果只换人物立绘：

1. 替换 `assets/GraceAshcroft/leader-art/png/GraceAshcroft_Foreground.png`。
2. 使用 `texconv.exe` 或 `tools/write_rgba_dds.py` 重新生成 `GraceAshcroft_Foreground.dds`。
3. 重新生成 `GraceAshcroft_LoadingScene.png/dds`。
4. 重新 cook `GraceUITexture.blp` 和 `LeaderFallbacks.blp`。

如果只换背景：

1. 替换 `assets/GraceAshcroft/leader-art/png/GraceAshcroft_Background.png`。
2. 使用 `texconv.exe` 或 `tools/write_rgba_dds.py` 重新生成 `GraceAshcroft_Background.dds`。
3. 重新生成 `GraceAshcroft_LoadingScene.png/dds`。
4. 重新 cook `GraceUITexture.blp`。
