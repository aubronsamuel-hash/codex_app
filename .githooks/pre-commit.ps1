# Requires -Version 7.0
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = git rev-parse --show-toplevel 2>$null
if (-not $repoRoot) { exit 0 }
$file = Join-Path $repoRoot "docs/codex/last_output.json"
if (-not (Test-Path $file)) {
  Write-Host "ERROR: docs/codex/last_output.json is missing."
  Write-Host "Hint: pwsh -File tools/codex/ensure_last_output.ps1 -Step \"NN\" -Title \"Your title\" -Summary \"Your summary\" -Status success"
  exit 1
}
try { $obj = Get-Content $file | ConvertFrom-Json } catch { Write-Host "ERROR: docs/codex/last_output.json is not valid JSON."; exit 1 }
$required = @("version","step","title","summary","status","timestamp")
$missing = @()
foreach ($k in $required) {
  if (-not $obj.PSObject.Properties.Name.Contains($k) -or [string]::IsNullOrWhiteSpace([string]$obj.$k)) { $missing += $k }
}
if ($missing.Count -gt 0) {
  Write-Host ("ERROR: last_output.json missing keys: " + ($missing -join ", "))
  Write-Host "Hint: pwsh -File tools/codex/ensure_last_output.ps1 -Step \"NN\" -Title \"Your title\" -Summary \"Your summary\""
  exit 1
}
exit 0
