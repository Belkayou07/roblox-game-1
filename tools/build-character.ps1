$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$Generator = Join-Path $RepoRoot "TheShatteredVeil\BlenderGenerateAsset.py"
$OutputDir = Join-Path $RepoRoot "TheShatteredVeil"

if (-not (Test-Path $Generator)) {
    throw "Missing generator: $Generator. Run git pull and try again."
}

$candidates = @()
$command = Get-Command blender.exe -ErrorAction SilentlyContinue
if ($command) {
    $candidates += $command.Source
}

$installRoot = Join-Path $env:ProgramFiles "Blender Foundation"
if (Test-Path $installRoot) {
    $candidates += Get-ChildItem $installRoot -Filter blender.exe -File -Recurse -ErrorAction SilentlyContinue |
        Sort-Object FullName -Descending |
        ForEach-Object { $_.FullName }
}

$localInstallRoot = Join-Path $env:LOCALAPPDATA "Programs\Blender Foundation"
if (Test-Path $localInstallRoot) {
    $candidates += Get-ChildItem $localInstallRoot -Filter blender.exe -File -Recurse -ErrorAction SilentlyContinue |
        Sort-Object FullName -Descending |
        ForEach-Object { $_.FullName }
}

$Blender = $candidates | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
if (-not $Blender) {
    throw "Blender was not found. Confirm Blender is installed, then send me its installation path."
}

Write-Host "Using Blender:" $Blender -ForegroundColor Cyan
Write-Host "Generator:" $Generator -ForegroundColor Cyan
Write-Host "Output:" $OutputDir -ForegroundColor Cyan

$env:SHATTERED_VEIL_OUTPUT = $OutputDir
& $Blender --background --python $Generator
if ($LASTEXITCODE -ne 0) {
    throw "Blender exited with code $LASTEXITCODE."
}

$required = @(
    "TheShatteredVeil.blend",
    "TheShatteredVeil_Roblox.fbx",
    "PREVIEW_FRONT.png",
    "PREVIEW_BACK.png",
    "PREVIEW_THREE_QUARTER.png",
    "PREVIEW_WEAPONS.png",
    "BUILD_REPORT.json"
)

foreach ($file in $required) {
    $path = Join-Path $OutputDir $file
    if (-not (Test-Path $path)) {
        throw "Build completed without required output: $path"
    }
}

Write-Host "The Shattered Veil blockout generated successfully." -ForegroundColor Green
