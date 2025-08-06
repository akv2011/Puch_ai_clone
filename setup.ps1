#!/usr/bin/env powershell
# Setup script for WhatsApp-Gemini MCP Server Integration

Write-Host "🚀 Setting up WhatsApp-Gemini MCP Server Integration" -ForegroundColor Green
Write-Host "=" * 60

# Check if uv is installed
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow
if (!(Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "❌ uv not found. Installing uv..." -ForegroundColor Red
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install uv" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ uv installed successfully" -ForegroundColor Green
} else {
    Write-Host "✅ uv is already installed" -ForegroundColor Green
}

# Setup WhatsApp-Gemini Server
Write-Host "`n📱 Setting up WhatsApp-Gemini server..." -ForegroundColor Yellow
Set-Location whatsapp-gemini-server
uv sync
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to setup WhatsApp-Gemini server" -ForegroundColor Red
    exit 1
}
Write-Host "✅ WhatsApp-Gemini server setup complete" -ForegroundColor Green

# Setup Weather Server
Write-Host "`n🌤️ Setting up Weather server..." -ForegroundColor Yellow
Set-Location ..\weather-server
uv sync
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to setup Weather server" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Weather server setup complete" -ForegroundColor Green

# Return to project root
Set-Location ..

Write-Host "`n🎉 Setup completed successfully!" -ForegroundColor Green
Write-Host "`n📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Configure API keys in whatsapp-gemini-server/.env" -ForegroundColor White
Write-Host "2. Update .vscode/mcp.json with correct paths" -ForegroundColor White
Write-Host "3. Restart VS Code to load MCP servers" -ForegroundColor White
Write-Host "4. Test with: @get_server_status" -ForegroundColor White
