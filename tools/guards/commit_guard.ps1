Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Param(
  [switch]$Strict
)
. "$PSScriptRoot/utils.ps1"

$repoRoot = git rev-parse --show-toplevel 2>$null
if (-not $repoRoot) { $repoRoot = (Resolve-Path ".").Path }
$lastOut = Join-Path $repoRoot "docs/codex/last_output.json"
$hint = 'Hint: pwsh -File tools/codex/ensure_last_output.ps1 -Step "NN" -Title "Title" -Summary "Short summary"'

if (-not (Test-Path $lastOut)) {
  Write-Host $hint
  Exit-Fail "commit_guard: missing docs/codex/last_output.json"
}

try {
  $obj = Get-Content -Path $lastOut -Raw | ConvertFrom-Json
} catch {
  Write-Host $hint
  Exit-Fail "commit_guard: docs/codex/last_output.json is not valid JSON."
}

$required = @("version","step","title","summary","status","timestamp")
$missing = @()
foreach ($k in $required) {
  if (-not $obj.PSObject.Properties.Name.Contains($k) -or [string]::IsNullOrWhiteSpace([string]$obj.$k)) { $missing += $k }
}
if ($missing.Count -gt 0) {
  Write-Host $hint
  Exit-Fail ("commit_guard: last_output.json missing: " + ($missing -join ", "))
}

Write-Host "commit_guard: OK"
