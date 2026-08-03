@echo off
setlocal
cd /d "%~dp0"
echo Connected rebuild: The Shattered Veil
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\build-character.ps1"
set EXIT_CODE=%ERRORLEVEL%
echo.
if not "%EXIT_CODE%"=="0" (
  echo Connected build failed. Copy the full error above and send it to ChatGPT.
) else (
  echo Connected pass completed.
  echo Check TheShatteredVeil\Progress\Connected_*.png
)
pause
exit /b %EXIT_CODE%
