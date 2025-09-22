Param()

$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "../..")
Set-Location $repoRoot

Write-Host "Running backend tests with coverage..."
& python -m pytest
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$coverageSummary = Join-Path $repoRoot "coverage_summary.txt"
if (Test-Path $coverageSummary) {
  Remove-Item $coverageSummary -Force
}

Write-Host "Generating coverage summary..."
& python -m coverage report | Tee-Object -FilePath $coverageSummary | Out-Null
if ($LASTEXITCODE -ne 0) {
  if (Test-Path $coverageSummary) {
    Remove-Item $coverageSummary -Force
  }
  exit $LASTEXITCODE
}

Write-Host "Running commit_guard.ps1..."
try {
  pwsh -File tools/guards/commit_guard.ps1
  if ($LASTEXITCODE -ne 0) { throw "commit_guard exit code $LASTEXITCODE" }
} catch {
  Write-Error "commit_guard failed."
  Write-Host "If the error mentions last_output.json or summary, run:"
  Write-Host "  pwsh -File tools/codex/ensure_last_output.ps1 -Step \"NN\" -Title \"Title\" -Summary \"Short summary\""
  if (Test-Path $coverageSummary) { Remove-Item $coverageSummary -Force }
  exit 1
}

$guards = @(
  "policy_guard.ps1",
  "roadmap_guard.ps1",
  "secret_scan.ps1",
  "readme_guard.ps1",
  "coverage_guard.ps1"
)

foreach ($guard in $guards) {
  $path = Join-Path $PSScriptRoot $guard
  Write-Host "Running $guard..."
  & $path
  if ($LASTEXITCODE -ne 0) {
    if (Test-Path $coverageSummary) { Remove-Item $coverageSummary -Force }
    exit $LASTEXITCODE
  }
}

if (Test-Path $coverageSummary) {
  Remove-Item $coverageSummary -Force
}

Write-Host "All guards completed successfully."
