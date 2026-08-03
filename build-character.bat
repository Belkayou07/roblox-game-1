@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\build-character.ps1"
set EXIT_CODE=%ERRORLEVEL%
echo.
if not "%EXIT_CODE%"=="0" (
  echo Build failed. Copy the error shown above and send it to ChatGPT.
) else (
  echo Build completed. Check TheShatteredVeil\PREVIEW_*.png and TheShatteredVeil\TheShatteredVeil.blend
)
pause
exit /b %EXIT_CODE%
