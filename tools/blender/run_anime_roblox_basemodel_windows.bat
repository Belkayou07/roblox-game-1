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
    echo Blender 4.2 or newer was not found.
    echo Install Blender, then run this file again.
    pause
    exit /b 1
)

echo Generating the modular anime Roblox basemodel...
"%BLENDER_EXE%" --background --python "tools\blender\create_anime_roblox_basemodel.py"
if errorlevel 1 (
    echo.
    echo Generation failed. Read the Blender error above.
    pause
    exit /b 1
)

echo.
echo Generated files are in:
echo   assets\generated\anime_roblox_basemodel\
echo.
echo Main files:
echo   anime_roblox_basemodel.blend
echo   anime_roblox_basemodel.fbx
echo.
echo Preview renders:
echo   anime_basemodel_front.png
echo   anime_basemodel_side.png
echo   anime_basemodel_back.png
echo   anime_basemodel_threequarter.png
echo   anime_basemodel_rig.png
echo.
pause
