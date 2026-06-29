param(
    [string]$ModsRoot = (Join-Path ([Environment]::GetFolderPath("MyDocuments")) "My Games\Sid Meier's Civilization VI\Mods"),
    [switch]$SkipValidation
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$source = Join-Path $repoRoot "mods\GraceAshcroft"
$target = Join-Path $ModsRoot "GraceAshcroft"
$checkScript = Join-Path $PSScriptRoot "check_static.ps1"

if (-not $SkipValidation) {
    & $checkScript
}
if (-not (Test-Path -LiteralPath $source -PathType Container)) {
    throw "GraceAshcroft source directory not found: $source"
}

$resolvedModsRoot = [System.IO.Path]::GetFullPath($ModsRoot)
$resolvedTarget = [System.IO.Path]::GetFullPath($target)
if (-not $resolvedTarget.StartsWith($resolvedModsRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing to deploy outside ModsRoot: $resolvedTarget"
}
if (-not $resolvedTarget.EndsWith("\GraceAshcroft", [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing unexpected GraceAshcroft target path: $resolvedTarget"
}

New-Item -ItemType Directory -Path $resolvedModsRoot -Force | Out-Null
if (Test-Path -LiteralPath $resolvedTarget) {
    Remove-Item -LiteralPath $resolvedTarget -Recurse -Force
}
Copy-Item -LiteralPath $source -Destination $resolvedTarget -Recurse -Force

Write-Host "GraceAshcroft deployed to: $resolvedTarget"
