$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$OutputDir = Join-Path $RepoRoot "TheShatteredVeil"
$Generator = Join-Path $OutputDir "BlenderGenerateAsset.py"
$GeneratorParts = Join-Path $PSScriptRoot "generator"
$Runner = Join-Path $PSScriptRoot "run_blender_build.py"

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

# Restore the readable Blender Python generator from the compressed repository source.
# This avoids requiring the user to copy a large script manually.
$parts = Get-ChildItem $GeneratorParts -Filter "BlenderGenerateAsset.py.gz.b64.part*" -File |
    Sort-Object Name
if (-not $parts) {
    throw "Generator source parts were not found in $GeneratorParts. Run git pull and try again."
}

$base64 = ($parts | ForEach-Object { Get-Content $_.FullName -Raw }) -join ""
$compressedBytes = [Convert]::FromBase64String($base64)
$inputStream = [System.IO.MemoryStream]::new($compressedBytes)
$gzipStream = [System.IO.Compression.GZipStream]::new(
    $inputStream,
    [System.IO.Compression.CompressionMode]::Decompress
)
$outputStream = [System.IO.File]::Create($Generator)
try {
    $gzipStream.CopyTo($outputStream)
}
finally {
    $outputStream.Dispose()
    $gzipStream.Dispose()
    $inputStream.Dispose()
}

if (-not (Test-Path $Runner)) {
    throw "Missing Blender build runner: $Runner. Run git pull and try again."
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
Write-Host "Runner:" $Runner -ForegroundColor Cyan
Write-Host "Output:" $OutputDir -ForegroundColor Cyan

$env:SHATTERED_VEIL_OUTPUT = $OutputDir
& $Blender --background --factory-startup --python $Runner
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

Write-Host "The Shattered Veil Blender blockout generated successfully." -ForegroundColor Green
