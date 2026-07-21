[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$cleanupScript = Join-Path $PSScriptRoot "cleanup_workspace.ps1"
$exitCode = 0

try {
    & python -B (Join-Path $PSScriptRoot "grace_ashcroft\build_assets.py")
    if ($LASTEXITCODE -ne 0) {
        throw "Grace Ashcroft asset build failed."
    }

    & python -B (Join-Path $PSScriptRoot "chuuni_society\build_assets.py")
    if ($LASTEXITCODE -ne 0) {
        throw "Chuuni Society asset build failed."
    }

    & python -B -m unittest `
        tools.common.tests.test_civ6_asset_cooker `
        tools.common.tests.test_civ6_mod_config `
        tools.common.tests.test_civ6_static_checks `
        tools.common.tests.test_civ6_texture `
        tools.common.tests.test_scaffold_civ6_leader_mod `
        tools.common.tests.test_run_civ6_tool_tests `
        tools.grace_ashcroft.tests.test_check_static `
        tools.grace_ashcroft.tests.test_build_assets `
        tools.grace_ashcroft.tests.test_cook_assets `
        tools.chuuni_society.tests.test_prepare_logo `
        tools.chuuni_society.tests.test_build_assets `
        tools.chuuni_society.tests.test_check_assets `
        tools.chuuni_society.tests.test_cook_assets `
        tools.far_east_magic_nap_society.tests.test_check_static `
        -v
    if ($LASTEXITCODE -ne 0) {
        throw "Civilization VI tool tests failed."
    }

    & python -B (Join-Path $PSScriptRoot "grace_ashcroft\check_static.py")
    if ($LASTEXITCODE -ne 0) {
        throw "Grace Ashcroft static validation failed."
    }

    & python -B (Join-Path $PSScriptRoot "chuuni_society\check_static.py")
    if ($LASTEXITCODE -ne 0) {
        throw "Chuuni Society asset validation failed."
    }

    & python -B (Join-Path $PSScriptRoot "far_east_magic_nap_society\check_static.py")
    if ($LASTEXITCODE -ne 0) {
        throw "Chuuni Society gameplay validation failed."
    }
}
catch {
    $exitCode = 1
    Write-Error $_
}
finally {
    & $cleanupScript -WorkspaceRoot $repoRoot
    if ($LASTEXITCODE -ne 0) {
        $exitCode = 1
        Write-Error "Workspace cleanup failed."
    }
}

exit $exitCode
