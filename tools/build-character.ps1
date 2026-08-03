$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$OutputDir = Join-Path $RepoRoot "TheShatteredVeil"
$ProgressDir = Join-Path $OutputDir "Progress"
$Generator = Join-Path $OutputDir "Phase1_Body.py"
$RuntimeGenerator = Join-Path $ProgressDir "Phase1_Body_Runtime.py"

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
    "Phase1_Report.json",
    "Phase1_Body_Runtime.py"
)
foreach ($file in $phase1Outputs) {
    $path = Join-Path $ProgressDir $file
    if (Test-Path $path) {
        Remove-Item $path -Force
    }
}

# Blender 4.5 removed the old BLENDER_EEVEE identifier. Create a temporary
# runtime copy with a version-safe engine selection while preserving the
# readable source file in the repository.
$source = Get-Content $Generator -Raw
$oldEngineLine = '    scene.render.engine = "BLENDER_EEVEE_NEXT" if hasattr(bpy.types, "EEVEE_NEXT") else "BLENDER_EEVEE"'
$newEngineBlock = @'
    for engine_name in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "BLENDER_WORKBENCH"):
        try:
            scene.render.engine = engine_name
            break
        except TypeError:
            continue
    else:
        raise RuntimeError("No supported Blender render engine is available.")
'@

if (-not $source.Contains($oldEngineLine)) {
    throw "The expected renderer configuration was not found in Phase1_Body.py."
}
$source = $source.Replace($oldEngineLine, $newEngineBlock.TrimEnd())
Set-Content -Path $RuntimeGenerator -Value $source -Encoding UTF8

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
Write-Host "Generator:" $RuntimeGenerator -ForegroundColor Cyan
Write-Host "Output:" $ProgressDir -ForegroundColor Cyan

$env:SHATTERED_VEIL_OUTPUT = $OutputDir
& $Blender --background --factory-startup --python $RuntimeGenerator
$BlenderExitCode = $LASTEXITCODE

if (Test-Path $RuntimeGenerator) {
    Remove-Item $RuntimeGenerator -Force
}

if ($BlenderExitCode -ne 0) {
    throw "Blender exited with code $BlenderExitCode."
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
