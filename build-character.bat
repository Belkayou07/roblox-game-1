@echo off
setlocal
cd /d "%~dp0"
echo Refined rebuild: The Shattered Veil
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\build-character.ps1"
set EXIT_CODE=%ERRORLEVEL%
echo.
if not "%EXIT_CODE%"=="0" (
  echo Refined build failed. Copy the full error above and send it to ChatGPT.
) else (
  echo Refined pass completed.
  echo Check TheShatteredVeil\Progress\Refined_*.png
)
pause
exit /b %EXIT_CODE%
