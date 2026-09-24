@echo off
cd /d "%~dp0"

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not found in PATH. Please install Python or contact admin.
    pause
    exit /b 1
)

python -m streamlit run app.py --server.headless=false --browser.gatherUsageStats=false