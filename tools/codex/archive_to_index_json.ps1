# Requires -Version 7.0
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = git rev-parse --show-toplevel 2>$null
if (-not $repoRoot) { $repoRoot = (Resolve-Path ".").Path }
$archiveDir = Join-Path $repoRoot "docs/codex/archive"
$csvPath = Join-Path $archiveDir "index.csv"
$jsonPath = Join-Path $archiveDir "index.json"
if (-not (Test-Path $csvPath)) { Write-Error "missing index.csv"; exit 1 }
$rows = Import-Csv -Path $csvPath
$normalized = $rows | ForEach-Object {
  [ordered]@{ commit=$_.commit; step=$_.step; title=$_.title; status=$_.status; timestamp=$_.timestamp; filename=$_.filename; path="docs/codex/archive/"+$_.filename }
} | Sort-Object -Property timestamp -Descending
$json = $normalized | ConvertTo-Json -Depth 6
$ascii = ($json.ToCharArray() | ForEach-Object { if ([int][char]$_ -le 127) { $_ } else { "?" } }) -join ""
Set-Content -Encoding Ascii -Path $jsonPath -Value $ascii
Write-Host "archive_to_index_json: wrote index.json with $($normalized.Count) entries"
