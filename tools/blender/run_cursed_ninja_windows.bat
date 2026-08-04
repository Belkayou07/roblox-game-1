@echo off
setlocal
cd /d "%~dp0\..\.."

set "BLENDER_EXE="
where blender >nul 2>nul && set "BLENDER_EXE=blender"

if not defined BLENDER_EXE if exist "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" set "BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
if not defined BLENDER_EXE if exist "C:\Program Files\Blender Foundation\Blender 4.4\blender.exe" set "BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 4.4\blender.exe"
if not defined BLENDER_EXE if exist "C:\Program Files\Blender Foundation\Blender 4.3\blender.exe" set "BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 4.3\blender.exe"
if not defined BLENDER_EXE if exist "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe" set "BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"

if not defined BLENDER_EXE (
    echo Blender was not found. Install Blender 4.2 or newer, then retry.
    pause
    exit /b 1
)

echo Generating the Cursed Ninja character...
"%BLENDER_EXE%" --background --python "tools\blender\create_cursed_ninja.py"
if errorlevel 1 (
    echo Generation failed. Read the Blender error above.
    pause
    exit /b 1
)

echo.
echo Generated:
echo   assets\generated\cursed_ninja\cursed_ninja.blend
echo   assets\generated\cursed_ninja\cursed_ninja.fbx
echo.
echo Open the Blend file. Frame 36 contains the mobility test pose.
pause
