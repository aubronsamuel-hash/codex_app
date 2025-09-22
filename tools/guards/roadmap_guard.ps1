
Param(
  [switch]$Strict
)
. "$PSScriptRoot/utils.ps1"

$refFound = $false
$lastCommit = git log -1 --pretty=%B 2>$null
if ($lastCommit -match "Ref:\s*docs/roadmap/step-\d{2}\.md") {
  $refFound = $true
} else {
  # Try PR body if available (CI context may inject)
  $prBody = $env:PR_BODY
  if ($prBody -and ($prBody -match "Ref:\s*docs/roadmap/step-\d{2}\.md")) {
    $refFound = $true
  }
}

if (-not $refFound) {
  Exit-Fail "Missing 'Ref: docs/roadmap/step-XX.md' in PR or last commit."
}

Write-Host "roadmap_guard: OK"
