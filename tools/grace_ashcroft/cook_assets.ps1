param(
    [string]$SdkRoot = $env:CIV6_SDK_ROOT,
    [string]$CookerPath = $env:CIV6_ASSET_COOKER
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$modRoot = Join-Path $repoRoot "mods\GraceAshcroft"
$buildScript = Join-Path $PSScriptRoot "build_assets.py"
$checkScript = Join-Path $PSScriptRoot "check_static.ps1"
$civilizationAssetVersion = 2
$civilizationPackage = "GraceCivilizationIconsV$civilizationAssetVersion"
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

$blpDir = Join-Path $modRoot "Platforms\Windows\BLPs"
$uiBlp = Join-Path $blpDir "GraceUITexture.blp"
$civilizationBlp = Join-Path $blpDir "$civilizationPackage.blp"
$resourceBlp = Join-Path $blpDir "$resourcePackage.blp"
Remove-Item -LiteralPath $uiBlp, $civilizationBlp, $resourceBlp -Force -ErrorAction SilentlyContinue

Push-Location $modRoot
try {
    & $CookerPath --mode XLP --platform Windows --config $configPath --pantry Images --stewpot Platforms\Windows\BLPs --log_path Logs XLPs\GraceUITexture.xlp
    if ($LASTEXITCODE -ne 0) { throw "Failed to cook GraceUITexture.xlp." }

    & $CookerPath --mode XLP --platform Windows --config $configPath --pantry Images --stewpot Platforms\Windows\BLPs --log_path Logs "XLPs\$civilizationPackage.xlp"
    if ($LASTEXITCODE -ne 0) { throw "Failed to cook $civilizationPackage.xlp." }

    & $CookerPath --mode XLP --platform Windows --config $configPath --pantry Images --stewpot Platforms\Windows\BLPs --log_path Logs "XLPs\$resourcePackage.xlp"
    if ($LASTEXITCODE -ne 0) { throw "Failed to cook $resourcePackage.xlp." }
}
finally {
    Pop-Location
}

if (-not (Test-Path -LiteralPath $uiBlp -PathType Leaf)) {
    throw "Expected cooked package was not created: $uiBlp"
}
if (-not (Test-Path -LiteralPath $civilizationBlp -PathType Leaf)) {
    throw "Expected cooked package was not created: $civilizationBlp"
}
if (-not (Test-Path -LiteralPath $resourceBlp -PathType Leaf)) {
    throw "Expected cooked package was not created: $resourceBlp"
}

python $buildScript --cleanup-mod-dds
if ($LASTEXITCODE -ne 0) { throw "Temporary DDS cleanup failed." }

& $checkScript
Write-Host "Grace Ashcroft assets cooked and validated."
