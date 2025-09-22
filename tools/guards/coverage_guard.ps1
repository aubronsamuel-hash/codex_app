
Param(
  [double]$Global = 0.70
)
. "$PSScriptRoot/utils.ps1"

$covFile = "coverage_summary.txt"
if (-not (Test-Path $covFile)) {
  Exit-Fail "coverage_summary.txt not found. Provide a summary or parse tool output."
}
$txt = Get-Content $covFile -Raw
$lines = $txt -split "`n"
$totLine = $lines | Where-Object { $_.TrimStart().StartsWith("TOTAL") } | Select-Object -First 1
if (-not $totLine) {
  Exit-Fail "Could not find TOTAL line in coverage summary"
}
$tokens = $totLine.Trim() -split "\s+"
if ($tokens.Count -lt 1) {
  Exit-Fail "Coverage summary TOTAL line malformed"
}
$percentToken = $tokens[-1]
if ($percentToken -match "^(\d+(?:\.\d+)?)%$") {
  $pct = [double]$Matches[1]
} else {
  Exit-Fail "Could not parse coverage percentage"
}
if ($pct -lt ($Global*100)) {
  Exit-Fail "Coverage $pct% is below threshold $([int]($Global*100))%"
}

Write-Host "coverage_guard: OK"
