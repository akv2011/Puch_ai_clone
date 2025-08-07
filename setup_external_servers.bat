@echo off
REM Setup External MCP Servers Script (Windows)
REM This script clones the external MCP servers used in the examples

echo 🔌 Setting up External MCP Servers...
echo ======================================

REM Check if we're in the right directory
if not exist "README.md" (
    echo ❌ Please run this script from the Puch_ai_clone directory
    exit /b 1
)
if not exist ".vscode" (
    echo ❌ Please run this script from the Puch_ai_clone directory  
    exit /b 1
)

echo.
echo 📦 Cloning Financial Datasets MCP Server...
if not exist "financial-datasets-server" (
    git clone https://github.com/ktanaka101/financial-datasets-mcp-server.git financial-datasets-server
    echo ✅ Financial Datasets Server cloned
) else (
    echo ⚠️ Financial Datasets Server already exists
)

echo.
echo 🌤️ Cloning Weather MCP Server...
if not exist "weather-server-new" (
    git clone https://github.com/rossshannon/weekly-weather-mcp.git weather-server-new
    echo ✅ Weather Server cloned
) else (
    echo ⚠️ Weather Server already exists
)

echo.
echo 🔧 Installing Dependencies...

REM Install Financial Server Dependencies
if exist "financial-datasets-server" (
    echo Installing Financial Server dependencies...
    cd financial-datasets-server
    where uv >nul 2>nul
    if %errorlevel% == 0 (
        uv add requests aiohttp
    ) else (
        pip install requests aiohttp
    )
    cd ..
)

REM Install Weather Server Dependencies
if exist "weather-server-new" (
    echo Installing Weather Server dependencies...
    cd weather-server-new
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
    cd ..
)

echo.
echo 🎉 Setup Complete!
echo.
echo 📋 Next Steps:
echo 1. Get API keys:
echo    • Financial: https://financialdatasets.ai
echo    • Weather: https://openweathermap.org/api (One Call API 3.0)
echo.
echo 2. Add API keys to your configuration:
echo    • Update .vscode/mcp.json
echo    • Update whatsapp-gemini-server/.env
echo.
echo 3. Follow the complete guide: HOW_TO_ADD_MCP_SERVERS.md
echo.
echo ✨ Your WhatsApp AI system will automatically discover all tools!
pause
