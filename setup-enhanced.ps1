#!/usr/bin/env powershell
# Enhanced setup script for WhatsApp-Gemini MCP Server with multi-server support

Write-Host "Setting up Enhanced WhatsApp-Gemini MCP Server" -ForegroundColor Green
Write-Host "==========================================================="

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check if uv is installed
if (!(Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "uv not found. Installing uv..." -ForegroundColor Red
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install uv" -ForegroundColor Red
        exit 1
    }
    Write-Host "uv installed successfully" -ForegroundColor Green
} else {
    Write-Host "uv is already installed" -ForegroundColor Green
}

# Check if npm/npx is available for task-master
if (Get-Command npm -ErrorAction SilentlyContinue) {
    Write-Host "npm/npx is available for task-master" -ForegroundColor Green
} else {
    Write-Host "npm/npx not found. Task-master may not work" -ForegroundColor Yellow
}

# Setup Enhanced WhatsApp-Gemini Server
Write-Host "Setting up Enhanced WhatsApp-Gemini server..." -ForegroundColor Yellow
Set-Location whatsapp-gemini-server

# Add enhanced dependencies
Write-Host "Installing enhanced dependencies..." -ForegroundColor Yellow
uv add google-genai twilio python-dotenv flask mcp httpx
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install enhanced dependencies" -ForegroundColor Red
    exit 1
}

uv sync
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to sync enhanced WhatsApp-Gemini server" -ForegroundColor Red
    exit 1
}
Write-Host "Enhanced WhatsApp-Gemini server setup complete" -ForegroundColor Green

# Setup Weather Server
Write-Host "Setting up Weather server..." -ForegroundColor Yellow
Set-Location ..\weather-server
uv sync
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to setup Weather server" -ForegroundColor Red
    exit 1
}
Write-Host "Weather server setup complete" -ForegroundColor Green

# Return to project root
Set-Location ..

# Test the enhanced setup
Write-Host "Testing enhanced setup..." -ForegroundColor Yellow
Set-Location whatsapp-gemini-server

Write-Host "Testing enhanced server syntax..." -ForegroundColor Cyan
$syntaxTest = uv run python -m py_compile whatsapp_gemini_enhanced.py 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "Enhanced server syntax is valid" -ForegroundColor Green
} else {
    Write-Host "Enhanced server syntax error:" -ForegroundColor Red
    Write-Host $syntaxTest
    Set-Location ..
    exit 1
}

# Test imports
Write-Host "Testing enhanced imports..." -ForegroundColor Cyan
$importsTest = uv run python -c @"
try:
    from google import genai
    from mcp.server.fastmcp import FastMCP
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    print('All enhanced imports successful')
except ImportError as e:
    print(f'Import error: {e}')
    exit(1)
"@ 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "All enhanced imports working" -ForegroundColor Green
} else {
    Write-Host "Enhanced import error:" -ForegroundColor Red
    Write-Host $importsTest
}

Set-Location ..

Write-Host "Enhanced setup completed successfully!" -ForegroundColor Green
Write-Host "What's New in Enhanced Version:" -ForegroundColor Cyan
Write-Host "   Multi-MCP server support" -ForegroundColor White
Write-Host "   Gemini can now control weather and task-master servers" -ForegroundColor White
Write-Host "   Automatic tool discovery and routing" -ForegroundColor White
Write-Host "   Enhanced WhatsApp responses with real-time data" -ForegroundColor White
Write-Host "   Function calling with Gemini 2.5" -ForegroundColor White

Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Test enhanced server: cd whatsapp-gemini-server; uv run test_whatsapp_enhanced.py" -ForegroundColor White
Write-Host "2. VS Code will now have access to 'whatsapp-gemini-enhanced' server" -ForegroundColor White
Write-Host "3. Restart VS Code to load the enhanced MCP server" -ForegroundColor White
Write-Host "4. Test with weather queries: @get weather forecast for New York" -ForegroundColor White
Write-Host "5. Test with task management: @create task for project planning" -ForegroundColor White

Write-Host "Available MCP Servers:" -ForegroundColor Cyan
Write-Host "   whatsapp-gemini-enhanced (NEW!) - Multi-server capable Gemini" -ForegroundColor Green
Write-Host "   weather - Weather forecasts and alerts" -ForegroundColor Blue
Write-Host "   task-master-ai - Task and project management" -ForegroundColor Magenta
Write-Host "   whatsapp-gemini - Original simple version" -ForegroundColor Gray

Write-Host "Enhanced Features Available:" -ForegroundColor Cyan
Write-Host "   send_whatsapp_with_gemini_enhanced" -ForegroundColor White
Write-Host "   chat_with_gemini_enhanced" -ForegroundColor White
Write-Host "   list_available_mcp_tools" -ForegroundColor White
Write-Host "   call_mcp_tool_directly" -ForegroundColor White
Write-Host "   get_server_status (enhanced)" -ForegroundColor White
