# ASCII-only. PowerShell 7+
# Purpose: validate PR body "Ref: docs/roadmap/step-XX.md" and last_output.json when --strict.
# Usage:
#   pwsh -File tools/guards/commit_guard.ps1
#   pwsh -File tools/guards/commit_guard.ps1 --strict
# CI passes PR body via env: PR_BODY

param(
    [switch]$Strict,
    [string]$PrBody,
    [string]$LastOutputPath = "docs/codex/last_output.json"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version 3

function Fail([string]$Message) {
    Write-Error $Message
    exit 1
}

# Source PR body from param or env
if (-not $PrBody -and $env:PR_BODY) { $PrBody = $env:PR_BODY }

Write-Host "commit_guard: strict=$($Strict.IsPresent), last_output='$LastOutputPath'"

# 1) Roadmap reference check (strict only)
$refPattern = 'Ref:\s*docs/roadmap/step-\d+\.md'
if ($Strict) {
    if (-not $PrBody) {
        Fail "Missing PR body content. Provide --PrBody or set env:PR_BODY."
    }
    if ($PrBody -notmatch $refPattern) {
        Fail "Missing 'Ref: docs/roadmap/step-XX.md' in PR or last commit."
    }
} else {
    if ($PrBody -and ($PrBody -notmatch $refPattern)) {
        Write-Warning "PR body has no 'Ref: docs/roadmap/step-XX.md' (non-strict)."
    }
}

# 2) Validate docs/codex/last_output.json
if (Test-Path -LiteralPath $LastOutputPath) {
    try {
        $null = Get-Content -LiteralPath $LastOutputPath -Raw | ConvertFrom-Json
        Write-Host "last_output.json is valid JSON."
    } catch {
        Fail ("Invalid JSON at {0}: {1}" -f $LastOutputPath, $_.Exception.Message)
    }
} elseif ($Strict) {
    Fail ("Missing required file: {0}" -f $LastOutputPath)
} else {
    Write-Host ("Optional file not found (non-strict): {0}" -f $LastOutputPath)
}

Write-Host "commit_guard OK"
