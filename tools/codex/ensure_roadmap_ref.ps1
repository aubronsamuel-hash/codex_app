param(
  [string]$StepRef,
  [switch]$Amend
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Resolve-StepRef {
  param([string]$InputRef)
  if ($InputRef) { return $InputRef }
  $docs = Get-ChildItem -Path "docs/roadmap" -Filter "step-*.md" -File | Sort-Object Name
  if (-not $docs) { throw "No roadmap step files under docs/roadmap" }
  $last = $docs[-1].Name
  return ("docs/roadmap/{0}" -f $last)
}

$refPath = Resolve-StepRef -InputRef $StepRef
$refLine = "Ref: $refPath"

# Try to update PR body (if gh is available and we are on a PR context)
$prNumber = $env:PR_NUMBER
if (-not $prNumber) {
  try {
    $prNumber = gh pr view --json number -q .number
  } catch {}
}

if ($prNumber) {
  try {
    $body = gh pr view $prNumber --json body -q .body
    if ($body -notmatch "(?m)^Ref:\s*") {
      $newBody = "$body`n`n$refLine"
      gh pr edit $prNumber --body "$newBody" | Out-Null
      Write-Host "Injected Ref into PR body: $refLine"
      exit 0
    }
  } catch {}
}

# Fallback: ensure last commit message contains the Ref line
$needCommit = $true
try {
  $lastMsg = git log -1 --pretty=%B
  if ($lastMsg -match "(?m)^Ref:\s*") { $needCommit = $false }
} catch {}

if ($needCommit) {
  $msg = "chore(ci): add roadmap reference`n`n$refLine"
  if ($Amend) {
    git commit --allow-empty --amend -m "$msg"
  } else {
    git commit --allow-empty -m "$msg"
  }
  Write-Host "Created commit with Ref line: $refLine"
}

# Push with SSH, then fallback to HTTPS if SSH fails
function Push-With-Fallback {
  param([string]$Branch)
  try {
    git push origin $Branch
    return
  } catch {
    Write-Warning "SSH push failed, switching to HTTPS"
    $origin = git remote get-url origin
    if ($origin -match "^git@github.com:(.*)$") {
      $repo = $Matches[1]
      git remote set-url origin https://github.com/$repo
      git push origin $Branch
      git remote set-url origin $origin
    } else {
      throw
    }
  }
}

$branch = git rev-parse --abbrev-ref HEAD
Push-With-Fallback -Branch $branch
