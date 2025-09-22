
Param()
. "$PSScriptRoot/utils.ps1"

$patterns = @(
  "AKIA[0-9A-Z]{16}",
  "(?i)api[_-]?key\s*=",
  "(?i)secret\s*=",
  "-----BEGIN (?:RSA|EC) PRIVATE KEY-----"
)

$diff = git diff --cached --unified=0 2>$null
foreach ($p in $patterns) {
  if ($diff -match $p) {
    Exit-Fail "secret-like pattern found in staged diff"
  }
}

Write-Host "secret_scan: OK"
