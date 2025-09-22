
Param()

function Write-ErrorLine {
    param([string]$Msg)
    Write-Host "ERROR: $Msg"
}

function Exit-Fail {
    param([string]$Msg)
    Write-ErrorLine $Msg
    exit 1
}
