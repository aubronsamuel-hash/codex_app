# ASCII-only. PowerShell 7+
# Wrapper to run all guards consistently with optional --strict.

param(
    [switch]$Strict
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version 3

$root = Split-Path -Parent $MyInvocation.MyCommand.Path

$guards = @(
    @{ name = 'roadmap_guard.ps1'; path = Join-Path $root 'roadmap_guard.ps1'; fix = 'Run: pwsh -File tools/codex/ensure_roadmap_ref.ps1 -StepRef "docs/roadmap/step-XX.md"' },
    @{ name = 'commit_guard.ps1'; path = Join-Path $root 'commit_guard.ps1'; fix = 'Ensure docs/codex/last_output.json is valid and include the roadmap Ref in the PR body.' }
)

$strictArgs = @()
if ($Strict) { $strictArgs += '-Strict' }

foreach ($g in $guards) {
    if (-not (Test-Path -LiteralPath $g.path)) { continue }
    Write-Host "Running $($g.name)..."
    pwsh -NoProfile -File $g.path @strictArgs
    if ($LASTEXITCODE -ne 0) {
        Write-Error "$($g.name) failed. $($g.fix)"
        throw "$($g.name) failed."
    }
}

Write-Host "All guards passed."
