$ErrorActionPreference = "Stop"

$target = Join-Path $PSScriptRoot "check_static.py"
& python $target @args
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
