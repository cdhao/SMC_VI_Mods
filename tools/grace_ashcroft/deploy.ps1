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

if (Test-Path -LiteralPath $target) {
    Remove-Item -LiteralPath $target -Recurse -Force
}
New-Item -ItemType Directory -Path $ModsRoot -Force | Out-Null
Copy-Item -LiteralPath $source -Destination $target -Recurse -Force

Write-Host "GraceAshcroft deployed to: $target"
