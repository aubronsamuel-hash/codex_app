
Param(
  [double]$Global = 0.70
)
. "$PSScriptRoot/utils.ps1"

$covFile = "coverage_summary.txt"
if (-not (Test-Path $covFile)) {
  Exit-Fail "coverage_summary.txt not found. Provide a summary or parse tool output."
}
$txt = Get-Content $covFile -Raw
if ($txt -match "TOTAL\s+(\d+)%") {
  $pct = [int]$Matches[1]
  if ($pct -lt ($Global*100)) {
    Exit-Fail "Coverage $pct% is below threshold $([int]($Global*100))%"
  }
} else {
  Exit-Fail "Could not parse coverage percentage"
}

Write-Host "coverage_guard: OK"
