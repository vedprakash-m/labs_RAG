@echo off
REM Azure Healthcare RAG Setup for Windows
REM This batch file runs the PowerShell script on Windows systems

echo Starting Azure Healthcare RAG Setup...
echo.

REM Check if PowerShell 7+ is available
where pwsh >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo Using PowerShell 7+
    pwsh -ExecutionPolicy Bypass -File setup_azure_rag.ps1
) else (
    echo PowerShell 7+ not found, trying Windows PowerShell...
    powershell -ExecutionPolicy Bypass -File setup_azure_rag.ps1
)

if %ERRORLEVEL% neq 0 (
    echo.
    echo Setup encountered errors. Please check the output above.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Setup completed successfully!
pause