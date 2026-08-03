$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$OutputDir = Join-Path $RepoRoot "TheShatteredVeil"
$ProgressDir = Join-Path $OutputDir "Progress"
$Generator = Join-Path $OutputDir "Phase2_Silhouette.py"

if (-not (Test-Path $Generator)) {
    throw "Missing silhouette generator: $Generator"
}

New-Item -ItemType Directory -Force -Path $ProgressDir | Out-Null

$phaseOutputs = @(
    "Silhouette_Front.png",
    "Silhouette_Side.png",
    "Silhouette_Back.png",
    "Silhouette_ThreeQuarter.png",
    "Silhouette_Weapons.png",
    "Silhouette_Pass.blend",
    "Silhouette_Pass.glb",
    "Silhouette_Report.json"
)
foreach ($file in $phaseOutputs) {
    $path = Join-Path $ProgressDir $file
    if (Test-Path $path) {
        Remove-Item $path -Force
    }
}

$candidates = @()
$command = Get-Command blender.exe -ErrorAction SilentlyContinue
if ($command) {
    $candidates += $command.Source
}

$installRoots = @(
    (Join-Path $env:ProgramFiles "Blender Foundation"),
    (Join-Path $env:LOCALAPPDATA "Programs\Blender Foundation")
)
foreach ($installRoot in $installRoots) {
    if (Test-Path $installRoot) {
        $candidates += Get-ChildItem $installRoot -Filter blender.exe -File -Recurse -ErrorAction SilentlyContinue |
            Sort-Object FullName -Descending |
            ForEach-Object { $_.FullName }
    }
}

$Blender = $candidates | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
if (-not $Blender) {
    throw "Blender was not found. Send me the full path to blender.exe."
}

Write-Host "Silhouette rebuild: head concealment, hair, clothing, swords" -ForegroundColor Cyan
Write-Host "Using Blender:" $Blender -ForegroundColor Cyan
Write-Host "Generator:" $Generator -ForegroundColor Cyan
Write-Host "Output:" $ProgressDir -ForegroundColor Cyan

$env:SHATTERED_VEIL_OUTPUT = $OutputDir
& $Blender --background --factory-startup --python $Generator
if ($LASTEXITCODE -ne 0) {
    throw "Blender exited with code $LASTEXITCODE."
}

$required = @(
    "Silhouette_Front.png",
    "Silhouette_Side.png",
    "Silhouette_Back.png",
    "Silhouette_ThreeQuarter.png",
    "Silhouette_Weapons.png",
    "Silhouette_Pass.blend",
    "Silhouette_Pass.glb",
    "Silhouette_Report.json"
)
foreach ($file in $required) {
    $path = Join-Path $ProgressDir $file
    if (-not (Test-Path $path)) {
        throw "Silhouette pass completed without required output: $path"
    }
}

Write-Host ""
Write-Host "Silhouette pass generated successfully." -ForegroundColor Green
Write-Host (Join-Path $ProgressDir "Silhouette_Front.png")
Write-Host (Join-Path $ProgressDir "Silhouette_Side.png")
Write-Host (Join-Path $ProgressDir "Silhouette_Back.png")
Write-Host (Join-Path $ProgressDir "Silhouette_ThreeQuarter.png")
Write-Host (Join-Path $ProgressDir "Silhouette_Weapons.png")
