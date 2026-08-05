@echo off
setlocal EnableExtensions

set "SCRIPT_DIR=%~dp0"
set "SCRIPT_PATH=%SCRIPT_DIR%create_anime_roblox_base_mannequin_v3.py"
set "BLENDER_EXE="

if not exist "%SCRIPT_PATH%" (
    echo [ERROR] The v3 Blender generator was not found:
    echo %SCRIPT_PATH%
    pause
    exit /b 1
)

for /f "delims=" %%I in ('where blender.exe 2^>nul') do (
    set "BLENDER_EXE=%%I"
    goto :blender_found
)

for /d %%D in ("C:\Program Files\Blender Foundation\Blender *") do (
    if exist "%%~fD\blender.exe" set "BLENDER_EXE=%%~fD\blender.exe"
)

:blender_found
if not defined BLENDER_EXE (
    echo [ERROR] Blender was not found.
    echo Install Blender 4.2 or newer, or add blender.exe to PATH.
    pause
    exit /b 1
)

echo Using Blender:
echo %BLENDER_EXE%
echo.
echo Generating the v3 blank anime Roblox base mannequin...
echo Existing generated outputs will be replaced.
echo This can take several minutes because Blender also renders preview images.
echo.

"%BLENDER_EXE%" --background --python "%SCRIPT_PATH%"
set "RESULT=%ERRORLEVEL%"

if not "%RESULT%"=="0" (
    echo.
    echo [ERROR] Blender returned exit code %RESULT%.
    echo Read the messages above and send the complete error output for debugging.
    pause
    exit /b %RESULT%
)

echo.
echo [DONE] The v3 mannequin was generated successfully.
echo Output folder:
echo %SCRIPT_DIR%..\..\assets\generated\anime_roblox_base_mannequin
pause
endlocal
