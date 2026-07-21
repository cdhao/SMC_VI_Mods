param(
    [string]$SdkRoot = $env:CIV6_SDK_ROOT,
    [string]$CookerPath = $env:CIV6_ASSET_COOKER,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$pythonScript = Join-Path $PSScriptRoot "cook_assets.py"
$pythonArgs = @($pythonScript)
if ($SdkRoot) { $pythonArgs += @("--sdk-root", $SdkRoot) }
if ($CookerPath) { $pythonArgs += @("--cooker-path", $CookerPath) }
if ($DryRun) { $pythonArgs += "--dry-run" }

& python @pythonArgs
if ($LASTEXITCODE -ne 0) { throw "Grace Ashcroft asset cooking failed." }
