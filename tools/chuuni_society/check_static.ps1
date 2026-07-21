param([string]$Python = "python")

$ErrorActionPreference = "Stop"
$scriptPath = Join-Path $PSScriptRoot "check_static.py"
& $Python -B $scriptPath
exit $LASTEXITCODE
