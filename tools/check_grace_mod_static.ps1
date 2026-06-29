$ErrorActionPreference = "Stop"
$target = Join-Path $PSScriptRoot "grace_ashcroft\check_static.ps1"
& $target @args
