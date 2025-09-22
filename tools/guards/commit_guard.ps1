Param(
  [switch]$Strict
)
. "$PSScriptRoot/utils.ps1"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
$lastOutputPath = Join-Path $repoRoot "docs/codex/last_output.json"
$hint = 'Hint: pwsh -File tools/codex/ensure_last_output.ps1 -Step "NN" -Title "Title" -Summary "Short summary"'

if (-not (Test-Path $lastOutputPath)) {
  Write-Host $hint
  Exit-Fail "commit_guard: missing docs/codex/last_output.json"
}

try {
  $json = Get-Content -Path $lastOutputPath -Raw | ConvertFrom-Json
} catch {
  Write-Host $hint
  Exit-Fail "commit_guard: invalid JSON in docs/codex/last_output.json"
}

$required = @("version", "step", "title", "summary", "status", "timestamp")
$missing = @()
foreach ($name in $required) {
  $hasProperty = $json.PSObject.Properties.Name -contains $name
  $value = $json.$name
  if (-not $hasProperty -or [string]::IsNullOrWhiteSpace([string]$value)) {
    $missing += $name
  }
}

if ($missing.Count -gt 0) {
  Write-Host $hint
  Exit-Fail ("commit_guard: docs/codex/last_output.json missing: " + ($missing -join ", "))
}

Write-Host "commit_guard: OK"
