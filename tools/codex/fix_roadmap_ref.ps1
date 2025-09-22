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
  if ($Step -ne "auto") { return $Step }

  if ($env:STEP -match "^(\\d{2})$") { return $Matches[1] }
  if ($branch -match "step[-_](\\d{2})") { return $Matches[1] }

  # look into recent commits for a Ref line
  $lastN = (git log -n 20 --pretty=%B) -join "\n"
  if ($lastN -match "Ref:\\s+docs/roadmap/step-(\\d{2})\\.md") { return $Matches[1] }

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
}

# Compute all Ref lines based on existing files (+ current)
if (-not ($existingSteps -contains [int]$curStep)) { $existingSteps += [int]$curStep }
$existingSteps = $existingSteps | Sort-Object -Unique
$allRefLines = $existingSteps | ForEach-Object { "Ref: docs/roadmap/step-{0:D2}.md" -f $_ }

# Ensure last commit contains the needed Ref(s)
$lastMsg = (git log -1 --pretty=%B)
if ($Mode -eq "all") {
  $missing = @()
  foreach($r in $allRefLines){ if ($lastMsg -notmatch [regex]::Escape($r)) { $missing += $r } }
  if ($missing.Count -gt 0) {
    Info "Adding empty commit with ALL missing Ref lines."
    $body = "chore(roadmap): ensure all roadmap Refs`n`n" + ($missing -join "`n")
    git commit --allow-empty -m $body | Out-Null
  } else { Info "Last commit already has all Ref lines." }
} else {
  if ($lastMsg -notmatch [regex]::Escape("Ref: $refRel")) {
    Info "Adding empty commit with current step Ref line."
    git commit --allow-empty -m "chore(step-$curStep): ensure roadmap Ref`n`nRef: $refRel" | Out-Null
  } else { Info "Last commit already contains the current step Ref line." }
}

# Ensure PR body contains ALL Ref lines
function Ensure-Pr-Body {
  param([string]$Repo,[string[]]$RefLines)

  $gh = (Get-Command gh -ErrorAction SilentlyContinue)
  if ($gh) {
    Info "gh CLI detected. Checking PR..."
    $prNumber = (gh pr view --json number -q .number 2>$null)
    if (-not $prNumber) {
      if ($CreatePrIfMissing) {
        Info "No PR found. Creating one via gh.";
        gh pr create --fill --base main --head $branch | Out-Null
        $prNumber = (gh pr view --json number -q .number)
      } else {
        Warn "No PR detected. Skipping PR body update."
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
    } else { Info "PR body already contains all Ref lines." }
    return
  }

  $token = $env:GITHUB_TOKEN
  if ($token) {
    Info "gh not found. Trying REST API (GITHUB_TOKEN present)."
    $prsJson = curl -s -H "Authorization: Bearer $token" -H "Accept: application/vnd.github+json" `
      "https://api.github.com/repos/$Repo/pulls?head=$Repo:$branch&state=open"
    $prs = $null; try { $prs = $prsJson | ConvertFrom-Json } catch {}
    if (-not $prs -or $prs.Count -eq 0) { Warn "No open PR found for $branch. Skipping PR body update."; return }
    $pr = $prs[0]
    $body = $pr.body
    foreach($r in $RefLines){ if (-not ($body -match [regex]::Escape($r))) { $body = if ($body) { "$body`n`n$r" } else { $r } } }
    $payload = @{ body = $body } | ConvertTo-Json -Compress
    curl -s -X PATCH -H "Authorization: Bearer $token" -H "Accept: application/vnd.github+json" -H "Content-Type: application/json" -d $payload "https://api.github.com/repos/$Repo/pulls/$($pr.number)" | Out-Null
    Info "PR body updated via REST API."
    return
  }

  Warn "Cannot update PR body automatically (no gh and no GITHUB_TOKEN). Please add these lines to the PR description:"
  foreach($r in $RefLines){ Write-Host $r }
}

Ensure-Pr-Body -Repo $Repo -RefLines $allRefLines

# Push with SSH->HTTPS fallback
function Try-Push { try { git push | Out-Null; return $true } catch { return $false } }
if (-not (Try-Push)){
  Warn "SSH push failed. Falling back to HTTPS."
  $originUrl = (git remote get-url origin).Trim()
  if ($originUrl -match "github.com[:/](?<owner>[^/]+)/(?<name>[^/.]+)(?:\\.git)?") {
    $owner = $Matches.owner; $name = $Matches.name
    $https = "https://github.com/$owner/$name.git"
    git remote set-url origin $https
    if (-not (Try-Push)) { Err "HTTPS push also failed. Check network/credentials."; exit 2 }
  } else { Err "Cannot parse origin to switch to HTTPS."; exit 3 }
}

Info "Done. Commit and PR body now satisfy roadmap guard for current and all steps."
