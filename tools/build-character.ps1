$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$OutputDir = Join-Path $RepoRoot "TheShatteredVeil"
$ProgressDir = Join-Path $OutputDir "Progress"
$Generator = Join-Path $OutputDir "Phase1_Body.py"

if (-not (Test-Path $Generator)) {
    throw "Missing Phase 1 generator: $Generator. Run git pull and try again."
}

New-Item -ItemType Directory -Force -Path $ProgressDir | Out-Null

# Remove outputs from the abandoned full-character generator so the rebuild
# cannot be confused with the previous failed model.
$legacyOutputs = @(
    "TheShatteredVeil.blend",
    "TheShatteredVeil_Roblox.fbx",
    "TheShatteredVeil_Roblox.glb",
    "PREVIEW_FRONT.png",
    "PREVIEW_BACK.png",
    "PREVIEW_THREE_QUARTER.png",
    "PREVIEW_WEAPONS.png",
    "BUILD_REPORT.json",
    "BlenderGenerateAsset.py"
)
foreach ($file in $legacyOutputs) {
    $path = Join-Path $OutputDir $file
    if (Test-Path $path) {
        Remove-Item $path -Force
    }
}

# Clear only generated Phase 1 outputs. The source script remains untouched.
$phase1Outputs = @(
    "Phase1_Body_Front.png",
    "Phase1_Body_Side.png",
    "Phase1_Body.blend",
    "Phase1_Body.glb",
    "Phase1_Report.json"
)
foreach ($file in $phase1Outputs) {
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

Write-Host "Fresh rebuild: Phase 1 - body proportions and anatomy" -ForegroundColor Cyan
Write-Host "Using Blender:" $Blender -ForegroundColor Cyan
Write-Host "Generator:" $Generator -ForegroundColor Cyan
Write-Host "Output:" $ProgressDir -ForegroundColor Cyan

$env:SHATTERED_VEIL_OUTPUT = $OutputDir
& $Blender --background --factory-startup --python $Generator
if ($LASTEXITCODE -ne 0) {
    throw "Blender exited with code $LASTEXITCODE."
}

$required = @(
    "Phase1_Body_Front.png",
    "Phase1_Body_Side.png",
    "Phase1_Body.blend",
    "Phase1_Body.glb",
    "Phase1_Report.json"
)
foreach ($file in $required) {
    $path = Join-Path $ProgressDir $file
    if (-not (Test-Path $path)) {
        throw "Phase 1 completed without required output: $path"
    }
}

Write-Host ""
Write-Host "Phase 1 generated successfully." -ForegroundColor Green
Write-Host "Review these two images before any other modeling continues:" -ForegroundColor Green
Write-Host (Join-Path $ProgressDir "Phase1_Body_Front.png")
Write-Host (Join-Path $ProgressDir "Phase1_Body_Side.png")
