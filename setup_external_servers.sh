#!/usr/bin/env bash
# Setup External MCP Servers Script
# This script clones the external MCP servers used in the examples

echo "🔌 Setting up External MCP Servers..."
echo "======================================"

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d ".vscode" ]; then
    echo "❌ Please run this script from the Puch_ai_clone directory"
    exit 1
fi

echo ""
echo "📦 Cloning Financial Datasets MCP Server..."
if [ ! -d "financial-datasets-server" ]; then
    git clone https://github.com/ktanaka101/financial-datasets-mcp-server.git financial-datasets-server
    echo "✅ Financial Datasets Server cloned"
else
    echo "⚠️  Financial Datasets Server already exists"
fi

echo ""
echo "🌤️  Cloning Weather MCP Server..."
if [ ! -d "weather-server-new" ]; then
    git clone https://github.com/rossshannon/weekly-weather-mcp.git weather-server-new
    echo "✅ Weather Server cloned"
else
    echo "⚠️  Weather Server already exists"
fi

echo ""
echo "🔧 Installing Dependencies..."

# Install Financial Server Dependencies
if [ -d "financial-datasets-server" ]; then
    echo "Installing Financial Server dependencies..."
    cd financial-datasets-server
    if command -v uv &> /dev/null; then
        uv add requests aiohttp
    else
        pip install requests aiohttp
    fi
    cd ..
fi

# Install Weather Server Dependencies  
if [ -d "weather-server-new" ]; then
    echo "Installing Weather Server dependencies..."
    cd weather-server-new
    python -m venv .venv
    source .venv/Scripts/activate 2>/dev/null || source .venv/bin/activate
    pip install -r requirements.txt
    cd ..
fi

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Get API keys:"
echo "   • Financial: https://financialdatasets.ai"
echo "   • Weather: https://openweathermap.org/api (One Call API 3.0)"
echo ""
echo "2. Add API keys to your configuration:"
echo "   • Update .vscode/mcp.json"
echo "   • Update whatsapp-gemini-server/.env"
echo ""
echo "3. Follow the complete guide: HOW_TO_ADD_MCP_SERVERS.md"
echo ""
echo "✨ Your WhatsApp AI system will automatically discover all tools!"
