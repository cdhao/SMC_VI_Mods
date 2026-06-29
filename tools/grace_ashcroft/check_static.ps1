$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$buildScript = Join-Path $PSScriptRoot "build_assets.py"
$cookScript = Join-Path $PSScriptRoot "cook_assets.ps1"
$deployScript = Join-Path $PSScriptRoot "deploy.ps1"
$commonTexture = Join-Path $repoRoot "tools\common\civ6_texture.py"
$workspaceCleanupScript = Join-Path $repoRoot "tools\cleanup_workspace.ps1"
$rootBuildWrapper = Join-Path $repoRoot "tools\build_grace_icon_assets.py"
$rootCheckWrapper = Join-Path $repoRoot "tools\check_grace_mod_static.ps1"
$legacyImplementation = Join-Path $repoRoot "tools\_check_grace_mod_static_impl.ps1"
$workflowDoc = Join-Path $repoRoot "docs\civ6-mod-workflow.md"
$graceDoc = Join-Path $repoRoot "docs\mods\grace-ashcroft-assets.md"
$farEastPlaceholder = Join-Path $repoRoot "tools\far_east_magic_nap_society\README.md"

function Assert-FileExists {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Missing required file: $Path"
    }
}

function Assert-ContainsText {
    param([string]$Path, [string]$Needle)
    $content = Get-Content -Raw -LiteralPath $Path
    if (-not $content.Contains($Needle)) {
        throw "Expected '$Needle' in $Path"
    }
}

function Assert-NotContainsText {
    param([string]$Path, [string]$Needle)
    $content = Get-Content -Raw -LiteralPath $Path
    if ($content.Contains($Needle)) {
        throw "Did not expect '$Needle' in $Path"
    }
}

@(
    $buildScript,
    $cookScript,
    $deployScript,
    $commonTexture,
    $workspaceCleanupScript,
    $rootBuildWrapper,
    $rootCheckWrapper,
    $legacyImplementation,
    $workflowDoc,
    $graceDoc,
    $farEastPlaceholder
) | ForEach-Object { Assert-FileExists $_ }

Assert-ContainsText $buildScript "INFECTED_BLOOD_ASSET_VERSION = 2"
Assert-ContainsText $buildScript 'INFECTED_BLOOD_PACKAGE_NAME = f"GraceResourceIconsV{INFECTED_BLOOD_ASSET_VERSION}"'
Assert-ContainsText $buildScript 'f"GraceResource_InfectedBlood_V{INFECTED_BLOOD_ASSET_VERSION}"'
Assert-ContainsText $buildScript "def cleanup_obsolete_infected_blood_assets"
Assert-ContainsText $buildScript "from tools.common.civ6_texture import"
Assert-NotContainsText $buildScript "MOD_VERSION ="
Assert-NotContainsText $buildScript "RESOURCE_ASSET_VERSION ="

Assert-ContainsText $cookScript '$infectedBloodAssetVersion = 2'
Assert-ContainsText $cookScript '$resourcePackage = "GraceResourceIconsV$infectedBloodAssetVersion"'
Assert-NotContainsText $cookScript '$resourcePackage = "GraceResourceIconsV2"'

Assert-ContainsText $deployScript "[System.IO.Path]::GetFullPath"
Assert-ContainsText $deployScript "StartsWith"
Assert-ContainsText $deployScript "EndsWith"
Assert-ContainsText $deployScript "Refusing"

Assert-ContainsText $commonTexture "def write_rgba_dds"
Assert-ContainsText $commonTexture "def resize_icon"
Assert-ContainsText $commonTexture "def texture_instance_xml"
Assert-NotContainsText $commonTexture "GraceAshcroft"
Assert-NotContainsText $commonTexture "InfectedBlood"

Assert-ContainsText $workspaceCleanupScript "[System.IO.Path]::GetFullPath"
Assert-ContainsText $workspaceCleanupScript "StartsWith"
Assert-ContainsText $workspaceCleanupScript "__pycache__"
Assert-ContainsText $workspaceCleanupScript ".tmp"
Assert-ContainsText $workspaceCleanupScript "SupportsShouldProcess"
Assert-ContainsText $workspaceCleanupScript "Refusing"
Assert-NotContainsText $workspaceCleanupScript "assets\GraceAshcroft\generated"

Assert-ContainsText $rootBuildWrapper "grace_ashcroft"
Assert-ContainsText $rootBuildWrapper "build_assets.py"
Assert-ContainsText $rootCheckWrapper "grace_ashcroft"
Assert-ContainsText $rootCheckWrapper "check_static.ps1"
Assert-ContainsText $legacyImplementation "tools\grace_ashcroft\build_assets.py"
Assert-ContainsText $legacyImplementation "INFECTED_BLOOD_ASSET_VERSION = 2"
Assert-NotContainsText $legacyImplementation "MOD_VERSION = 2"
Assert-NotContainsText $legacyImplementation "RESOURCE_ASSET_VERSION = 2"

# Keep the existing deep validation intact while the public entry points move.
& $legacyImplementation @args
