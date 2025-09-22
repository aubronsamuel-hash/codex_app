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

$guards = @(
  "policy_guard.ps1",
  "roadmap_guard.ps1",
  "commit_guard.ps1",
  "secret_scan.ps1",
  "readme_guard.ps1",
  "coverage_guard.ps1"
)

$guardExit = 0
foreach ($guard in $guards) {
  $path = Join-Path $PSScriptRoot $guard
  Write-Host "Running $guard..."
  & $path
  if ($LASTEXITCODE -ne 0) {
    $guardExit = $LASTEXITCODE
    break
  }
}

if (Test-Path $coverageSummary) {
  Remove-Item $coverageSummary -Force
}

if ($guardExit -ne 0) { exit $guardExit }

Write-Host "All guards completed successfully."
