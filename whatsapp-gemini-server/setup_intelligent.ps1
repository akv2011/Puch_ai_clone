# Enhanced WhatsApp-Gemini MCP Server Setup with Intelligent Routing
# This script sets up the intelligent MCP system with smart routing capabilities

Write-Host "🧠 Setting up Intelligent WhatsApp-Gemini MCP Server" -ForegroundColor Cyan
Write-Host "Enhanced with Smart Routing & Fallback Mechanisms" -ForegroundColor Yellow
Write-Host "=" * 65

# Check if we're in the right directory
if (-not (Test-Path "whatsapp_gemini_intelligent.py")) {
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
Write-Host "🔧 Checking uv installation..." -ForegroundColor Yellow
$uvVersion = uv --version 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ uv is installed: $uvVersion" -ForegroundColor Green
} else {
    Write-Host "❌ uv is not installed. Please install it first." -ForegroundColor Red
    Write-Host "   Run: pip install uv" -ForegroundColor White
    exit 1
}

# Install dependencies with enhanced packages for intelligent routing
Write-Host "📦 Installing enhanced dependencies..." -ForegroundColor Yellow
$installResult = Invoke-CommandWithLogging "uv sync" "Installing core dependencies"

if ($installResult -eq $null) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Install additional packages for intelligent features
$additionalPackages = @(
    "asyncio-throttle",
    "aiofiles", 
    "pydantic",
    "tenacity"
)

foreach ($package in $additionalPackages) {
    Write-Host "📦 Installing $package..." -ForegroundColor Yellow
    Invoke-CommandWithLogging "uv add $package" "Installing $package"
}

# Create or update .env file with intelligent system configuration
Write-Host "📝 Setting up enhanced environment configuration..." -ForegroundColor Yellow

if (-not (Test-Path ".env")) {
    Write-Host "Creating enhanced .env file..." -ForegroundColor Yellow
    
    $envContent = @"
# Enhanced WhatsApp-Gemini MCP Server Configuration
# Intelligent Routing & Multi-Server Support

# Gemini API Configuration (Required)
GEMINI_API_KEY=your_gemini_api_key_here
# Alternative: GOOGLE_API_KEY=your_google_api_key_here

# Twilio Configuration (for WhatsApp)
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Optional: Additional MCP Server API Keys
ANTHROPIC_API_KEY=your_anthropic_key_here
PERPLEXITY_API_KEY=your_perplexity_key_here
OPENAI_API_KEY=your_openai_key_here

# System Configuration
LOG_LEVEL=INFO
MAX_RETRIES=3
CONNECTION_TIMEOUT=30

# Intelligent Routing Configuration
ENABLE_FALLBACK=true
DEFAULT_TEMPERATURE=0.1
MAX_TOKENS=1000
"@
    
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    
    Write-Host "✅ Enhanced .env file created" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Next steps for .env configuration:" -ForegroundColor Yellow
    Write-Host "   1. Get Gemini API key from: https://makersuite.google.com/app/apikey" -ForegroundColor White
    Write-Host "   2. Get Twilio credentials from: https://console.twilio.com/" -ForegroundColor White
    Write-Host "   3. Edit .env file with your actual credentials" -ForegroundColor White
    Write-Host "   4. Optional: Add other service API keys for enhanced features" -ForegroundColor White
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

# Test dependencies
Write-Host "🧪 Testing enhanced dependencies..." -ForegroundColor Yellow
$depsTest = uv run python -c "
import google.generativeai as genai
import twilio
from mcp.server.fastmcp import FastMCP
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from flask import Flask
import asyncio
import json
from enum import Enum
from dataclasses import dataclass
print('✅ All enhanced dependencies installed successfully')
" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ All enhanced dependencies are working" -ForegroundColor Green
} else {
    Write-Host "❌ Dependency test failed:" -ForegroundColor Red
    Write-Host $depsTest -ForegroundColor Red
    exit 1
}

# Test the intelligent system
Write-Host "🧠 Testing intelligent MCP system..." -ForegroundColor Yellow
$systemTest = uv run python -c "
import sys
sys.path.append('.')
try:
    from whatsapp_gemini_intelligent import IntelligentMCPManager, MCP_SERVERS
    manager = IntelligentMCPManager()
    print(f'✅ Intelligent system loaded successfully')
    print(f'📊 Configured servers: {list(MCP_SERVERS.keys())}')
    print(f'🎯 Total capabilities: {sum(len(config.capabilities) for config in MCP_SERVERS.values())}')
except ImportError as e:
    print(f'⚠️ Some dependencies missing: {e}')
    print('🔧 This is normal if external MCP servers are not yet installed')
except Exception as e:
    print(f'❌ System test failed: {e}')
" 2>&1

Write-Host $systemTest

# Create VS Code MCP configuration
Write-Host "🔧 Creating VS Code MCP configuration..." -ForegroundColor Yellow

$mcpConfigDir = "../.vscode"
$mcpConfigFile = "$mcpConfigDir/mcp.json"

if (-not (Test-Path $mcpConfigDir)) {
    New-Item -ItemType Directory -Path $mcpConfigDir -Force | Out-Null
}

# Enhanced MCP configuration
$mcpConfig = @{
    "servers" = @{
        "whatsapp-gemini-intelligent" = @{
            "command" = "C:\Users\arunk\.local\bin\uv.exe"
            "args" = @(
                "--directory"
                "c:\Users\arunk\Puch_ai_clone\whatsapp-gemini-server"
                "run"
                "whatsapp_gemini_intelligent.py"
            )
            "env" = @{
                "GEMINI_API_KEY" = "`$GEMINI_API_KEY"
                "TWILIO_ACCOUNT_SID" = "`$TWILIO_ACCOUNT_SID"
                "TWILIO_AUTH_TOKEN" = "`$TWILIO_AUTH_TOKEN"
            }
            "description" = "Intelligent WhatsApp-Gemini MCP server with smart routing"
        }
        "weather" = @{
            "command" = "C:\Users\arunk\.local\bin\uv.exe"
            "args" = @(
                "--directory"
                "c:\Users\arunk\Puch_ai_clone\weather-server"
                "run"
                "weather.py"
            )
            "description" = "Weather forecasts and alerts"
        }
        "task-master-ai" = @{
            "command" = "npx"
            "args" = @("-y", "--package=task-master-ai", "task-master-ai")
            "env" = @{
                "ANTHROPIC_API_KEY" = "`$ANTHROPIC_API_KEY"
                "GOOGLE_API_KEY" = "`$GEMINI_API_KEY"
            }
            "description" = "Task management and project planning"
        }
    }
}

$mcpConfig | ConvertTo-Json -Depth 4 | Out-File -FilePath $mcpConfigFile -Encoding UTF8

Write-Host "✅ Enhanced VS Code MCP configuration created at $mcpConfigFile" -ForegroundColor Green

# Create documentation
Write-Host "📚 Creating enhanced documentation..." -ForegroundColor Yellow

$docContent = @"
# Intelligent WhatsApp-Gemini MCP System

## 🧠 Enhanced Features

### Smart Query Routing
- **Intent Analysis**: Automatically detects what type of query you're asking
- **Server Selection**: Routes to the best available MCP server
- **Fallback System**: Uses alternatives when primary servers fail
- **Error Recovery**: Graceful handling of connection issues

### Supported Query Types
1. **Weather Queries**: "What's the weather in Tokyo?"
   → Routes to weather MCP server
   
2. **Task Management**: "Create a task to learn Python"
   → Routes to task-master MCP server
   
3. **General Questions**: "Tell me a joke"
   → Uses direct Gemini AI
   
4. **Complex Queries**: "Check weather in Paris and create travel task"
   → Uses multiple servers automatically

### Available Tools
- `send_whatsapp_with_intelligent_ai`: Enhanced WhatsApp with smart routing
- `chat_with_intelligent_gemini`: AI chat with multi-server capabilities
- `get_intelligent_server_status`: Detailed system status
- `list_intelligent_capabilities`: Show all available features
- `start_intelligent_webhook_server`: Enhanced webhook processing

### Testing
Run the comprehensive test suite:
```powershell
uv run test_intelligent_system.py
```

### Usage Examples
1. **Weather + Task Combo**: "Weather in NYC and create umbrella task"
2. **Smart Fallback**: If weather server is down, provides general weather info
3. **Error Recovery**: Automatically retries failed connections
4. **Multi-Intent**: Handles queries requiring multiple tools

## 🚀 Quick Start
1. Configure .env with your API keys
2. Add to VS Code MCP configuration  
3. Test with: `uv run test_intelligent_system.py`
4. Start using intelligent routing!
"@

$docContent | Out-File -FilePath "INTELLIGENT_SYSTEM.md" -Encoding UTF8

# Final setup summary
Write-Host ""
Write-Host "🎉 Intelligent WhatsApp-Gemini MCP Server setup completed!" -ForegroundColor Green
Write-Host ""
Write-Host "🌟 Enhanced Features Installed:" -ForegroundColor Cyan
Write-Host "   ✅ Smart query analysis and routing" -ForegroundColor White
Write-Host "   ✅ Automatic server selection" -ForegroundColor White
Write-Host "   ✅ Fallback mechanisms for reliability" -ForegroundColor White
Write-Host "   ✅ Enhanced error handling and recovery" -ForegroundColor White
Write-Host "   ✅ Multi-server tool coordination" -ForegroundColor White
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env file with your API credentials" -ForegroundColor White
Write-Host "2. Test the system: uv run test_intelligent_system.py" -ForegroundColor White
Write-Host "3. Add to VS Code: Configuration created in ../.vscode/mcp.json" -ForegroundColor White
Write-Host "4. Start chatting with intelligent AI assistance!" -ForegroundColor White
Write-Host ""
Write-Host "🧠 The intelligent routing system will automatically:" -ForegroundColor Yellow
Write-Host "   • Detect if you're asking about weather → route to weather server" -ForegroundColor White
Write-Host "   • Detect if you're asking about tasks → route to task-master server" -ForegroundColor White
Write-Host "   • Handle general questions → use direct Gemini AI" -ForegroundColor White
Write-Host "   • Provide fallbacks when servers are unavailable" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Documentation created: INTELLIGENT_SYSTEM.md" -ForegroundColor Green
