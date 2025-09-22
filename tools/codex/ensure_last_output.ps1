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

function Assert-NonEmpty {
    param(
        [string]$Name,
        [string]$Value
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        throw "Parameter '$Name' cannot be empty."
    }
}

Assert-NonEmpty -Name "Step" -Value $Step
Assert-NonEmpty -Name "Title" -Value $Title
Assert-NonEmpty -Name "Summary" -Value $Summary
Assert-NonEmpty -Name "Status" -Value $Status

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "../..")).Path
$docDir = Join-Path $repoRoot "docs/codex"
if (-not (Test-Path $docDir)) {
    New-Item -ItemType Directory -Force -Path $docDir | Out-Null
}

$timestamp = (Get-Date -AsUTC).ToString("yyyy-MM-ddTHH:mm:ssZ")

$payload = [ordered]@{
    version = "1"
    step = $Step
    title = $Title
    summary = $Summary
    status = $Status
    timestamp = $timestamp
}

if ($Outputs -and $Outputs.Count -gt 0) {
    $payload.outputs = $Outputs
}

$json = $payload | ConvertTo-Json -Depth 6
$asciiBuilder = New-Object System.Text.StringBuilder
foreach ($ch in $json.ToCharArray()) {
    $code = [int][char]$ch
    if ($code -ge 0 -and $code -le 127) {
        [void]$asciiBuilder.Append($ch)
    } else {
        [void]$asciiBuilder.Append("?")
    }
}

$outFile = Join-Path $docDir "last_output.json"
Set-Content -Encoding Ascii -Path $outFile -Value $asciiBuilder.ToString()

try {
    Get-Content -Path $outFile -Raw | ConvertFrom-Json | Out-Null
} catch {
    Write-Error "Invalid JSON written to $outFile"
    exit 1
}

Write-Host "last_output.json updated at $outFile"
