@echo off
title UiPath Maestro Case Portal Launcher
color 0b

echo ====================================================================
echo   UiPath Maestro Case Portal - Tech Pack Processor Launcher
echo ====================================================================
echo.

:: 1. Verify Python Installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not configured in your system PATH.
    echo Please install Python 3.8+ and tick "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: 2. Set current project directory path
set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

:: 3. Setup Virtual Environment (Venv)
if not exist "venv" (
    echo [Setup] Creating self-contained virtual environment (venv)...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to initialize virtual environment.
        pause
        exit /b 1
    )
)

echo [Setup] Activating Python environment...
call venv\Scripts\activate

:: 4. Install Dependencies
echo [Setup] Verifying and installing required packages (FastAPI, Gemini, openpyxl)...
python -m pip install --upgrade pip >nul 2>&1
pip install -r ai-agent\requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install packages. Check internet connection.
    pause
    exit /b 1
)

:: 5. Generate Sample Tech Packs
if not exist "sample-data\sample_techpack_1.pdf" (
    echo [Setup] Creating mock PDF tech packs for testing...
    python sample-data\generate_sample_data.py
)

:: 6. Launch FastAPI Backend Server in New Window
echo [System] Starting FastAPI server on http://127.0.0.1:8000/ ...
start "FastAPI Server - Tech Pack Processing" cmd /c "call venv\Scripts\activate && cd ai-agent && uvicorn main:app --host 127.0.0.1 --port 8000"

:: 7. Wait 3 seconds for uvicorn to bind to port
timeout /t 3 /nobreak >nul

:: 8. Launch Browser
echo [System] Opening your default web browser to portal UI...
start http://localhost:8000/

echo.
echo ====================================================================
echo   PORTAL INITIATED SUCCESSFULLY!
echo   * Keep the newly opened console window active to run the server.
echo   * Press any key in this window to close the launcher.
echo ====================================================================
echo.
pause
