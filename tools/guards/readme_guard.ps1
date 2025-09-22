
Param()
. "$PSScriptRoot/utils.ps1"

if (-not (Test-Path "README.md")) {
  Exit-Fail "Missing README.md at repo root"
}
Write-Host "readme_guard: OK"
