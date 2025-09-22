
Param(
  [switch]$Strict
)
. "$PSScriptRoot/utils.ps1"

$jsonPath = "docs/codex/last_output.json"
if (-not (Test-Path $jsonPath)) {
  Exit-Fail "Missing docs/codex/last_output.json"
}

try {
  $o = Get-Content $jsonPath -Raw | ConvertFrom-Json
  if (-not $o.summary) { Exit-Fail "last_output.json missing 'summary'" }
} catch {
  Exit-Fail "Invalid JSON in last_output.json"
}

Write-Host "commit_guard: OK"
