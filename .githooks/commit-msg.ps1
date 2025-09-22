param([Parameter(Mandatory=$true)][string]$MsgFile)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not (Test-Path $MsgFile)) { exit 0 }
$content = Get-Content -Raw -Path $MsgFile

# Si une ligne Ref existe deja, OK
if ($content -match "(?i)^Ref:\s*docs/roadmap/step-") { exit 0 }

# Essaye d'inferer le step depuis le nom de branche
$branch = (git rev-parse --abbrev-ref HEAD).Trim()
$step = $null
if ($branch -match "(?i)step[-_/]?([0-9]{1,2})") {
  $n = [int]$Matches[1]
  $step = $n.ToString("00")
}

if ($null -ne $step) {
  Add-Content -Encoding Ascii -Path $MsgFile -Value "`nRef: docs/roadmap/step-$step.md"
  exit 0
}

Write-Host "ERROR: Missing 'Ref: docs/roadmap/step-XX.md' in commit message."
Write-Host "Hint: add a line like: Ref: docs/roadmap/step-03.md"
exit 1
