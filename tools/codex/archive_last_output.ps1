# Requires -Version 7.0
param([string]$Step,[switch]$Force)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = git rev-parse --show-toplevel
Set-Location $repoRoot
$src = Join-Path $repoRoot "docs/codex/last_output.json"
if (-not (Test-Path $src)) { Write-Error "archive_last_output: missing $src"; exit 1 }
try { $obj = Get-Content $src | ConvertFrom-Json } catch { Write-Error "invalid JSON"; exit 1 }
$required = @("version","step","title","summary","status","timestamp")
foreach ($k in $required) { if (-not $obj.$k) { Write-Error "missing $k"; exit 1 } }
if ($Step) { $obj.step = "$Step" }

$commit = (git rev-parse --short=12 HEAD).Trim()
$archiveDir = Join-Path $repoRoot "docs/codex/archive"
if (-not (Test-Path $archiveDir)) { New-Item -ItemType Directory -Force -Path $archiveDir | Out-Null }

$iso = (Get-Date $obj.timestamp).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$dest = Join-Path $archiveDir ("step-" + $obj.step + "__" + $commit + "__" + $iso + ".json")
if ((Test-Path $dest) -and -not $Force) { Write-Host "archive already exists"; exit 0 }
Copy-Item $src $dest -Force

$index = Join-Path $archiveDir "index.csv"
if (-not (Test-Path $index)) { "commit,step,title,status,timestamp,filename" | Set-Content -Encoding Ascii -Path $index }
$line = ('{0},{1},"{2}",{3},{4},{5}' -f $commit,$obj.step,($obj.title -replace '"',''''),$obj.status,$iso,(Split-Path $dest -Leaf))
Add-Content -Encoding Ascii -Path $index -Value $line
Write-Host "archive_last_output: archived to $dest"
