# ASCII-only. PowerShell 7+
# Wrapper to run all guards consistently with optional --strict.

param(
    [switch]$Strict
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version 3

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$guardParameters = @{}
if ($Strict) {
    $guardParameters["Strict"] = $true
}

function Run-Step($name, $script) {
    Write-Host ("Running {0}..." -f $name)
    & $script @guardParameters
    if ($LASTEXITCODE -ne 0) { throw ("{0} failed." -f $name) }
}

# Example ordering: roadmap first, then commit
if (Test-Path "$root/roadmap_guard.ps1") {
    Run-Step "roadmap_guard.ps1" "$root/roadmap_guard.ps1"
}

if (Test-Path "$root/commit_guard.ps1") {
    Run-Step "commit_guard.ps1" "$root/commit_guard.ps1"
}

Write-Host "All guards passed."
