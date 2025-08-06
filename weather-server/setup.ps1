# Weather MCP Server Setup Script for Windows
# Run this script in PowerShell to set up the weather MCP server

Write-Host "🌤️  Setting up Weather MCP Server" -ForegroundColor Cyan
Write-Host "=" * 50

# Check if we're in the right directory
if (-not (Test-Path "weather.py")) {
    Write-Host "❌ Please run this script from the weather-server directory" -ForegroundColor Red
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
    Write-Host "Installing uv package manager..." -ForegroundColor Yellow
    Invoke-CommandWithLogging -Command 'powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"' -Description "Installing uv"
    
    Write-Host "⚠️  Please restart your terminal and run this script again to use uv" -ForegroundColor Yellow
    Write-Host "Press any key to continue..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 0
}

# Create virtual environment
Invoke-CommandWithLogging -Command "uv venv" -Description "Creating virtual environment"

# Install dependencies
Invoke-CommandWithLogging -Command "uv add mcp httpx" -Description "Installing dependencies"

Write-Host ""
Write-Host "🎉 Setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "To run the server:" -ForegroundColor Cyan
Write-Host "  uv run weather.py" -ForegroundColor White
Write-Host ""
Write-Host "To test the server:" -ForegroundColor Cyan
Write-Host "  cd .." -ForegroundColor White
Write-Host "  powershell -File test-weather-server.ps1" -ForegroundColor White
Write-Host ""
Write-Host "The weather server has been added to your MCP configuration." -ForegroundColor Green
Write-Host "Restart Claude Desktop to use the new weather tools!" -ForegroundColor Green
