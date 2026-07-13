param(
    [string]$SdkRoot = $env:CIV6_SDK_ROOT,
    [string]$CookerPath = $env:CIV6_ASSET_COOKER
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$modRoot = Join-Path $repoRoot "mods\GraceAshcroft"
$cookerRoot = Join-Path $repoRoot "assets\GraceAshcroft\cooker"
$buildScript = Join-Path $PSScriptRoot "build_assets.py"
$checkScript = Join-Path $PSScriptRoot "check_static.ps1"
$infectedBloodAssetVersion = 2
$resourcePackage = "GraceResourceIconsV$infectedBloodAssetVersion"

if (-not $SdkRoot) {
    $SdkRoot = "C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization VI SDK"
}
if (-not $CookerPath) {
    $CookerPath = Join-Path $SdkRoot "AssetModTools\Cooker\Civ6AssetCooker_FinalRelease.exe"
}
$configPath = Join-Path $SdkRoot "AssetModTools\Cooker\Civ6.cfg"

if (-not (Test-Path -LiteralPath $CookerPath -PathType Leaf)) {
    throw "Civ6 Asset Cooker not found: $CookerPath"
}
if (-not (Test-Path -LiteralPath $configPath -PathType Leaf)) {
    throw "Civ6 cooker config not found: $configPath"
}

python $buildScript
if ($LASTEXITCODE -ne 0) { throw "Grace asset generation failed." }

$cookerBlpDir = Join-Path $cookerRoot "Platforms\Windows\BLPs"
$runtimeBlpDir = Join-Path $modRoot "Platforms\Windows\BLPs"
$packageNames = @("GraceUITexture", $resourcePackage, "LeaderFallbacks")
New-Item -ItemType Directory -Path $cookerBlpDir, $runtimeBlpDir -Force | Out-Null
foreach ($packageName in $packageNames) {
    Remove-Item -LiteralPath (Join-Path $cookerBlpDir "$packageName.blp") -Force -ErrorAction SilentlyContinue
}

Push-Location $cookerRoot
try {
    & $CookerPath --mode XLP --platform Windows --config $configPath --pantry Images --stewpot Platforms\Windows\BLPs --log_path Logs XLPs\GraceUITexture.xlp
    if ($LASTEXITCODE -ne 0) { throw "Failed to cook GraceUITexture.xlp." }

    & $CookerPath --mode XLP --platform Windows --config $configPath --pantry Images --stewpot Platforms\Windows\BLPs --log_path Logs "XLPs\$resourcePackage.xlp"
    if ($LASTEXITCODE -ne 0) { throw "Failed to cook $resourcePackage.xlp." }

    & $CookerPath --mode XLP --platform Windows --config $configPath --pantry Images --stewpot Platforms\Windows\BLPs --log_path Logs XLPs\leaderfallbacks.xlp
    if ($LASTEXITCODE -ne 0) { throw "Failed to cook leaderfallbacks.xlp." }
}
finally {
    Pop-Location
}

foreach ($packageName in $packageNames) {
    $cookedBlp = Join-Path $cookerBlpDir "$packageName.blp"
    if (-not (Test-Path -LiteralPath $cookedBlp -PathType Leaf)) {
        throw "Expected cooked package was not created: $cookedBlp"
    }
    Copy-Item -LiteralPath $cookedBlp -Destination (Join-Path $runtimeBlpDir "$packageName.blp") -Force
}

python $buildScript --cleanup-cooker-dds
if ($LASTEXITCODE -ne 0) { throw "Temporary DDS cleanup failed." }

& $checkScript
Write-Host "Grace Ashcroft assets cooked and validated."
