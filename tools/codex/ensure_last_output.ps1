# Requires -Version 7.0
param(
  [Parameter(Mandatory=$true)][string]$Step,
  [Parameter(Mandatory=$true)][string]$Title,
  [Parameter(Mandatory=$true)][string]$Summary,
  [string]$Status = "success",
  [string[]]$Outputs
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSCommandPath | Split-Path -Parent
$docDir = Join-Path $root "docs/codex"
if (-not (Test-Path $docDir)) { New-Item -ItemType Directory -Force -Path $docDir | Out-Null }

$payload = [ordered]@{
  version   = "1"
  step      = "$Step"
  title     = "$Title"
  summary   = "$Summary"
  status    = "$Status"
  timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
}
if ($Outputs -and $Outputs.Count -gt 0) { $payload.outputs = $Outputs }

$json = $payload | ConvertTo-Json -Depth 6
$ascii = ($json.ToCharArray() | ForEach-Object { if ([int][char]$_ -le 127) { $_ } else { "?" } }) -join ""
$outFile = Join-Path $docDir "last_output.json"
Set-Content -Encoding Ascii -Path $outFile -Value $ascii

try { Get-Content $outFile | ConvertFrom-Json | Out-Null } catch { Write-Error "Invalid JSON written to $outFile"; exit 1 }
Write-Host "Wrote ASCII last_output.json and validated OK: $outFile"
