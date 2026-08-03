@echo off
setlocal
cd /d "%~dp0"
echo Silhouette rebuild: The Shattered Veil
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\build-character.ps1"
set EXIT_CODE=%ERRORLEVEL%
echo.
if not "%EXIT_CODE%"=="0" (
  echo Silhouette build failed. Copy the full error above and send it to ChatGPT.
) else (
  echo Silhouette build completed. Check TheShatteredVeil\Progress\Silhouette_*.png
)
pause
exit /b %EXIT_CODE%
