@echo off
setlocal

cd /d "%~dp0\..\.."

set "BLENDER_EXE="

where blender >nul 2>nul
if %errorlevel%==0 set "BLENDER_EXE=blender"

if not defined BLENDER_EXE if exist "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" set "BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
if not defined BLENDER_EXE if exist "C:\Program Files\Blender Foundation\Blender 4.4\blender.exe" set "BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 4.4\blender.exe"
if not defined BLENDER_EXE if exist "C:\Program Files\Blender Foundation\Blender 4.3\blender.exe" set "BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 4.3\blender.exe"
if not defined BLENDER_EXE if exist "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe" set "BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"

if not defined BLENDER_EXE (
    echo.
    echo Blender was not found.
    echo Install Blender 4.2 or newer, or add blender.exe to PATH.
    echo.
    pause
    exit /b 1
)

echo Generating classic blocky R15 avatar blueprint...
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
echo   assets\generated\blocky_r15_blueprint.blend
echo   assets\generated\blocky_r15_blueprint.fbx
echo.
echo Open the Blend file and move the timeline to frame 35 to inspect articulation.
echo.
pause
