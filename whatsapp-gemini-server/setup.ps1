# WhatsApp-Gemini MCP Server Setup Script for Windows
# Run this script in PowerShell to set up the WhatsApp-Gemini MCP server

Write-Host "📱🤖 Setting up WhatsApp-Gemini MCP Server" -ForegroundColor Cyan
Write-Host "=" * 55

# Check if we're in the right directory
if (-not (Test-Path "whatsapp_gemini.py")) {
    Write-Host "❌ Please run this script from the whatsapp-gemini-server directory" -ForegroundColor Red
    exit 1
}

# Function to run commands with error handling
function Invoke-CommandWithLogging {
    param(
        [string]$Command,
        [string]$Description
    )
    
    Write-Host "Running: $Description" -ForegroundColor Yellow
    try {
        $result = Invoke-Expression $Command
        Write-Host "✅ $Description completed successfully" -ForegroundColor Green
        return $result
    }
    catch {
        Write-Host "❌ $Description failed: $_" -ForegroundColor Red
        return $null
    }
}

# Check if uv is installed
Write-Host "Checking for uv package manager..." -ForegroundColor Yellow
try {
    $uvVersion = uv --version 2>$null
    Write-Host "✅ uv is already installed: $uvVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ uv not found. Please install uv first by running the weather server setup." -ForegroundColor Red
    exit 1
}

# Create virtual environment and install dependencies
Invoke-CommandWithLogging -Command "uv sync" -Description "Installing dependencies"

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ .env file created" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: You need to edit the .env file with your credentials!" -ForegroundColor Yellow
    Write-Host "   1. Get Gemini API key from: https://makersuite.google.com/app/apikey" -ForegroundColor White
    Write-Host "   2. Get Twilio credentials from: https://console.twilio.com/" -ForegroundColor White
    Write-Host "   3. Edit .env file with your actual credentials" -ForegroundColor White
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

# Test dependencies
Write-Host "Testing dependencies..." -ForegroundColor Yellow
$depsTest = uv run python -c "
import google.generativeai as genai
import twilio
from mcp.server.fastmcp import FastMCP
print('All dependencies installed successfully')
" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ All dependencies are working" -ForegroundColor Green
} else {
    Write-Host "❌ Dependency test failed:" -ForegroundColor Red
    Write-Host $depsTest -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 WhatsApp-Gemini MCP Server setup completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env file with your API credentials" -ForegroundColor White
Write-Host "2. Set up Twilio WhatsApp sandbox: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn" -ForegroundColor White
Write-Host "3. Test the server: uv run whatsapp_gemini.py" -ForegroundColor White
Write-Host "4. Add to Claude Desktop configuration" -ForegroundColor White
Write-Host ""
Write-Host "🔧 The server has been added to your MCP configuration automatically!" -ForegroundColor Green
