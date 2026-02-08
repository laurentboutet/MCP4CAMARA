@echo off
setlocal enabledelayedexpansion

echo 🚀 CAMARA FastMCP Server - Setup Script
echo ========================================

REM Check Python
py -3.13 --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 3.13 not found. Please install from python.org
    exit /b 1
)

echo ✅ Python detected

REM Create virtual environment
if not exist "venv" (
    echo 📦 Creating virtual environment...
    py -3.13 -m venv venv
)

REM Activate venv
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements_fastmcp.txt

REM Create .env
if not exist ".env" (
    echo 📝 Creating .env from template...
    copy .env.example .env
    echo ⚠️  Please edit .env with your CAMARA credentials!
)

echo.
echo ✅ Setup complete!
echo.
echo 📋 Next steps:
echo    1. Edit .env with your CAMARA_BASE_URL and CAMARA_API_KEY
echo    2. For Claude Desktop: See CLAUDE_SETUP.md
echo    3. For server mode: py -3.13 camara_final_complete.py --server
echo    4. For local mode: py -3.13 camara_final_complete.py
echo.
pause
