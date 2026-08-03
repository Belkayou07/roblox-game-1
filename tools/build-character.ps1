$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$OutputDir = Join-Path $RepoRoot "TheShatteredVeil"
$ProgressDir = Join-Path $OutputDir "Progress"
$Generator = Join-Path $OutputDir "Phase4_Refined.py"

if (-not (Test-Path $Generator)) {
    throw "Missing refined generator: $Generator. Run git pull and try again."
}

New-Item -ItemType Directory -Force -Path $ProgressDir | Out-Null

$outputs = @(
    "Refined_Front.png",
    "Refined_Side.png",
    "Refined_Back.png",
    "Refined_ThreeQuarter.png",
    "Refined_Weapons.png",
    "Refined_Pass.blend",
    "Refined_Pass.glb",
    "Refined_Report.json"
)
foreach ($file in $outputs) {
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

Write-Host "Refined rebuild: torso, face, cloth and swords" -ForegroundColor Cyan
Write-Host "Using Blender:" $Blender -ForegroundColor Cyan
Write-Host "Generator:" $Generator -ForegroundColor Cyan
Write-Host "Output:" $ProgressDir -ForegroundColor Cyan

$env:SHATTERED_VEIL_OUTPUT = $OutputDir
& $Blender --background --factory-startup --python $Generator
$BlenderExitCode = $LASTEXITCODE

if ($BlenderExitCode -ne 0) {
    throw "Blender exited with code $BlenderExitCode."
}

foreach ($file in $outputs) {
    $path = Join-Path $ProgressDir $file
    if (-not (Test-Path $path)) {
        throw "Refined pass completed without required output: $path"
    }
}

Write-Host ""
Write-Host "Refined character pass generated successfully." -ForegroundColor Green
Write-Host (Join-Path $ProgressDir "Refined_Front.png")
Write-Host (Join-Path $ProgressDir "Refined_Side.png")
Write-Host (Join-Path $ProgressDir "Refined_Back.png")
Write-Host (Join-Path $ProgressDir "Refined_ThreeQuarter.png")
Write-Host (Join-Path $ProgressDir "Refined_Weapons.png")
