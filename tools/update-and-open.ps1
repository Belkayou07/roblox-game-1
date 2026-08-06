$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

function Require-Command {
    param([Parameter(Mandatory = $true)][string]$Name)

    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' was not found. Make sure it is installed and available in this terminal."
    }
}

Require-Command -Name "git"
Require-Command -Name "rojo"

Write-Host ""
Write-Host "[1/3] Pulling the latest game update..." -ForegroundColor Cyan
& git pull --ff-only
if ($LASTEXITCODE -ne 0) {
    throw "Git pull failed. Resolve the Git message above, then run this updater again."
}

$buildDirectory = Join-Path $repoRoot "build"
$outputFile = Join-Path $buildDirectory "RobloxGame1-Latest.rbxlx"

New-Item -ItemType Directory -Path $buildDirectory -Force | Out-Null

Write-Host "[2/3] Building a fresh Roblox place..." -ForegroundColor Cyan
& rojo build default.project.json -o $outputFile
if ($LASTEXITCODE -ne 0) {
    throw "Rojo build failed. Review the error above."
}

Write-Host "[3/3] Opening the fresh build in Roblox Studio..." -ForegroundColor Cyan
Start-Process -FilePath $outputFile

Write-Host ""
Write-Host "Done. This Studio window contains the latest GitHub version." -ForegroundColor Green
Write-Host "Build: $outputFile"
