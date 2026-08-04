@echo off
setlocal

cd /d "%~dp0\..\.."

set "BLENDER_EXE="

where blender >nul 2>nul
if %errorlevel%==0 (
    set "BLENDER_EXE=blender"
)

if not defined BLENDER_EXE if exist "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" set "BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
if not defined BLENDER_EXE if exist "C:\Program Files\Blender Foundation\Blender 4.4\blender.exe" set "BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 4.4\blender.exe"
if not defined BLENDER_EXE if exist "C:\Program Files\Blender Foundation\Blender 4.3\blender.exe" set "BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 4.3\blender.exe"
if not defined BLENDER_EXE if exist "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe" set "BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"

if not defined BLENDER_EXE (
    echo.
    echo Blender was not found.
    echo Install Blender or add blender.exe to PATH, then run this file again.
    echo.
    pause
    exit /b 1
)

echo Generating Roblox avatar blueprint...
"%BLENDER_EXE%" --background --python "tools\blender\create_roblox_avatar_blueprint.py"

if errorlevel 1 (
    echo.
    echo Generation failed. Read the Blender error above.
    echo.
    pause
    exit /b 1
)

echo.
echo Generated files:
echo   assets\generated\roblox_avatar_blueprint.blend
echo   assets\generated\roblox_avatar_blueprint.fbx
echo.
pause
