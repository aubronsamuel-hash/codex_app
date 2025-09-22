
Param(
  [string]$PolicyFile = "tools/guards/policy.toml"
)
. "$PSScriptRoot/utils.ps1"

if (-not (Test-Path $PolicyFile)) {
  Exit-Fail "policy file not found: $PolicyFile"
}

$content = Get-Content $PolicyFile -Raw
if ($content -match "AKIA[0-9A-Z]{16}") {
  Exit-Fail "example secret leaked in policy file"
}

Write-Host "policy_guard: OK"
