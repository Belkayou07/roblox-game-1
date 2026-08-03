@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\build-character.ps1"
set EXIT_CODE=%ERRORLEVEL%
echo.
if not "%EXIT_CODE%"=="0" (
  echo Phase 1 build failed. Copy the complete error above and send it to ChatGPT.
) else (
  echo Phase 1 body build completed.
  echo Send these two files:
  echo   TheShatteredVeil\Progress\Phase1_Body_Front.png
  echo   TheShatteredVeil\Progress\Phase1_Body_Side.png
)
pause
exit /b %EXIT_CODE%
