$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$modRoot = Join-Path $root "mods\GraceAshcroft"
$assetRoot = Join-Path $root "assets\GraceAshcroft"

function Assert-FileExists {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Missing required file: $Path"
    }
}

function Assert-FileMissing {
    param([string]$Path)

    if (Test-Path -LiteralPath $Path -PathType Leaf) {
        throw "Obsolete file should be removed: $Path"
    }
}

function Assert-DdsHeader {
    param(
        [string]$Path,
        [int]$ExpectedWidth,
        [int]$ExpectedHeight,
        [int]$ExpectedBitsPerPixel
    )

    $bytes = [System.IO.File]::ReadAllBytes($Path)
    if ($bytes.Length -lt 128) {
        throw "DDS file is too small: $Path"
    }

    $magic = [System.Text.Encoding]::ASCII.GetString($bytes, 0, 4)
    if ($magic -ne "DDS ") {
        throw "File is not a DDS texture: $Path"
    }

    $height = [BitConverter]::ToInt32($bytes, 12)
    $width = [BitConverter]::ToInt32($bytes, 16)
    $fourCCValue = [BitConverter]::ToUInt32($bytes, 84)
    $fourCC = [System.Text.Encoding]::ASCII.GetString($bytes, 84, 4)
    $bitsPerPixel = [BitConverter]::ToInt32($bytes, 88)
    $redMask = [BitConverter]::ToUInt32($bytes, 92)
    $greenMask = [BitConverter]::ToUInt32($bytes, 96)
    $blueMask = [BitConverter]::ToUInt32($bytes, 100)
    $alphaMask = [BitConverter]::ToUInt32($bytes, 104)
    $redMaskText = "{0:X8}" -f $redMask
    $greenMaskText = "{0:X8}" -f $greenMask
    $blueMaskText = "{0:X8}" -f $blueMask
    $alphaMaskText = "{0:X8}" -f $alphaMask

    if ($width -ne $ExpectedWidth -or $height -ne $ExpectedHeight -or $bitsPerPixel -ne $ExpectedBitsPerPixel) {
        throw "Unexpected DDS header for $Path. Expected ${ExpectedWidth}x${ExpectedHeight}x${ExpectedBitsPerPixel}, got ${width}x${height}x${bitsPerPixel}."
    }

    $isLegacyRgba =
        $fourCCValue -eq 0 -and
        $redMaskText -eq "000000FF" -and
        $greenMaskText -eq "0000FF00" -and
        $blueMaskText -eq "00FF0000" -and
        $alphaMaskText -eq "FF000000"

    $isDx10Rgba = $false
    if ($fourCCValue -eq 0x30315844) {
        if ($bytes.Length -lt 148) {
            throw "DDS DX10 header is missing extended format data: $Path"
        }

        $dxgiFormat = [BitConverter]::ToUInt32($bytes, 128)
        $isDx10Rgba = $dxgiFormat -eq 28
    }

    if (-not ($isLegacyRgba -or $isDx10Rgba)) {
        throw ("Unexpected DDS pixel format for {0}. Expected legacy RGBA masks R=0x000000FF G=0x0000FF00 B=0x00FF0000 A=0xFF000000 or DX10 DXGI_FORMAT_R8G8B8A8_UNORM. Got FourCC='{1}' R=0x{2} G=0x{3} B=0x{4} A=0x{5}." -f $Path, $fourCC, $redMaskText, $greenMaskText, $blueMaskText, $alphaMaskText)
    }
}

function Assert-Contains {
    param(
        [string]$Path,
        [string]$Needle
    )

    $content = Get-Content -Raw -LiteralPath $Path
    if (-not $content.Contains($Needle)) {
        throw "Expected '$Needle' in $Path"
    }
}

function Assert-BinaryContains {
    param(
        [string]$Path,
        [string]$Needle
    )

    $bytes = [System.IO.File]::ReadAllBytes($Path)
    $content = [System.Text.Encoding]::ASCII.GetString($bytes)
    if (-not $content.Contains($Needle)) {
        throw "Expected binary '$Needle' in $Path"
    }
}

function Assert-BinaryNotContains {
    param(
        [string]$Path,
        [string]$Needle
    )

    $bytes = [System.IO.File]::ReadAllBytes($Path)
    $content = [System.Text.Encoding]::ASCII.GetString($bytes)
    if ($content.Contains($Needle)) {
        throw "Did not expect binary '$Needle' in $Path"
    }
}

function Assert-NotContains {
    param(
        [string]$Path,
        [string]$Needle
    )

    $content = Get-Content -Raw -LiteralPath $Path
    if ($content.Contains($Needle)) {
        throw "Did not expect '$Needle' in $Path"
    }
}

function Assert-DoesNotMatch {
    param(
        [string]$Path,
        [string]$Pattern
    )

    $content = Get-Content -Raw -LiteralPath $Path
    if ($content -match $Pattern) {
        throw "Did not expect pattern '$Pattern' in $Path"
    }
}

function Assert-Matches {
    param(
        [string]$Path,
        [string]$Pattern
    )

    $content = Get-Content -Raw -LiteralPath $Path
    if ($content -notmatch $Pattern) {
        throw "Expected pattern '$Pattern' in $Path"
    }
}

$modinfo = Join-Path $modRoot "GraceAshcroft.modinfo"
$config = Join-Path $modRoot "Data\Config.sql"
$gameplay = Join-Path $modRoot "Data\Gameplay.sql"
$colors = Join-Path $modRoot "Data\GraceColors.xml"
$text = Join-Path $modRoot "Text\GraceAshcroft_zh_Hans_CN.sql"
$lua = Join-Path $modRoot "Scripts\GraceGameplay.lua"
$icons = Join-Path $modRoot "Icons\GraceIcons.sql"
$districtArtDef = Join-Path $modRoot "ArtDefs\Districts.artdef"
$fallbackLeaderArtDef = Join-Path $modRoot "ArtDefs\FallbackLeaders.artdef"
$artDep = Join-Path $modRoot "GraceAshcroft.dep"
$backgroundImage = Join-Path $assetRoot "leader-art\png\GraceAshcroft_Background.png"
$backgroundTexture = Join-Path $assetRoot "leader-art\dds\GraceAshcroft_Background.dds"
$foregroundImage = Join-Path $assetRoot "leader-art\png\GraceAshcroft_Foreground.png"
$foregroundTexture = Join-Path $assetRoot "leader-art\dds\GraceAshcroft_Foreground.dds"
$loadingSceneImage = Join-Path $assetRoot "leader-art\png\GraceAshcroft_LoadingScene.png"
$loadingSceneTexture = Join-Path $assetRoot "leader-art\dds\GraceAshcroft_LoadingScene.dds"
$loadingBlankImage = Join-Path $assetRoot "leader-art\png\GraceAshcroft_LoadingBlank.png"
$loadingBlankTexture = Join-Path $assetRoot "leader-art\dds\GraceAshcroft_LoadingBlank.dds"
$modBackgroundImage = Join-Path $modRoot "Images\GraceAshcroft_Background.png"
$modBackgroundTexture = Join-Path $modRoot "Images\GraceAshcroft_Background.dds"
$modForegroundImage = Join-Path $modRoot "Images\GraceAshcroft_Foreground.png"
$modForegroundTexture = Join-Path $modRoot "Images\GraceAshcroft_Foreground.dds"
$modLoadingSceneImage = Join-Path $modRoot "Images\GraceAshcroft_LoadingScene.png"
$modLoadingSceneTexture = Join-Path $modRoot "Images\GraceAshcroft_LoadingScene.dds"
$modLoadingBlankImage = Join-Path $modRoot "Images\GraceAshcroft_LoadingBlank.png"
$modLoadingBlankTexture = Join-Path $modRoot "Images\GraceAshcroft_LoadingBlank.dds"
$backgroundUiEntity = Join-Path $modRoot "Images\Textures\GraceAshcroft_Background_UI.tex"
$foregroundUiEntity = Join-Path $modRoot "Images\Textures\GraceAshcroft_Foreground_UI.tex"
$foregroundFallbackEntity = Join-Path $modRoot "Images\Textures\GraceAshcroft_Foreground_Fallback.tex"
$loadingSceneUiEntity = Join-Path $modRoot "Images\Textures\GraceAshcroft_LoadingScene_UI.tex"
$loadingBlankUiEntity = Join-Path $modRoot "Images\Textures\GraceAshcroft_LoadingBlank_UI.tex"
$oldBoardBase = "GraceAshcroft_" + "Board"
$oldBoardImage = Join-Path $modRoot "Images\$oldBoardBase.png"
$oldBoardTexture = Join-Path $modRoot "Images\$oldBoardBase.dds"
$oldBoardUiEntity = Join-Path $modRoot ("Images\Textures\" + $oldBoardBase + "_UI.tex")
$oldBoardFallbackEntity = Join-Path $modRoot ("Images\Textures\" + $oldBoardBase + "_Fallback.tex")
$uiTextureXlp = Join-Path $modRoot "XLPs\GraceUITexture.xlp"
$leaderFallbackXlp = Join-Path $modRoot "XLPs\leaderfallbacks.xlp"
$uiTextureBlp = Join-Path $modRoot "Platforms\Windows\BLPs\GraceUITexture.blp"
$leaderFallbackBlp = Join-Path $modRoot "Platforms\Windows\BLPs\LeaderFallbacks.blp"
$iconSizes = @(22, 30, 32, 38, 50, 64, 80, 256)
$iconBases = @(
    "GraceAshcroft_Icon_Hemolytic",
    "GraceAshcroft_Icon_Stabilizer",
    "GraceAshcroft_Icon_Steroid",
    "GraceAshcroft_Icon_InfectedBlood",
    "GraceAshcroft_Icon_Leader"
)
$iconSources = @(
    (Join-Path $assetRoot "source\icons\GraceAshcroft_Hemolytic.png"),
    (Join-Path $assetRoot "source\icons\GraceAshcroft_Stabilizer.png"),
    (Join-Path $assetRoot "source\icons\GraceAshcroft_Steroid.png"),
    (Join-Path $assetRoot "source\icons\GraceAshcroft_InfectedBlood.png"),
    (Join-Path $assetRoot "source\icons\GraceAshcroft_LeaderIcon.png")
)

@($modinfo, $config, $gameplay, $colors, $text, $lua, $icons, $districtArtDef, $fallbackLeaderArtDef, $artDep, $backgroundImage, $backgroundTexture, $foregroundImage, $foregroundTexture, $loadingSceneImage, $loadingSceneTexture, $loadingBlankImage, $loadingBlankTexture, $backgroundUiEntity, $foregroundUiEntity, $foregroundFallbackEntity, $loadingSceneUiEntity, $loadingBlankUiEntity, $uiTextureXlp, $leaderFallbackXlp, $uiTextureBlp, $leaderFallbackBlp) | ForEach-Object {
    Assert-FileExists $_
}

@($oldBoardImage, $oldBoardTexture, $oldBoardUiEntity, $oldBoardFallbackEntity, $modBackgroundImage, $modBackgroundTexture, $modForegroundImage, $modForegroundTexture, $modLoadingSceneImage, $modLoadingSceneTexture, $modLoadingBlankImage, $modLoadingBlankTexture) | ForEach-Object {
    Assert-FileMissing $_
}

$iconSources | ForEach-Object {
    Assert-FileExists $_
}

foreach ($iconBase in $iconBases) {
    foreach ($iconSize in $iconSizes) {
        $iconName = "${iconBase}_${iconSize}"
        $generatedPng = Join-Path $assetRoot "generated\icons\png\${iconName}.png"
        $generatedDds = Join-Path $assetRoot "generated\icons\dds\${iconName}.dds"
        $modDds = Join-Path $modRoot "Images\${iconName}.dds"
        $modTex = Join-Path $modRoot "Images\Textures\${iconName}.tex"

        Assert-FileExists $generatedPng
        Assert-FileExists $generatedDds
        Assert-FileExists $modTex
        Assert-FileMissing $modDds
        Assert-DdsHeader $generatedDds $iconSize $iconSize 32
        Assert-Contains $modTex "<m_Name text=""${iconName}""/>"
        Assert-Contains $modTex "<m_RelativePath text=""../${iconName}.dds""/>"
    }
}

Assert-DdsHeader $backgroundTexture 2048 1024 32
Assert-DdsHeader $foregroundTexture 1024 2048 32
Assert-DdsHeader $loadingSceneTexture 2048 1024 32
Assert-DdsHeader $loadingBlankTexture 8 8 32

Assert-Contains $modinfo "<Mod id="
Assert-Contains $modinfo "AddGameplayScripts"
Assert-Contains $modinfo "Data/Config.sql"
Assert-Contains $modinfo "Data/Gameplay.sql"
Assert-Contains $modinfo "Text/GraceAshcroft_zh_Hans_CN.sql"
Assert-Contains $modinfo "Scripts/GraceGameplay.lua"
Assert-Contains $modinfo "UpdateIcons"
Assert-Contains $modinfo "Icons/GraceIcons.sql"
Assert-Contains $modinfo "UpdateArt"
Assert-Contains $modinfo "GraceAshcroft.dep"
Assert-Contains $modinfo "UpdateColors"
Assert-Contains $modinfo "Data/GraceColors.xml"
Assert-Contains $modinfo "ArtDefs/Districts.artdef"
Assert-Contains $modinfo "ArtDefs/FallbackLeaders.artdef"
Assert-NotContains $modinfo "Images/GraceAshcroft_Background.png"
Assert-NotContains $modinfo "Images/GraceAshcroft_Background.dds"
Assert-NotContains $modinfo "Images/GraceAshcroft_Foreground.png"
Assert-NotContains $modinfo "Images/GraceAshcroft_Foreground.dds"
Assert-NotContains $modinfo "Images/GraceAshcroft_LoadingScene.png"
Assert-NotContains $modinfo "Images/GraceAshcroft_LoadingScene.dds"
Assert-NotContains $modinfo "Images/GraceAshcroft_LoadingBlank.png"
Assert-NotContains $modinfo "Images/GraceAshcroft_LoadingBlank.dds"
Assert-Contains $modinfo "Images/Textures/GraceAshcroft_Background_UI.tex"
Assert-Contains $modinfo "Images/Textures/GraceAshcroft_Foreground_UI.tex"
Assert-Contains $modinfo "Images/Textures/GraceAshcroft_Foreground_Fallback.tex"
Assert-Contains $modinfo "Images/Textures/GraceAshcroft_LoadingScene_UI.tex"
Assert-Contains $modinfo "Images/Textures/GraceAshcroft_LoadingBlank_UI.tex"
Assert-Contains $modinfo "Images/Textures/GraceAshcroft_Icon_Leader_256.tex"
Assert-Contains $modinfo "Images/Textures/GraceAshcroft_Icon_InfectedBlood_256.tex"
Assert-Contains $modinfo "Images/Textures/GraceAshcroft_Icon_Hemolytic_256.tex"
Assert-Contains $modinfo "Images/Textures/GraceAshcroft_Icon_Stabilizer_256.tex"
Assert-Contains $modinfo "Images/Textures/GraceAshcroft_Icon_Steroid_256.tex"
Assert-Contains $modinfo "XLPs/GraceUITexture.xlp"
Assert-Contains $modinfo "XLPs/leaderfallbacks.xlp"
Assert-Contains $modinfo "Platforms/Windows/BLPs/GraceUITexture.blp"
Assert-Contains $modinfo "Platforms/Windows/BLPs/LeaderFallbacks.blp"
Assert-NotContains $modinfo $oldBoardBase
Assert-NotContains $modinfo "AddUserInterfaces"
Assert-NotContains $modinfo "UI/GraceBloodPanel"

Assert-Contains $config "CIVILIZATION_ELPIS_PROTOCOL"
Assert-Contains $config "LEADER_GRACE_ASHCROFT"
Assert-Contains $config "Players:Expansion2_Players"
Assert-Contains $config "DISTRICT_GRACE_ARK"
Assert-Contains $config "'IMG_LOADING_FOREGROUND_GRACE_ASHCROFT'"
Assert-Contains $config "'IMG_LOADING_BACKGROUND_GRACE_ASHCROFT'"
Assert-Contains $config "'ICON_LEADER_GRACE_ASHCROFT'"
Assert-NotContains $config "'ICON_LEADER_DEFAULT'"
Assert-NotContains $config "'LEADER_DEFAULT_NEUTRAL'"
Assert-NotContains $config $oldBoardBase
Assert-NotContains $config "BUILDING_RHODES_HILL_SANATORIUM"

Assert-Contains $gameplay "DISTRICT_GRACE_ARK"
Assert-Contains $gameplay "TRAIT_DISTRICT_GRACE_ARK"
Assert-Contains $gameplay "'LEADER_GRACE_ASHCROFT', 'IMG_LOADING_FOREGROUND_BLANK_GRACE_ASHCROFT', 'IMG_LOADING_SCENE_GRACE_ASHCROFT'"
Assert-NotContains $gameplay "'LEADER_GRACE_ASHCROFT', 'IMG_LOADING_FOREGROUND_GRACE_ASHCROFT', 'IMG_LOADING_BACKGROUND_GRACE_ASHCROFT'"
Assert-Contains $gameplay "'LEADER_GRACE_ASHCROFT', 'IMG_LOADING_BACKGROUND_GRACE_ASHCROFT'"
Assert-NotContains $gameplay "'LEADER_DEFAULT_NEUTRAL'"
Assert-NotContains $gameplay $oldBoardBase
Assert-Contains $gameplay "RESOURCE_INFECTED_BLOOD"
Assert-Contains $gameplay "'RESOURCE_INFECTED_BLOOD', 'KIND_RESOURCE'"
Assert-Contains $gameplay "Resource_Consumption"
Assert-Contains $gameplay "DistrictReplaces"
Assert-Contains $gameplay "'DISTRICT_GRACE_ARK', 'DISTRICT_CAMPUS'"
Assert-Contains $gameplay "ZOC = (SELECT ZOC FROM Districts WHERE DistrictType = 'DISTRICT_ENCAMPMENT')"
Assert-Contains $gameplay "HitPoints = (SELECT HitPoints FROM Districts WHERE DistrictType = 'DISTRICT_ENCAMPMENT')"
Assert-Contains $gameplay "CanAttack = (SELECT CanAttack FROM Districts WHERE DistrictType = 'DISTRICT_ENCAMPMENT')"
Assert-Contains $gameplay "Districts_XP2"
Assert-Contains $gameplay "AttackRange"
Assert-Contains $gameplay "StartBiasRivers"
Assert-Contains $gameplay "'CIVILIZATION_ELPIS_PROTOCOL', 2"
Assert-Contains $gameplay "StartBiasTerrains"
Assert-Contains $gameplay "'CIVILIZATION_ELPIS_PROTOCOL', 'TERRAIN_GRASS_HILLS', 3"
Assert-Contains $gameplay "'CIVILIZATION_ELPIS_PROTOCOL', 'TERRAIN_PLAINS_HILLS', 3"
Assert-Contains $gameplay "'CIVILIZATION_ELPIS_PROTOCOL', 'TERRAIN_TUNDRA_HILLS', 4"
Assert-Contains $gameplay "'CIVILIZATION_ELPIS_PROTOCOL', 'TERRAIN_DESERT_HILLS', 5"
Assert-NotContains $gameplay "StartBiasResources"
Assert-NotContains $gameplay "RESOURCE_HORSES"
Assert-Contains $gameplay "PROJECT_GRACE_HEMOLYTIC_1"
Assert-Contains $gameplay "PROJECT_GRACE_HEMOLYTIC_2"
Assert-Contains $gameplay "PROJECT_GRACE_HEMOLYTIC_3"
Assert-Contains $gameplay "PROJECT_GRACE_STABILIZER_1"
Assert-Contains $gameplay "PROJECT_GRACE_STABILIZER_2"
Assert-Contains $gameplay "PROJECT_GRACE_STABILIZER_3"
Assert-Contains $gameplay "PROJECT_GRACE_STEROID_1"
Assert-Contains $gameplay "PROJECT_GRACE_STEROID_2"
Assert-Contains $gameplay "PROJECT_GRACE_STEROID_3"
Assert-NotContains $gameplay "PROJECT_GRACE_HEMOLYTIC_AGENT"
Assert-DoesNotMatch $gameplay "PROJECT_GRACE_STABILIZER['""]"
Assert-DoesNotMatch $gameplay "PROJECT_GRACE_STEROID['""]"
Assert-Contains $gameplay "PROJECT_GRACE_BLOOD_SAMPLE_ANALYSIS"
Assert-Contains $gameplay "PROJECT_GRACE_ABNORMAL_PATHOLOGY"
Assert-Contains $gameplay "PROJECT_GRACE_STRATEGIC_MATERIAL_SYNTHESIS"
Assert-NotContains $gameplay "PROJECT_GRACE_CONTAINMENT_REVIEW"
Assert-NotContains $gameplay "WHERE ProjectType = 'PROJECT_ENHANCE_DISTRICT_CAMPUS'"
Assert-Contains $gameplay "'PROJECT_GRACE_BLOOD_SAMPLE_ANALYSIS',"
Assert-Contains $gameplay "'PROJECT_GRACE_ABNORMAL_PATHOLOGY',"
Assert-Contains $gameplay "'PROJECT_GRACE_STRATEGIC_MATERIAL_SYNTHESIS',"
Assert-Contains $gameplay "1, 'NO_COST_PROGRESSION', 0, 'TECH_WRITING', 'DISTRICT_GRACE_ARK'"
Assert-Contains $gameplay "MaxPlayerInstances"
Assert-Contains $gameplay "ProjectPrereqs"
Assert-Contains $gameplay "'PROJECT_GRACE_HEMOLYTIC_2', 'PROJECT_GRACE_HEMOLYTIC_1', 1"
Assert-Contains $gameplay "'PROJECT_GRACE_HEMOLYTIC_3', 'PROJECT_GRACE_HEMOLYTIC_2', 1"
Assert-Contains $gameplay "'PROJECT_GRACE_STABILIZER_2', 'PROJECT_GRACE_STABILIZER_1', 1"
Assert-Contains $gameplay "'PROJECT_GRACE_STABILIZER_3', 'PROJECT_GRACE_STABILIZER_2', 1"
Assert-Contains $gameplay "'PROJECT_GRACE_STEROID_2', 'PROJECT_GRACE_STEROID_1', 1"
Assert-Contains $gameplay "'PROJECT_GRACE_STEROID_3', 'PROJECT_GRACE_STEROID_2', 1"
Assert-Contains $gameplay "Project_ResourceCosts"
Assert-Contains $gameplay "StartProductionCost"
Assert-DoesNotMatch $gameplay "'PROJECT_GRACE_[A-Z0-9_]+', 'RESOURCE_INFECTED_BLOOD', 3"
Assert-Contains $gameplay "'PROJECT_GRACE_HEMOLYTIC_1', 'RESOURCE_INFECTED_BLOOD', 1"
Assert-Contains $gameplay "'PROJECT_GRACE_HEMOLYTIC_2', 'RESOURCE_INFECTED_BLOOD', 1"
Assert-Contains $gameplay "'PROJECT_GRACE_HEMOLYTIC_3', 'RESOURCE_INFECTED_BLOOD', 1"
Assert-Contains $gameplay "'PROJECT_GRACE_STABILIZER_1', 'RESOURCE_INFECTED_BLOOD', 1"
Assert-Contains $gameplay "'PROJECT_GRACE_STABILIZER_2', 'RESOURCE_INFECTED_BLOOD', 1"
Assert-Contains $gameplay "'PROJECT_GRACE_STABILIZER_3', 'RESOURCE_INFECTED_BLOOD', 1"
Assert-Contains $gameplay "'PROJECT_GRACE_STEROID_1', 'RESOURCE_INFECTED_BLOOD', 1"
Assert-Contains $gameplay "'PROJECT_GRACE_STEROID_2', 'RESOURCE_INFECTED_BLOOD', 1"
Assert-Contains $gameplay "'PROJECT_GRACE_STEROID_3', 'RESOURCE_INFECTED_BLOOD', 1"
Assert-Contains $gameplay "'PROJECT_GRACE_BLOOD_SAMPLE_ANALYSIS', 'RESOURCE_INFECTED_BLOOD', 1"
Assert-Contains $gameplay "'PROJECT_GRACE_ABNORMAL_PATHOLOGY', 'RESOURCE_INFECTED_BLOOD', 1"
Assert-Contains $gameplay "'PROJECT_GRACE_STRATEGIC_MATERIAL_SYNTHESIS', 'RESOURCE_INFECTED_BLOOD', 1"
Assert-NotContains $gameplay "GRACE_PROJECT_BLOOD_COST"
Assert-NotContains $gameplay "GRACE_NATIVE_PROJECT_BLOOD_COST"
Assert-Contains $gameplay "'TECH_WRITING', 'DISTRICT_GRACE_ARK'"
Assert-Contains $gameplay "GRACE_ARK_CITY_CENTER_SCIENCE"
Assert-Contains $gameplay "'GRACE_ARK_CITY_CENTER_SCIENCE', 'LOC_GRACE_ARK_CITY_CENTER_SCIENCE_DESCRIPTION', 'YIELD_SCIENCE', 2, 1, 'DISTRICT_CITY_CENTER'"
Assert-Contains $gameplay "GRACE_ARK_DISTRICT_SCIENCE_"
Assert-Contains $gameplay "DistrictType NOT IN ('DISTRICT_CITY_CENTER', 'DISTRICT_GRACE_ARK')"
Assert-Contains $gameplay "COALESCE(InternalOnly, 0) = 0"
Assert-Contains $gameplay "COALESCE(CityCenter, 0) = 0"
Assert-NotContains $gameplay "GRACE_ARK_CITY_CENTER_PRODUCTION"
Assert-NotContains $gameplay "GRACE_ARK_DISTRICT_PRODUCTION"
Assert-Contains $gameplay "GRACE_ARK_IMPROVEMENT_SCIENCE_"
Assert-Contains $gameplay "COALESCE(Buildable, 0) = 1"
Assert-NotContains $gameplay "GRACE_ARK_IMPROVEMENT_PRODUCTION_"
Assert-NotContains $gameplay "GRACE_ARK_PROD_"
Assert-Contains $gameplay "GRACE_ARK_SCIENCE_ADJACENCY_PRODUCTION"
Assert-Contains $gameplay "'GRACE_ARK_SCIENCE_ADJACENCY_PRODUCTION', 'MODIFIER_ALL_DISTRICTS_ADJUST_YIELD_BASED_ON_ADJACENCY_BONUS', NULL, 'GRACE_ARK_DISTRICT_PLOT_REQUIREMENTS'"
Assert-Contains $gameplay "'GRACE_ARK_SCIENCE_ADJACENCY_PRODUCTION', 'YieldTypeToMirror', 'YIELD_SCIENCE'"
Assert-Contains $gameplay "'GRACE_ARK_SCIENCE_ADJACENCY_PRODUCTION', 'YieldTypeToGrant', 'YIELD_PRODUCTION'"
Assert-Contains $gameplay "GRACE_ARK_TO_SCIENCE"
Assert-Contains $gameplay "GRACE_ARK_TO_FAITH"
Assert-Contains $gameplay "GRACE_ARK_TO_CULTURE"
Assert-Contains $gameplay "GRACE_ARK_TO_GOLD"
Assert-Contains $gameplay "GRACE_ARK_TO_PRODUCTION"
Assert-Contains $gameplay "GRACE_PLAYER_HAS_CURRENCY"
Assert-Contains $gameplay "'GRACE_PLAYER_HAS_CURRENCY', 'REQUIREMENT_PLAYER_HAS_TECHNOLOGY'"
Assert-Contains $gameplay "'GRACE_PLAYER_HAS_CURRENCY', 'TechnologyType', 'TECH_CURRENCY'"
Assert-Contains $gameplay "GRACE_PLOT_HAS_ARK"
Assert-Contains $gameplay "'GRACE_PLOT_HAS_ARK', 'REQUIREMENT_PLOT_DISTRICT_TYPE_MATCHES'"
Assert-Contains $gameplay "'GRACE_PLOT_HAS_ARK', 'DistrictType', 'DISTRICT_GRACE_ARK'"
Assert-Contains $gameplay "GRACE_UNIT_IS_RANGED"
Assert-Contains $gameplay "'GRACE_UNIT_IS_RANGED', 'REQUIREMENT_UNIT_PROMOTION_CLASS_MATCHES'"
Assert-Contains $gameplay "'GRACE_UNIT_IS_RANGED', 'UnitPromotionClass', 'PROMOTION_CLASS_RANGED'"
Assert-Contains $gameplay "GRACE_UNIT_IS_LAND"
Assert-Contains $gameplay "'GRACE_UNIT_IS_LAND', 'REQUIREMENT_UNIT_DOMAIN_MATCHES'"
Assert-Contains $gameplay "'GRACE_UNIT_IS_LAND', 'UnitDomain', 'DOMAIN_LAND'"
Assert-Contains $gameplay "GRACE_ARK_RANGED_GARRISON_UNIT_REQUIREMENTS"
Assert-Contains $gameplay "'GRACE_ARK_GARRISON_RANGE', 'MODIFIER_PLAYER_UNITS_ADJUST_ATTACK_RANGE', 'GRACE_PLAYER_HAS_CURRENCY_REQUIREMENTS', 'GRACE_ARK_RANGED_GARRISON_UNIT_REQUIREMENTS'"
Assert-Contains $gameplay "'GRACE_ARK_GARRISON_SIGHT', 'MODIFIER_PLAYER_UNIT_ADJUST_SIGHT', 'GRACE_PLAYER_HAS_CURRENCY_REQUIREMENTS', 'GRACE_ARK_RANGED_GARRISON_UNIT_REQUIREMENTS'"
Assert-Contains $gameplay "'GRACE_ARK_GARRISON_RANGE', 'Amount', 1"
Assert-Contains $gameplay "'GRACE_ARK_GARRISON_SIGHT', 'Amount', 1"
Assert-DoesNotMatch $lua "for\s+_,\s*unit\s+in\s+player:GetUnits\(\):Members\(\)\s+do[\s\S]*GRACE_ARK_GARRISON"
Assert-Contains $gameplay "GRACE_BLOOD_PER_BARBARIAN_KILL"
Assert-Contains $gameplay "GRACE_BLOOD_PER_BARBARIAN_CAMP"
Assert-Contains $gameplay "GRACE_KILL_GOLD_PERCENT"
Assert-Contains $gameplay "GRACE_BSAA_POST_COMBAT_GOLD"
Assert-Contains $gameplay "'TRAIT_CIVILIZATION_ELPIS_PROTOCOL', 'GRACE_BSAA_POST_COMBAT_GOLD'"
Assert-Contains $gameplay "'TRAIT_CIVILIZATION_ELPIS_PROTOCOL', 'GRACE_HEMOLYTIC_1_COMBAT'"
Assert-Contains $gameplay "'TRAIT_CIVILIZATION_ELPIS_PROTOCOL', 'GRACE_HEMOLYTIC_2_COMBAT'"
Assert-Contains $gameplay "'TRAIT_CIVILIZATION_ELPIS_PROTOCOL', 'GRACE_HEMOLYTIC_3_COMBAT'"
Assert-Contains $gameplay "'TRAIT_CIVILIZATION_ELPIS_PROTOCOL', 'GRACE_STABILIZER_1_COMBAT'"
Assert-Contains $gameplay "'TRAIT_CIVILIZATION_ELPIS_PROTOCOL', 'GRACE_STABILIZER_2_COMBAT'"
Assert-Contains $gameplay "'TRAIT_CIVILIZATION_ELPIS_PROTOCOL', 'GRACE_STABILIZER_3_COMBAT'"
Assert-Contains $gameplay "'GRACE_BSAA_POST_COMBAT_GOLD', 'MODIFIER_PLAYER_UNITS_ADJUST_POST_COMBAT_YIELD'"
Assert-Contains $gameplay "'GRACE_BSAA_POST_COMBAT_GOLD', 'YieldType', 'YIELD_GOLD'"
Assert-Contains $gameplay "'GRACE_BSAA_POST_COMBAT_GOLD', 'PercentDefeatedStrength'"
Assert-Contains $gameplay "'TRAIT_CIVILIZATION_ELPIS_PROTOCOL', 'GRACE_INFECTED_BLOOD_UPGRADE_DISCOUNT'"
Assert-Contains $gameplay "GRACE_PLAYER_HAS_INFECTED_BLOOD"
Assert-Contains $gameplay "'GRACE_PLAYER_HAS_INFECTED_BLOOD', 'REQUIREMENT_PLAYER_HAS_RESOURCE_OWNED'"
Assert-Contains $gameplay "'GRACE_PLAYER_HAS_INFECTED_BLOOD', 'ResourceType', 'RESOURCE_INFECTED_BLOOD'"
Assert-Contains $gameplay "GRACE_PLAYER_HAS_INFECTED_BLOOD_REQUIREMENTS"
Assert-Contains $gameplay "'GRACE_PLAYER_HAS_INFECTED_BLOOD_REQUIREMENTS', 'GRACE_PLAYER_HAS_INFECTED_BLOOD'"
Assert-Contains $gameplay "'GRACE_INFECTED_BLOOD_UPGRADE_DISCOUNT', 'MODIFIER_PLAYER_ADJUST_UNIT_UPGRADE_DISCOUNT_PERCENT', 'GRACE_PLAYER_HAS_INFECTED_BLOOD_REQUIREMENTS', NULL"
Assert-Contains $gameplay "'GRACE_BLOOD_UPGRADE_DISCOUNT_PERCENT', '50'"
Assert-Contains $gameplay "SELECT 'GRACE_INFECTED_BLOOD_UPGRADE_DISCOUNT', 'Amount', Value"
Assert-Contains $gameplay "GRACE_STRATEGIC_MAX_BLOOD_PER_PROJECT"
Assert-Contains $gameplay "GRACE_STRATEGIC_RESOURCE_PER_BLOOD"
Assert-Contains $gameplay "GRACE_PATHOLOGY_MAX_BLOOD_PER_PROJECT"
Assert-Contains $gameplay "GRACE_PATHOLOGY_CITY_YIELD_PERCENT"
Assert-Contains $gameplay "GRACE_PATHOLOGY_MIN_REWARD_PER_BLOOD"
Assert-NotContains $gameplay "GRACE_EUREKA_FALLBACK_SCIENCE"
Assert-NotContains $gameplay "GRACE_GREAT_SCIENTIST_POINTS"
Assert-NotContains $gameplay "GRACE_CONTAINMENT_REVIEW_SCIENCE"
Assert-Contains $gameplay "GRACE_HEMOLYTIC_1_OWNER_REQUIREMENTS"
Assert-Contains $gameplay "GRACE_HEMOLYTIC_2_OWNER_REQUIREMENTS"
Assert-Contains $gameplay "GRACE_HEMOLYTIC_3_OWNER_REQUIREMENTS"
Assert-Contains $gameplay "GRACE_STABILIZER_1_OWNER_REQUIREMENTS"
Assert-Contains $gameplay "GRACE_STABILIZER_2_OWNER_REQUIREMENTS"
Assert-Contains $gameplay "GRACE_STABILIZER_3_OWNER_REQUIREMENTS"
Assert-Contains $gameplay "RequirementSetRequirements"
Assert-Contains $gameplay "'GRACE_HAS_HEMOLYTIC_1', 'REQUIREMENT_PLAYER_HAS_COMPLETED_PROJECT', 1, 0"
Assert-Contains $gameplay "'GRACE_NOT_HAS_HEMOLYTIC_2', 'REQUIREMENT_PLAYER_HAS_COMPLETED_PROJECT', 1, 1"
Assert-Contains $gameplay "'GRACE_HAS_STABILIZER_1', 'REQUIREMENT_PLAYER_HAS_COMPLETED_PROJECT', 1, 0"
Assert-Contains $gameplay "'GRACE_NOT_HAS_STABILIZER_2', 'REQUIREMENT_PLAYER_HAS_COMPLETED_PROJECT', 1, 1"
Assert-Contains $gameplay "'GRACE_HAS_HEMOLYTIC_1', 'ProjectType', 'PROJECT_GRACE_HEMOLYTIC_1'"
Assert-Contains $gameplay "'GRACE_NOT_HAS_HEMOLYTIC_2', 'ProjectType', 'PROJECT_GRACE_HEMOLYTIC_2'"
Assert-Contains $gameplay "'GRACE_HAS_STABILIZER_1', 'ProjectType', 'PROJECT_GRACE_STABILIZER_1'"
Assert-Contains $gameplay "'GRACE_NOT_HAS_STABILIZER_2', 'ProjectType', 'PROJECT_GRACE_STABILIZER_2'"
Assert-Contains $gameplay "'GRACE_HEMOLYTIC_1_OWNER_REQUIREMENTS', 'GRACE_HAS_HEMOLYTIC_1'"
Assert-Contains $gameplay "'GRACE_HEMOLYTIC_1_OWNER_REQUIREMENTS', 'GRACE_NOT_HAS_HEMOLYTIC_2'"
Assert-Contains $gameplay "'GRACE_HEMOLYTIC_2_OWNER_REQUIREMENTS', 'GRACE_HAS_HEMOLYTIC_2'"
Assert-Contains $gameplay "'GRACE_HEMOLYTIC_2_OWNER_REQUIREMENTS', 'GRACE_NOT_HAS_HEMOLYTIC_3'"
Assert-Contains $gameplay "'GRACE_HEMOLYTIC_3_OWNER_REQUIREMENTS', 'GRACE_HAS_HEMOLYTIC_3'"
Assert-Contains $gameplay "'GRACE_STABILIZER_1_OWNER_REQUIREMENTS', 'GRACE_HAS_STABILIZER_1'"
Assert-Contains $gameplay "'GRACE_STABILIZER_1_OWNER_REQUIREMENTS', 'GRACE_NOT_HAS_STABILIZER_2'"
Assert-Contains $gameplay "'GRACE_STABILIZER_2_OWNER_REQUIREMENTS', 'GRACE_HAS_STABILIZER_2'"
Assert-Contains $gameplay "'GRACE_STABILIZER_2_OWNER_REQUIREMENTS', 'GRACE_NOT_HAS_STABILIZER_3'"
Assert-Contains $gameplay "'GRACE_STABILIZER_3_OWNER_REQUIREMENTS', 'GRACE_HAS_STABILIZER_3'"
Assert-Contains $gameplay "'GRACE_HEMOLYTIC_1_COMBAT', 'MODIFIER_PLAYER_UNITS_ADJUST_COMBAT_STRENGTH', 'GRACE_HEMOLYTIC_1_OWNER_REQUIREMENTS', 'REQUIREMENTS_OPPONENT_IS_BARBARIAN'"
Assert-Contains $gameplay "'GRACE_HEMOLYTIC_2_COMBAT', 'MODIFIER_PLAYER_UNITS_ADJUST_COMBAT_STRENGTH', 'GRACE_HEMOLYTIC_2_OWNER_REQUIREMENTS', 'REQUIREMENTS_OPPONENT_IS_BARBARIAN'"
Assert-Contains $gameplay "'GRACE_HEMOLYTIC_3_COMBAT', 'MODIFIER_PLAYER_UNITS_ADJUST_COMBAT_STRENGTH', 'GRACE_HEMOLYTIC_3_OWNER_REQUIREMENTS', 'REQUIREMENTS_OPPONENT_IS_BARBARIAN'"
Assert-Contains $gameplay "'GRACE_STABILIZER_1_COMBAT', 'MODIFIER_PLAYER_UNITS_ADJUST_COMBAT_STRENGTH', 'GRACE_STABILIZER_1_OWNER_REQUIREMENTS', NULL"
Assert-Contains $gameplay "'GRACE_STABILIZER_2_COMBAT', 'MODIFIER_PLAYER_UNITS_ADJUST_COMBAT_STRENGTH', 'GRACE_STABILIZER_2_OWNER_REQUIREMENTS', NULL"
Assert-Contains $gameplay "'GRACE_STABILIZER_3_COMBAT', 'MODIFIER_PLAYER_UNITS_ADJUST_COMBAT_STRENGTH', 'GRACE_STABILIZER_3_OWNER_REQUIREMENTS', NULL"
Assert-Contains $gameplay "'GRACE_HEMOLYTIC_3_COMBAT', 'Amount', 15"
Assert-Contains $gameplay "'GRACE_STABILIZER_3_COMBAT', 'Amount', 15"
Assert-Contains $gameplay "'GRACE_STEROID_HEALING', '5'"
Assert-DoesNotMatch $gameplay "ABILITY_GRACE_HEMOLYTIC_[123]', 'KIND_ABILITY"
Assert-DoesNotMatch $gameplay "ABILITY_GRACE_STABILIZER_[123]', 'KIND_ABILITY"
Assert-DoesNotMatch $gameplay "ABILITY_GRACE_HEMOLYTIC_[123]', 'CLASS_ALL_UNITS"
Assert-DoesNotMatch $gameplay "ABILITY_GRACE_STABILIZER_[123]', 'CLASS_ALL_UNITS"
Assert-NotContains $gameplay "UnitAbilities"
Assert-NotContains $gameplay "UnitAbilityModifiers"
Assert-NotContains $gameplay "MODIFIER_UNIT_ADJUST_COMBAT_STRENGTH"
Assert-DoesNotMatch $gameplay "ABILITY_GRACE_STEROID_[123]', 'KIND_ABILITY"
Assert-DoesNotMatch $gameplay "ABILITY_GRACE_STEROID_[123]', 'CLASS_ALL_UNITS"
Assert-DoesNotMatch $gameplay "ABILITY_GRACE_STEROID_[123]', 'LOC_ABILITY_GRACE_STEROID"
Assert-NotContains $gameplay "GRACE_ATTACH_HEMOLYTIC_"
Assert-NotContains $gameplay "GRACE_ATTACH_STABILIZER_"
Assert-NotContains $gameplay "REQUIREMENT_UNIT_HAS_ABILITY"
Assert-NotContains $gameplay "GRACE_REQUIRES_NO_HEMOLYTIC"
Assert-NotContains $gameplay "GRACE_REQUIRES_NO_STABILIZER"
Assert-NotContains $gameplay "GRACE_STEROID_1_COMBAT"
Assert-NotContains $gameplay "GRACE_STEROID_2_COMBAT"
Assert-NotContains $gameplay "GRACE_STEROID_3_COMBAT"
Assert-NotContains $gameplay "GRACE_STEROID_DEFENSE"
Assert-NotContains $gameplay "BUILDING_RHODES_HILL_SANATORIUM"

Assert-Contains $colors "<Colors>"
Assert-Contains $colors "<PlayerColors>"
Assert-Contains $colors "<Type>LEADER_GRACE_ASHCROFT</Type>"
Assert-Contains $colors "<Usage>Unique</Usage>"
Assert-Contains $colors "<Type>COLOR_PLAYER_GRACE_LIGHT_BLUE</Type>"
Assert-Contains $colors "<Type>COLOR_PLAYER_GRACE_YELLOW</Type>"
Assert-Contains $colors "<Type>COLOR_PLAYER_GRACE_PURPLE</Type>"
Assert-Contains $colors "<Color>93,205,236,255</Color>"
Assert-Contains $colors "<Color>246,218,92,255</Color>"
Assert-Contains $colors "<Color>139,98,232,255</Color>"
Assert-Contains $colors "<PrimaryColor>COLOR_PLAYER_GRACE_LIGHT_BLUE</PrimaryColor>"
Assert-Contains $colors "<SecondaryColor>COLOR_PLAYER_GRACE_YELLOW</SecondaryColor>"
Assert-Contains $colors "<Alt1PrimaryColor>COLOR_PLAYER_GRACE_PURPLE</Alt1PrimaryColor>"
Assert-Contains $colors "<Alt1SecondaryColor>COLOR_PLAYER_GRACE_YELLOW</Alt1SecondaryColor>"

Assert-Contains $text "LOC_CIVILIZATION_ELPIS_PROTOCOL_NAME"
Assert-Contains $text "LOC_LEADER_GRACE_ASHCROFT_NAME"
Assert-Contains $text "LOC_DISTRICT_GRACE_ARK_NAME"
Assert-Contains $text "LOC_RESOURCE_INFECTED_BLOOD_NAME"
Assert-Contains $text "LOC_ABILITY_GRACE_HEMOLYTIC_3_NAME"
Assert-Contains $text "LOC_PROJECT_GRACE_HEMOLYTIC_1_NAME"
Assert-Contains $text "LOC_PROJECT_GRACE_HEMOLYTIC_2_NAME"
Assert-Contains $text "LOC_PROJECT_GRACE_HEMOLYTIC_3_NAME"
Assert-Contains $text "LOC_PROJECT_GRACE_STABILIZER_1_NAME"
Assert-Contains $text "LOC_PROJECT_GRACE_STABILIZER_2_NAME"
Assert-Contains $text "LOC_PROJECT_GRACE_STABILIZER_3_NAME"
Assert-Contains $text "LOC_PROJECT_GRACE_STEROID_1_NAME"
Assert-Contains $text "LOC_PROJECT_GRACE_STEROID_2_NAME"
Assert-Contains $text "LOC_PROJECT_GRACE_STEROID_3_NAME"
Assert-Contains $text "LOC_PROJECT_GRACE_BLOOD_SAMPLE_ANALYSIS_NAME"
Assert-Contains $text "LOC_PROJECT_GRACE_ABNORMAL_PATHOLOGY_NAME"
Assert-Contains $text "LOC_PROJECT_GRACE_STRATEGIC_MATERIAL_SYNTHESIS_NAME"
Assert-Contains $text "溶血剂 III"
Assert-Contains $text "稳定剂 III"
Assert-Contains $text "类固醇 III"
Assert-Contains $text "每回合开始时所有受伤单位恢复 +15 [ICON_Damaged] 生命值"
Assert-Contains $text "方舟"
Assert-Contains $text "方舟的 [ICON_Science] 科技相邻加成也提供等额 [ICON_Production] 生产力"
Assert-Contains $text "每个其他相邻区域"
Assert-Contains $text "每个相邻可建造改良设施"
Assert-Contains $text "研究“货币”后"
Assert-Contains $text "陆地远程单位获得 +1 攻击距离和 +1 视野"
Assert-Contains $text "LOC_GRACE_ARK_GARRISON_RANGE_PREVIEW"
Assert-Contains $text "LOC_GRACE_ARK_GARRISON_SIGHT_PREVIEW"
Assert-NotContains $text "LOC_GRACE_ARK_PRODUCTION_MIRROR_DESCRIPTION"
Assert-NotContains $text "LOC_GRACE_ARK_CITY_CENTER_PRODUCTION_DESCRIPTION"
Assert-NotContains $text "LOC_GRACE_ARK_DISTRICT_PRODUCTION_DESCRIPTION"
Assert-NotContains $text "LOC_GRACE_ARK_IMPROVEMENT_PRODUCTION_DESCRIPTION"
Assert-Contains $text "LOC_GRACE_NOTIFICATION_WRITING_EUREKA"
Assert-Contains $text "LOC_GRACE_NOTIFICATION_BSAA_GOLD_GAINED"
Assert-Contains $text "LOC_GRACE_NOTIFICATION_STRATEGIC_SYNTHESIS_DONE"
Assert-Contains $text "LOC_GRACE_NOTIFICATION_STRATEGIC_SYNTHESIS_NO_TARGET"
Assert-Contains $text "LOC_GRACE_NOTIFICATION_PATHOLOGY_DONE"
Assert-Contains $text "LOC_GRACE_NOTIFICATION_EUREKA_FALLBACK_PATHOLOGY"
Assert-Contains $text "消耗 1 感染者血液"
Assert-Contains $text "BSAA补给箱"
Assert-Contains $text "拥有感染者血液时，单位升级金币费用降低 50%"
Assert-Contains $text "每次成功升级消耗 1 感染者血液"
Assert-Contains $text "病理人才资助"
Assert-Contains $text "战略物资合成"
Assert-Contains $text "当前城市每回合"
Assert-NotContains $text "消耗 3 感染者血液"
Assert-NotContains $text "LOC_GRACE_NOTIFICATION_NOT_ENOUGH_BLOOD"
Assert-NotContains $text "LOC_GRACE_NOTIFICATION_PROJECT_BLOOD_COST_SETTLED"
Assert-NotContains $text "LOC_PROJECT_GRACE_HEMOLYTIC_AGENT_NAME"
Assert-DoesNotMatch $text "LOC_PROJECT_GRACE_STABILIZER_NAME['""]"
Assert-DoesNotMatch $text "LOC_PROJECT_GRACE_STEROID_NAME['""]"
Assert-NotContains $text "LOC_GRACE_STEROID_PREVIEW"
Assert-NotContains $text "方舟复制的学院相邻加成"
Assert-NotContains $text "LOC_BUILDING_RHODES_HILL_SANATORIUM_NAME"
Assert-NotContains $text "罗兹山疗养院"
Assert-NotContains $text "隔离协议复盘"
Assert-NotContains $text "奖励随时代提高"

Assert-Contains $lua "RESOURCE_INFECTED_BLOOD"
Assert-Contains $lua "GetResourceAmount"
Assert-Contains $lua "ChangeResourceAmount"
Assert-NotContains $lua "SpendProjectBloodRemainder"
Assert-NotContains $lua "GRACE_PROJECT_BLOOD_COST"
Assert-NotContains $lua "GRACE_NATIVE_PROJECT_BLOOD_COST"
Assert-Contains $lua "GRACE_WRITING_BOOST_GRANTED"
Assert-Contains $lua "TriggerBoost(TECH_WRITING_INDEX)"
Assert-Contains $lua "Events.CityProjectCompleted.Add"
Assert-Contains $lua "Events.UnitUpgraded.Add"
Assert-Contains $lua "OnUnitUpgraded"
Assert-Contains $lua "recentUpgradeBloodSpends"
Assert-Contains $lua 'local upgradeKey = tostring(currentTurn) .. ":"'
Assert-Contains $lua "ChangeBlood(playerID, -1"
Assert-Contains $lua "LOC_GRACE_NOTIFICATION_UNIT_UPGRADED_BLOOD_SPENT"
Assert-Contains $lua "bCancelled"
Assert-Contains $lua "if bCancelled == true then"
Assert-Contains $lua "bIsFirstTime"
Assert-Contains $lua "if bIsFirstTime == false then"
Assert-Contains $lua "STEROID_LAST_HEAL_TURN"
Assert-Contains $lua "ForceHealUnit"
Assert-Contains $lua "unit:ChangeDamage(-actualHeal)"
Assert-Contains $lua "Steroid healing applied"
Assert-NotContains $lua "UnitManager.ChangeDamage"
Assert-Contains $lua "Events.UnitKilledInCombat.Add"
Assert-Contains $lua "elseif Events.Combat ~= nil then"
Assert-Contains $lua "Events.Combat.Add"
Assert-Contains $lua "Events.ImprovementActivated.Add"
Assert-Contains $lua "OnImprovementActivated"
Assert-Contains $lua "IsBarbarianCampImprovement"
Assert-Contains $lua "GRACE_BLOOD_PER_BARBARIAN_CAMP"
Assert-NotContains $lua "Events.UnitAddedToMap.Add"
Assert-NotContains $lua "OnUnitAddedToMap"
Assert-NotContains $lua 'local HEMOLYTIC_LEVEL = "GRACE_HEMOLYTIC_LEVEL"'
Assert-NotContains $lua 'local STABILIZER_LEVEL = "GRACE_STABILIZER_LEVEL"'
Assert-NotContains $lua "propertyName = HEMOLYTIC_LEVEL"
Assert-NotContains $lua "propertyName = STABILIZER_LEVEL"
Assert-NotContains $lua "HEMOLYTIC_ABILITIES"
Assert-NotContains $lua "STABILIZER_ABILITIES"
Assert-NotContains $lua "SetUnitAbilityLevel"
Assert-NotContains $lua "ApplyEnhancerLevelToUnit"
Assert-NotContains $lua "ApplyEnhancerLevelToUnits"
Assert-NotContains $lua "GetUnitAbility"
Assert-NotContains $lua "GetAbilityCount"
Assert-NotContains $lua "ChangeAbilityCount"
Assert-NotContains $lua "GetUnitByID"
Assert-Contains $lua "PROJECT_GRACE_HEMOLYTIC_1"
Assert-Contains $lua "PROJECT_GRACE_HEMOLYTIC_2"
Assert-Contains $lua "PROJECT_GRACE_HEMOLYTIC_3"
Assert-Contains $lua "PROJECT_GRACE_STABILIZER_1"
Assert-Contains $lua "PROJECT_GRACE_STABILIZER_2"
Assert-Contains $lua "PROJECT_GRACE_STABILIZER_3"
Assert-Contains $lua "PROJECT_GRACE_STEROID_1"
Assert-Contains $lua "PROJECT_GRACE_STEROID_2"
Assert-Contains $lua "PROJECT_GRACE_STEROID_3"
Assert-Contains $lua "ENHANCER_PROJECTS"
Assert-Contains $lua "PROJECT_GRACE_BLOOD_SAMPLE_ANALYSIS"
Assert-Contains $lua "PROJECT_GRACE_STRATEGIC_MATERIAL_SYNTHESIS"
Assert-Contains $lua "TriggerBoost"
Assert-NotContains $lua "TryAwardKillGold"
Assert-NotContains $lua "ChangeGoldBalance"
Assert-NotContains $lua "GRACE_KILL_GOLD_PERCENT"
Assert-NotContains $lua "unitTypeCache"
Assert-NotContains $lua "CacheUnitType"
Assert-NotContains $lua "ClearUnitTypeCache"
Assert-NotContains $lua "CacheExistingUnitTypes"
Assert-NotContains $lua "recentGoldAwards"
Assert-NotContains $lua "GetCachedUnitType"
Assert-NotContains $lua "baseCombat <= 0"
Assert-Contains $lua "HandleStrategicMaterialSynthesis"
Assert-Contains $lua "FindStrategicSynthesisTarget"
Assert-Contains $lua "GetResourceStockpileCap"
Assert-Contains $lua "GRACE_STRATEGIC_MAX_BLOOD_PER_PROJECT"
Assert-Contains $lua "GRACE_STRATEGIC_RESOURCE_PER_BLOOD"
Assert-Contains $lua "HandlePathologyFunding"
Assert-Contains $lua "CalculatePathologyRewardPerBlood"
Assert-Contains $lua "GetCityGreatScientistPointsPerTurn"
Assert-Contains $lua "GetCityScienceYield"
Assert-Contains $lua "GRACE_PATHOLOGY_MAX_BLOOD_PER_PROJECT"
Assert-Contains $lua "GRACE_PATHOLOGY_CITY_YIELD_PERCENT"
Assert-Contains $lua "GRACE_PATHOLOGY_MIN_REWARD_PER_BLOOD"
Assert-Contains $lua 'math.min(GetParam("GRACE_PATHOLOGY_MAX_BLOOD_PER_PROJECT", 4)'
Assert-Contains $lua 'math.min(GetParam("GRACE_STRATEGIC_MAX_BLOOD_PER_PROJECT", 5)'
Assert-DoesNotMatch $lua "tonumber\s*\(\s*[A-Za-z0-9_:.]+GetProperty\s*\("
Assert-NotContains $lua "GetEraScaledValue"
Assert-NotContains $lua "HandleContainmentReview"
Assert-NotContains $lua "PROJECT_GRACE_CONTAINMENT_REVIEW"
Assert-NotContains $lua "GRACE_EUREKA_FALLBACK_SCIENCE"
Assert-NotContains $lua "GRACE_GREAT_SCIENTIST_POINTS"
Assert-NotContains $lua "GRACE_CONTAINMENT_REVIEW_SCIENCE"
Assert-NotContains $lua "AttachModifierByID"
Assert-NotContains $lua "GRACE_ATTACH_HEMOLYTIC_"
Assert-NotContains $lua "GRACE_ATTACH_STABILIZER_"
Assert-NotContains $lua "PROJECT_GRACE_HEMOLYTIC_AGENT"
Assert-DoesNotMatch $lua "PROJECT_GRACE_STABILIZER['""]"
Assert-DoesNotMatch $lua "PROJECT_GRACE_STEROID['""]"
Assert-NotContains $lua "LuaEvents.GraceBloodChanged"
Assert-NotContains $lua "local INFECTED_BLOOD"
Assert-NotContains $lua "SetBlood"
Assert-NotContains $lua "TrySpendBlood"
Assert-NotContains $lua "GetProperty(INFECTED_BLOOD"
Assert-NotContains $lua "SetProperty(INFECTED_BLOOD"

Assert-Contains $icons "ICON_RESOURCE_INFECTED_BLOOD"
Assert-Contains $icons "RESOURCE_INFECTED_BLOOD"
Assert-Contains $icons "ICON_LEADER_GRACE_ASHCROFT"
Assert-Contains $icons "ICON_DISTRICT_GRACE_ARK"
Assert-Contains $icons "ICON_DISTRICT_GRACE_ARK_FOW"
Assert-Contains $icons "ICON_PROJECT_GRACE_HEMOLYTIC_1"
Assert-Contains $icons "ICON_PROJECT_GRACE_HEMOLYTIC_2"
Assert-Contains $icons "ICON_PROJECT_GRACE_HEMOLYTIC_3"
Assert-Contains $icons "ICON_PROJECT_GRACE_STABILIZER_1"
Assert-Contains $icons "ICON_PROJECT_GRACE_STABILIZER_2"
Assert-Contains $icons "ICON_PROJECT_GRACE_STABILIZER_3"
Assert-Contains $icons "ICON_PROJECT_GRACE_STEROID_1"
Assert-Contains $icons "ICON_PROJECT_GRACE_STEROID_2"
Assert-Contains $icons "ICON_PROJECT_GRACE_STEROID_3"
Assert-NotContains $icons "ICON_PROJECT_GRACE_HEMOLYTIC_AGENT"
Assert-DoesNotMatch $icons "ICON_PROJECT_GRACE_STABILIZER['""]"
Assert-DoesNotMatch $icons "ICON_PROJECT_GRACE_STEROID['""]"
Assert-Contains $icons "ICON_PROJECT_GRACE_STRATEGIC_MATERIAL_SYNTHESIS"
Assert-NotContains $icons "ICON_PROJECT_GRACE_CONTAINMENT_REVIEW"
Assert-Contains $icons "IconTextureAtlases"
Assert-Contains $icons "IconDefinitions"
Assert-Contains $icons "ICON_ATLAS_GRACE_LEADER"
Assert-Contains $icons "ICON_ATLAS_GRACE_INFECTED_BLOOD"
Assert-Contains $icons "ICON_ATLAS_GRACE_HEMOLYTIC"
Assert-Contains $icons "ICON_ATLAS_GRACE_STABILIZER"
Assert-Contains $icons "ICON_ATLAS_GRACE_STEROID"
Assert-Contains $icons "ICON_ATLAS_FONT_ICON_BASELINE_6"
Assert-Contains $icons "ICON_ATLAS_DISTRICTS"
Assert-Contains $icons "ICON_ATLAS_PROJECTS"
Assert-Contains $icons "'ICON_PROJECT_GRACE_HEMOLYTIC_1', 'ICON_ATLAS_GRACE_HEMOLYTIC', 0"
Assert-Contains $icons "'ICON_PROJECT_GRACE_STABILIZER_1', 'ICON_ATLAS_GRACE_STABILIZER', 0"
Assert-Contains $icons "'ICON_PROJECT_GRACE_STEROID_1', 'ICON_ATLAS_GRACE_STEROID', 0"
Assert-Contains $icons "'ICON_PROJECT_GRACE_BLOOD_SAMPLE_ANALYSIS', 'ICON_ATLAS_PROJECTS', 16"
Assert-Contains $icons "'ICON_PROJECT_GRACE_ABNORMAL_PATHOLOGY', 'ICON_ATLAS_PROJECTS', 16"
Assert-Contains $icons "'ICON_PROJECT_GRACE_STRATEGIC_MATERIAL_SYNTHESIS', 'ICON_ATLAS_PROJECTS', 16"
Assert-NotContains $icons "'ICON_RESOURCE_INFECTED_BLOOD', 'ICON_ATLAS_RESOURCES'"

Assert-Contains $districtArtDef "DISTRICT_GRACE_ARK"
Assert-Contains $districtArtDef "<m_ElementName text=""DISTRICT_CAMPUS""/>"
Assert-Contains $districtArtDef "<m_ArtDefPath text=""Landmarks.artdef""/>"
Assert-Contains $districtArtDef "<m_ElementName text=""Campus""/>"
Assert-Contains $districtArtDef "<m_ElementName text=""Campus_Pillaged""/>"
Assert-Contains $districtArtDef "<m_ElementName text=""Campus_UnderConstruction""/>"
Assert-Contains $districtArtDef "Build_District_Campus"
Assert-Contains $districtArtDef "PLAY_AMBIENCE_DISTRICT_CAMPUS"
Assert-Contains $districtArtDef "STOP_AMBIENCE_DISTRICT_CAMPUS"
Assert-Contains $fallbackLeaderArtDef "<m_TemplateName text=""LeaderFallback""/>"
Assert-Contains $fallbackLeaderArtDef "<m_Name text=""LEADER_GRACE_ASHCROFT""/>"
Assert-Contains $fallbackLeaderArtDef "<m_Name text=""DEFAULT""/>"
Assert-Contains $fallbackLeaderArtDef "<m_EntryName text=""FALLBACK_NEUTRAL_GRACE_ASHCROFT""/>"
Assert-Contains $fallbackLeaderArtDef "<m_XLPClass text=""LeaderFallback""/>"
Assert-Contains $fallbackLeaderArtDef "<m_XLPPath text=""leaderfallbacks.xlp""/>"
Assert-Contains $fallbackLeaderArtDef "<m_BLPPackage text=""LeaderFallbacks""/>"
Assert-Contains $fallbackLeaderArtDef "<m_LibraryName text=""LeaderFallback""/>"
Assert-Contains $artDep "<name text=""GraceAshcroft""/>"
Assert-Contains $artDep "<id text=""6b8f93c1-7c19-4f06-a7c5-9ef0f1c7c911""/>"
Assert-Contains $artDep "<ArtDefPath text=""Districts.artdef""/>"
Assert-Contains $artDep "<ConsumerName text=""LeaderFallback""/>"
Assert-Contains $artDep "<Element text=""FallbackLeaders.artdef""/>"
Assert-Contains $artDep "<Element text=""LeaderFallback""/>"
Assert-Contains $artDep "<ConsumerName text=""UI""/>"
Assert-Contains $artDep "<Element text=""UITexture""/>"
Assert-Contains $artDep "<ArtDefPath text=""FallbackLeaders.artdef""/>"
Assert-Contains $artDep "<LibraryName text=""LeaderFallback""/>"
Assert-Contains $artDep "<Element text=""LeaderFallbacks.blp""/>"
Assert-Contains $artDep "<LibraryName text=""UITexture""/>"
Assert-Contains $artDep "<Element text=""GraceUITexture.blp""/>"

Assert-Contains $uiTextureXlp "<m_ClassName text=""UITexture""/>"
Assert-Contains $uiTextureXlp "<m_PackageName text=""GraceUITexture""/>"
Assert-Contains $uiTextureXlp "<m_EntryID text=""IMG_LOADING_BACKGROUND_GRACE_ASHCROFT""/>"
Assert-Contains $uiTextureXlp "<m_EntryID text=""IMG_LOADING_FOREGROUND_GRACE_ASHCROFT""/>"
Assert-Contains $uiTextureXlp "<m_EntryID text=""IMG_LOADING_SCENE_GRACE_ASHCROFT""/>"
Assert-Contains $uiTextureXlp "<m_EntryID text=""IMG_LOADING_FOREGROUND_BLANK_GRACE_ASHCROFT""/>"
Assert-Contains $uiTextureXlp "<m_ObjectName text=""GraceAshcroft_Background_UI""/>"
Assert-Contains $uiTextureXlp "<m_ObjectName text=""GraceAshcroft_Foreground_UI""/>"
Assert-Contains $uiTextureXlp "<m_ObjectName text=""GraceAshcroft_LoadingScene_UI""/>"
Assert-Contains $uiTextureXlp "<m_ObjectName text=""GraceAshcroft_LoadingBlank_UI""/>"
Assert-Contains $uiTextureXlp "<m_EntryID text=""GraceAshcroft_Icon_Leader_256""/>"
Assert-Contains $uiTextureXlp "<m_EntryID text=""GraceAshcroft_Icon_InfectedBlood_256""/>"
Assert-Contains $uiTextureXlp "<m_EntryID text=""GraceAshcroft_Icon_Hemolytic_256""/>"
Assert-Contains $uiTextureXlp "<m_EntryID text=""GraceAshcroft_Icon_Stabilizer_256""/>"
Assert-Contains $uiTextureXlp "<m_EntryID text=""GraceAshcroft_Icon_Steroid_256""/>"
Assert-NotContains $uiTextureXlp $oldBoardBase
Assert-Contains $leaderFallbackXlp "<m_ClassName text=""LeaderFallback""/>"
Assert-Contains $leaderFallbackXlp "<m_PackageName text=""LeaderFallbacks""/>"
Assert-Contains $leaderFallbackXlp "<m_EntryID text=""FALLBACK_NEUTRAL_GRACE_ASHCROFT""/>"
Assert-Contains $leaderFallbackXlp "<m_ObjectName text=""GraceAshcroft_Foreground_Fallback""/>"
Assert-NotContains $leaderFallbackXlp $oldBoardBase

Assert-Contains $backgroundUiEntity "<m_ClassName text=""UserInterface""/>"
Assert-Contains $backgroundUiEntity "<m_Width>2048</m_Width>"
Assert-Contains $backgroundUiEntity "<m_Height>1024</m_Height>"
Assert-Contains $backgroundUiEntity "<m_RelativePath text=""../GraceAshcroft_Background.dds""/>"
Assert-Contains $backgroundUiEntity "<m_Name text=""GraceAshcroft_Background_UI""/>"
Assert-Contains $backgroundUiEntity "<Element text=""UserInterface""/>"
Assert-Contains $foregroundUiEntity "<m_ClassName text=""UserInterface""/>"
Assert-Contains $foregroundUiEntity "<m_Width>1024</m_Width>"
Assert-Contains $foregroundUiEntity "<m_Height>2048</m_Height>"
Assert-Contains $foregroundUiEntity "<m_RelativePath text=""../GraceAshcroft_Foreground.dds""/>"
Assert-Contains $foregroundUiEntity "<m_Name text=""GraceAshcroft_Foreground_UI""/>"
Assert-Contains $foregroundUiEntity "<Element text=""UserInterface""/>"
Assert-Contains $foregroundFallbackEntity "<m_ClassName text=""Leader_Fallback""/>"
Assert-Contains $foregroundFallbackEntity "<m_Width>1024</m_Width>"
Assert-Contains $foregroundFallbackEntity "<m_Height>2048</m_Height>"
Assert-Contains $foregroundFallbackEntity "<m_RelativePath text=""../GraceAshcroft_Foreground.dds""/>"
Assert-Contains $foregroundFallbackEntity "<m_Name text=""GraceAshcroft_Foreground_Fallback""/>"
Assert-Contains $foregroundFallbackEntity "<Element text=""Leader_Fallback""/>"
Assert-Contains $foregroundFallbackEntity "<Element text=""Leader""/>"
Assert-Contains $foregroundFallbackEntity "<Element text=""Fallback""/>"
Assert-NotContains $backgroundUiEntity $oldBoardBase
Assert-NotContains $foregroundUiEntity $oldBoardBase
Assert-NotContains $foregroundFallbackEntity $oldBoardBase
Assert-Contains $loadingSceneUiEntity "<m_ClassName text=""UserInterface""/>"
Assert-Contains $loadingSceneUiEntity "<m_Width>2048</m_Width>"
Assert-Contains $loadingSceneUiEntity "<m_Height>1024</m_Height>"
Assert-Contains $loadingSceneUiEntity "<m_RelativePath text=""../GraceAshcroft_LoadingScene.dds""/>"
Assert-Contains $loadingSceneUiEntity "<m_Name text=""GraceAshcroft_LoadingScene_UI""/>"
Assert-Contains $loadingSceneUiEntity "<Element text=""UserInterface""/>"
Assert-Contains $loadingBlankUiEntity "<m_ClassName text=""UserInterface""/>"
Assert-Contains $loadingBlankUiEntity "<m_Width>8</m_Width>"
Assert-Contains $loadingBlankUiEntity "<m_Height>8</m_Height>"
Assert-Contains $loadingBlankUiEntity "<m_RelativePath text=""../GraceAshcroft_LoadingBlank.dds""/>"
Assert-Contains $loadingBlankUiEntity "<m_Name text=""GraceAshcroft_LoadingBlank_UI""/>"
Assert-Contains $loadingBlankUiEntity "<Element text=""UserInterface""/>"
Assert-NotContains $loadingSceneUiEntity $oldBoardBase
Assert-NotContains $loadingBlankUiEntity $oldBoardBase

Assert-BinaryContains $uiTextureBlp "IMG_LOADING_BACKGROUND_GRACE_ASHCROFT"
Assert-BinaryContains $uiTextureBlp "IMG_LOADING_FOREGROUND_GRACE_ASHCROFT"
Assert-BinaryContains $uiTextureBlp "IMG_LOADING_SCENE_GRACE_ASHCROFT"
Assert-BinaryContains $uiTextureBlp "IMG_LOADING_FOREGROUND_BLANK_GRACE_ASHCROFT"
Assert-BinaryContains $uiTextureBlp "GraceAshcroft_Icon_Leader_256"
Assert-BinaryContains $uiTextureBlp "GraceAshcroft_Icon_InfectedBlood_256"
Assert-BinaryContains $uiTextureBlp "GraceAshcroft_Icon_Hemolytic_256"
Assert-BinaryContains $uiTextureBlp "GraceAshcroft_Icon_Stabilizer_256"
Assert-BinaryContains $uiTextureBlp "GraceAshcroft_Icon_Steroid_256"
Assert-BinaryContains $leaderFallbackBlp "FALLBACK_NEUTRAL_GRACE_ASHCROFT"
Assert-BinaryContains $leaderFallbackBlp "GraceAshcroft_Foreground_Fallback"
Assert-BinaryNotContains $uiTextureBlp $oldBoardBase
Assert-BinaryNotContains $leaderFallbackBlp $oldBoardBase

Write-Host "Grace Ashcroft mod static validation passed."
