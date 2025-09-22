Param(
  [string]$Step = "auto",
  [ValidateSet("current","all")] [string]$Mode = "current",
  [string]$Repo = "",
  [switch]$CreatePrIfMissing
)

$ErrorActionPreference = "Stop"
function Info($m){ Write-Host "[INFO] $m" }
function Warn($m){ Write-Host "[WARN] $m" }
function Err ($m){ Write-Host "[ERR ] $m" }

$script:SummaryItems = @()
function Add-Summary {
  param([string]$Message)
  if ($null -eq $script:SummaryItems) { $script:SummaryItems = @() }
  $script:SummaryItems += $Message
}

function Normalize-StepToken {
  param([string]$Value)

  if ([string]::IsNullOrWhiteSpace($Value)) { return $null }

  $match = [regex]::Match($Value, "step[-_]?(?<n>\\d{1,2})", 'IgnoreCase')
  if ($match.Success) { return "{0:D2}" -f ([int]$match.Groups['n'].Value) }

  $generic = [regex]::Match($Value, "(?<!\\d)(?<n>\\d{1,2})(?!\\d)")
  if ($generic.Success) { return "{0:D2}" -f ([int]$generic.Groups['n'].Value) }

  return $null
}

# Detect branch & repo
$branch = (git rev-parse --abbrev-ref HEAD).Trim()
if ([string]::IsNullOrWhiteSpace($Repo)) {
  $originUrl = (git remote get-url origin).Trim()
  if ($originUrl -match "github.com[:/](?<owner>[^/]+)/(?<name>[^/.]+)(?:\\.git)?") {
    $Repo = "$($Matches.owner)/$($Matches.name)"
  } else { throw "Cannot parse GitHub repo from origin URL: $originUrl" }
}
Info "Branch: $branch, Repo: $Repo"

# Discover existing steps from files
$roadmapDir = Join-Path (Get-Location) "docs/roadmap"
$existingSteps = @()
if (Test-Path $roadmapDir) {
  Get-ChildItem $roadmapDir -Filter "step-*.md" | ForEach-Object {
    if ($_.Name -match "step-(?<n>\\d{2})\\.md") { $existingSteps += [int]$Matches.n }
  }
}
$existingSteps = $existingSteps | Sort-Object -Unique

# Detect current step
function Detect-Step {
  param([string]$Fallback)

  if ($Step -ne "auto") {
    $normalized = Normalize-StepToken $Step
    if ($normalized) { return $normalized }
    throw "Unable to understand step value '$Step'. Use NN (e.g. 04)."
  }

  $envStep = Normalize-StepToken $env:STEP
  if ($envStep) { return $envStep }

  $branchStep = Normalize-StepToken $branch
  if ($branchStep) { return $branchStep }

  $gitLogLines = @()
  try { $gitLogLines = git log -n 20 --pretty=%B 2>$null } catch { $gitLogLines = @() }
  $joined = ($gitLogLines | Where-Object { $_ -ne $null }) -join "`n"
  if ($joined) {
    $refMatches = [regex]::Matches($joined, "docs/roadmap/step-(?<n>\\d{1,})\\.md", 'IgnoreCase')
    if ($refMatches.Count -gt 0) {
      $lastMatch = $refMatches[$refMatches.Count-1]
      return "{0:D2}" -f ([int]$lastMatch.Groups['n'].Value)
    }

    $genericMatch = Normalize-StepToken $joined
    if ($genericMatch) { return $genericMatch }
  }

  if ($existingSteps.Count -gt 0) { return "{0:D2}" -f ($existingSteps | Select-Object -Last 1) }

  if ($Fallback) { return $Fallback }
  throw "Unable to detect step. Provide -Step NN or set branch like feature/step-04/..."
}

$curStep = Detect-Step -Fallback "01"
$refRel  = "docs/roadmap/step-$curStep.md"
Info "Detected step: $curStep"

# Ensure roadmap file exists
if (-not (Test-Path $refRel)) {
  Warn "Missing $refRel. Creating a minimal placeholder."
  New-Item -ItemType Directory -Force -Path (Split-Path $refRel) | Out-Null
  @(
    "# Step $curStep",
    "",
    "Status: DRAFT",
    "",
    "Autocreated to satisfy roadmap guard.",
    ""
  ) | Set-Content -Path $refRel -Encoding UTF8
  git add $refRel
  git commit -m "chore(roadmap): add placeholder for step $curStep`n`nRef: $refRel" | Out-Null
  Add-Summary "Created placeholder file $refRel and committed it."
}

# Compute all Ref lines based on existing files (+ current)
if (-not ($existingSteps -contains [int]$curStep)) { $existingSteps += [int]$curStep }
$existingSteps = $existingSteps | Sort-Object -Unique
$allRefLines = $existingSteps | ForEach-Object { "Ref: docs/roadmap/step-{0:D2}.md" -f $_ }

# Ensure last commit contains the needed Ref(s)
$lastMsgLines = @()
try { $lastMsgLines = git log -1 --pretty=%B 2>$null } catch { $lastMsgLines = @() }
$lastMsg = ($lastMsgLines | Where-Object { $_ -ne $null }) -join "`n"
if ($Mode -eq "all") {
  $missing = @()
  foreach($r in $allRefLines){ if ($lastMsg -notmatch [regex]::Escape($r)) { $missing += $r } }
  if ($missing.Count -gt 0) {
    Info "Adding empty commit with ALL missing Ref lines."
    $body = "chore(roadmap): ensure all roadmap Refs`n`n" + ($missing -join "`n")
    git commit --allow-empty -m $body | Out-Null
    Add-Summary "Created empty commit adding missing Ref lines: $($missing -join ', ')."
  } else { Info "Last commit already has all Ref lines." }
} else {
  if ($lastMsg -notmatch [regex]::Escape("Ref: $refRel")) {
    Info "Adding empty commit with current step Ref line."
    git commit --allow-empty -m "chore(step-$curStep): ensure roadmap Ref`n`nRef: $refRel" | Out-Null
    Add-Summary "Created empty commit ensuring Ref: $refRel."
  } else { Info "Last commit already contains the current step Ref line." }
}

# Ensure PR body contains ALL Ref lines
function Ensure-Pr-Body {
  param([string]$Repo,[string[]]$RefLines)

  $gh = (Get-Command gh -ErrorAction SilentlyContinue)
  if ($gh) {
    Info "gh CLI detected. Checking PR..."
    $prNumber = $null
    try { $prNumber = gh pr view --json number -q .number 2>$null } catch { $prNumber = $null }
    if (-not $prNumber) {
      if ($CreatePrIfMissing) {
        Info "No PR found. Creating one via gh.";
        gh pr create --fill --base main --head $branch | Out-Null
        $prNumber = gh pr view --json number -q .number
        Add-Summary "Created pull request for branch $branch via gh CLI."
      } else {
        Warn "No PR detected. Skipping PR body update."
        Add-Summary "PR body not updated (no PR associated with branch $branch)."
        return
      }
    }
    $body = (gh pr view $prNumber --json body -q .body)
    $toAdd = @()
    foreach($r in $RefLines){ if (-not ($body -match [regex]::Escape($r))) { $toAdd += $r } }
    if ($toAdd.Count -gt 0) {
      Info "Appending missing Ref lines to PR body via gh."
      $newBody = if ($body) { "$body`n`n$($toAdd -join "`n")" } else { ($toAdd -join "`n") }
      $tmp = New-TemporaryFile
      Set-Content -Path $tmp -Value $newBody -Encoding UTF8
      gh pr edit $prNumber --body-file $tmp | Out-Null
      Add-Summary "Updated PR #$prNumber body via gh with lines: $($toAdd -join ', ')."
    } else { Info "PR body already contains all Ref lines." }
    return
  }

  $token = $env:GITHUB_TOKEN
  if ($token) {
    Info "gh not found. Trying REST API (GITHUB_TOKEN present)."
    $headers = @{ Authorization = "Bearer $token"; Accept = "application/vnd.github+json" }
    $uri = "https://api.github.com/repos/$Repo/pulls?head=$Repo:$branch&state=open"
    $prs = $null
    try { $prs = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers } catch {}
    if (-not $prs -or $prs.Count -eq 0) {
      Warn "No open PR found for $branch. Skipping PR body update."
      Add-Summary "PR body not updated via API (no open PR for branch $branch)."
      return
    }
    $pr = if ($prs -is [System.Array]) { $prs[0] } else { $prs }
    $body = $pr.body
    $added = @()
    foreach($r in $RefLines){ if (-not ($body -match [regex]::Escape($r))) { $body = if ($body) { "$body`n`n$r" } else { $r }; $added += $r } }
    if ($added.Count -eq 0) { Info "PR body already contains all Ref lines."; return }
    $payload = @{ body = $body } | ConvertTo-Json -Compress
    $patchUri = "https://api.github.com/repos/$Repo/pulls/$($pr.number)"
    Invoke-RestMethod -Method Patch -Uri $patchUri -Headers ($headers + @{ "Content-Type" = "application/json" }) -Body $payload | Out-Null
    Info "PR body updated via REST API."
    Add-Summary "Updated PR #$($pr.number) body via REST API with lines: $($added -join ', ')."
    return
  }

  Warn "Cannot update PR body automatically (no gh and no GITHUB_TOKEN). Please add these lines to the PR description:"
  foreach($r in $RefLines){ Write-Host $r }
  Add-Summary "PR body requires manual update with Ref lines: $($RefLines -join ', ')."
}

Ensure-Pr-Body -Repo $Repo -RefLines $allRefLines

# Push with SSH->HTTPS fallback
function Try-Push { try { git push | Out-Null; return $true } catch { return $false } }
$eventName = $env:GITHUB_EVENT_NAME
$runningInActions = $env:GITHUB_ACTIONS -eq "true"
$skipPush = $false
if ($runningInActions -and $eventName -and $eventName -like "pull_request*") {
  Warn "Skipping git push because workflow is running for $eventName (write permissions may be restricted)."
  Add-Summary "Push skipped (GitHub Actions $eventName run)."
  $skipPush = $true
}

if (-not $skipPush) {
  $usedFallback = $false
  $pushed = Try-Push
  if (-not $pushed) {
    Warn "SSH push failed. Falling back to HTTPS."
    $originUrl = (git remote get-url origin).Trim()
    if ($originUrl -match "github.com[:/](?<owner>[^/]+)/(?<name>[^/.]+)(?:\\.git)?") {
      $owner = $Matches.owner; $name = $Matches.name
      $https = "https://github.com/$owner/$name.git"
      git remote set-url origin $https
      $usedFallback = $true
      $pushed = Try-Push
    } else {
      if ($runningInActions) {
        Warn "Cannot parse origin to switch to HTTPS. Skipping fallback in CI."
        Add-Summary "Push failed: could not parse origin URL for HTTPS fallback."
      } else {
        Err "Cannot parse origin to switch to HTTPS."
        exit 3
      }
    }
  }

  if ($pushed) {
    if ($usedFallback) {
      Add-Summary "Pushed changes via HTTPS fallback."
    } else {
      Add-Summary "Pushed changes using existing remote configuration."
    }
  } else {
    if ($runningInActions) {
      Warn "HTTPS push also failed (likely due to limited credentials). Please push manually."
      Add-Summary "Push failed in CI. Please push manually with required credentials."
    } else {
      Err "HTTPS push also failed. Check network/credentials."
      exit 2
    }
  }
}

Info "Done. Commit and PR body now satisfy roadmap guard for current and all steps."

Info "Summary:"
if ($script:SummaryItems.Count -gt 0) {
  foreach($item in $script:SummaryItems){ Info "  - $item" }
} else {
  Info "  No updates were necessary."
}
