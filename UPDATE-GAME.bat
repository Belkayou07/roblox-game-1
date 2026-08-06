@echo off
setlocal
cd /d "%~dp0"

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\update-and-open.ps1"

if errorlevel 1 (
    echo.
    echo The update did not finish successfully.
    pause
)

endlocal
