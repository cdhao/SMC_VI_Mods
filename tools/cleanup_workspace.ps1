[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$WorkspaceRoot
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($WorkspaceRoot)) {
    $scriptRoot = $PSScriptRoot
    if ([string]::IsNullOrWhiteSpace($scriptRoot)) {
        $scriptRoot = Split-Path -Parent $PSCommandPath
    }
    $WorkspaceRoot = Split-Path -Parent $scriptRoot
}

$resolvedWorkspace = [System.IO.Path]::GetFullPath($WorkspaceRoot)
$targets = New-Object System.Collections.Generic.List[string]

$tmpPath = Join-Path $resolvedWorkspace ".tmp"
if (Test-Path -LiteralPath $tmpPath -PathType Container) {
    $targets.Add([System.IO.Path]::GetFullPath($tmpPath))
}

Get-ChildItem -LiteralPath $resolvedWorkspace -Directory -Recurse -Force -Filter "__pycache__" |
    ForEach-Object {
        $targets.Add([System.IO.Path]::GetFullPath($_.FullName))
    }

$uniqueTargets = $targets | Sort-Object -Unique

foreach ($target in $uniqueTargets) {
    if (-not $target.StartsWith($resolvedWorkspace, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to remove path outside workspace: $target"
    }
    if (-not (
        $target.EndsWith("\.tmp", [System.StringComparison]::OrdinalIgnoreCase) -or
        $target.EndsWith("\__pycache__", [System.StringComparison]::OrdinalIgnoreCase)
    )) {
        throw "Refusing to remove unexpected cleanup target: $target"
    }
}

$removed = 0
foreach ($target in $uniqueTargets) {
    if ($PSCmdlet.ShouldProcess($target, "Remove workspace temporary directory")) {
        Remove-Item -LiteralPath $target -Recurse -Force
        $removed += 1
    }
}

Write-Host "Workspace cleanup completed. Removed $removed temporary directories."
