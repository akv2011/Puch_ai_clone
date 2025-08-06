# WhatsApp-Gemini MCP Server with Intelligent Routing 🧠

A Model Context Protocol server that integrates WhatsApp messaging with Google's Gemini AI, featuring **intelligent routing** between direct AI responses and specialized MCP tools for weather, tasks, and more.

## 🚀 Current Production Features

- **🧠 Intelligent Routing**: Automatically routes weather queries to MCP tools, general queries to Gemini
- **⚡ Real-time Weather**: Integration with National Weather Service API
- **📱 WhatsApp Integration**: Full Twilio webhook processing with auto-replies  
- **🔧 MCP Tools**: Send WhatsApp messages from VS Code Gemini
- **🛡️ Error Handling**: Graceful fallbacks and character limit handling
- **⚙️ Multi-threading**: Non-blocking webhook responses

## 🏗️ Production Architecture

```
📱 WhatsApp Message
    ↓
🌐 Twilio Webhook → production/whatsapp_mcp_bridge.py
    ↓ (intelligent keyword analysis)
🧠 Smart Routing:
   • Weather keywords → MCP Weather Tools → Real forecast data
   • General queries → Direct Gemini → Conversational responses
    ↓
📱 WhatsApp Auto-Reply (intelligently crafted)
```

## 🛠️ Available Production Tools

### **WhatsApp MCP Server** (`production/whatsapp_mcp_tools.py`)
- `send_whatsapp(phone_number, message)` → Send WhatsApp message from VS Code
- `get_whatsapp_status()` → Check Twilio connection status

### **Intelligent Webhook** (`production/whatsapp_mcp_bridge.py`)  
- Smart keyword-based routing (weather → MCP, general → Gemini)
- Real weather data from National Weather Service
- Character limit handling (1600 chars)
- Multi-threaded processing for fast responses

## 📋 Prerequisites

1. **Google Gemini API Key**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Keep it secure

2. **Twilio Account** (for WhatsApp)
   - Sign up at [Twilio](https://www.twilio.com/)
   - Get your Account SID and Auth Token
   - Enable WhatsApp sandbox for testing

## ⚙️ Setup Instructions

### 1. Install Dependencies

```powershell
cd whatsapp-gemini-server
uv sync
```

### 2. Configure Environment

1. Copy the environment template:
   ```powershell
   copy .env.example .env
   ```

2. Edit `.env` file with your credentials:
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key
   TWILIO_ACCOUNT_SID=your_twilio_account_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
   ```

### 3. Set Up Twilio WhatsApp Sandbox

1. Go to [Twilio Console WhatsApp Sandbox](https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn)
2. Follow the instructions to join the sandbox
3. Send the activation message to the sandbox number

### 4. Test the Production System

**Test Intelligent Webhook:**
```powershell
cd production
uv run whatsapp_mcp_bridge.py
```

**Test MCP Server:**
```powershell
# In VS Code, restart and test MCP tools
cd production  
uv run whatsapp_mcp_tools.py
```

## 🔧 VS Code MCP Configuration

Your system is configured in `.vscode/mcp.json` with:

```json
{
  "servers": {
    "whatsapp-tools": {
      "command": "C:\\Users\\arunk\\.local\\bin\\uv.exe",
      "args": [
        "--directory", 
        "c:\\Users\\arunk\\Puch_ai_clone\\whatsapp-gemini-server\\production",
        "run", 
        "whatsapp_mcp_tools.py"
      ],
      "type": "stdio"
    }
  }
}
```

## 📱 Production Usage Examples

### **In VS Code Gemini Chat:**

1. **Send WhatsApp with current weather data**:
   ```
   "Send the weather forecast for New York to +1234567890 via WhatsApp"
   ```

2. **Check system status**:
   ```
   "Check the WhatsApp connection status"
   ```

### **Via WhatsApp (Intelligent Auto-Reply):**

**Weather Queries** (→ Routes to MCP Tools):
- Send: `"What's the weather in Tokyo?"` → Real forecast data
- Send: `"Weather in NYC"`→ Current conditions and forecast
- Send: `"Is it going to rain in London?"` → Precipitation forecast

**General Queries** (→ Routes to Direct Gemini):
- Send: `"Hi"` → Conversational AI response
- Send: `"Tell me a joke"` → Gemini-powered humor
- Send: `"How are you?"` → Natural conversation

### **Smart Routing Examples:**
```
Input: "Weather in Chicago" 
→ Detects weather keywords
→ Routes to MCP weather tools  
→ Returns real Chicago forecast

Input: "Hello, how are you?"
→ No weather/task keywords detected
→ Routes to direct Gemini
→ Returns conversational response
```

## 🔐 Security Notes

- **Never commit your `.env` file** - it contains sensitive credentials
- **Use environment variables** for production deployments
- **Twilio Sandbox** is for testing only - upgrade for production use

## 🐛 Troubleshooting

### Common Issues:

1. **"Gemini API key not configured"**
   - Ensure `GEMINI_API_KEY` is set in your `.env` file
   - Verify the API key is valid

2. **"Twilio not configured"**
   - Check `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` in `.env`
   - Verify credentials are correct

3. **WhatsApp messages not sending**
   - Ensure you've activated the Twilio WhatsApp sandbox
   - Check that the recipient has also joined the sandbox
   - Verify phone number format (+1234567890)

4. **Import errors**
   - Run `uv sync` to install all dependencies

### Logs and Debugging:

The server logs all activities to stderr. Check the logs for detailed error information.

## 🔄 Production Workflow

1. **WhatsApp User sends message** → Twilio Webhook
2. **Intelligent webhook** (`production/whatsapp_mcp_bridge.py`) analyzes keywords
3. **Smart routing decision**:
   - Weather keywords → Calls MCP weather tools → Real data
   - General queries → Direct Gemini → Conversational AI
4. **AI response sent** → WhatsApp via Twilio (auto-reply)
5. **VS Code MCP integration** → Send messages from Gemini chat

## 🧠 Intelligence Features

- **🎯 Keyword Detection**: Automatically detects weather-related queries
- **🔄 Dynamic Routing**: Routes to specialized tools vs general AI
- **🛡️ Graceful Fallbacks**: Falls back to Gemini if MCP tools fail  
- **⚡ Real-time Data**: Weather from National Weather Service API
- **📏 Smart Formatting**: Handles WhatsApp 1600 character limits
- **🔄 Non-blocking**: Multi-threaded webhook processing

## 🌟 Advanced Features

- **Context support**: Provide context to Gemini for better responses
- **Message history**: Track sent messages with SIDs
- **Error handling**: Comprehensive error reporting
- **Service monitoring**: Real-time status checking

## 📚 API References

- [Google Gemini API](https://ai.google.dev/docs)
- [Twilio WhatsApp API](https://www.twilio.com/docs/whatsapp)
- [MCP Protocol](https://modelcontextprotocol.io/)

## 📁 Production File Structure

```
whatsapp-gemini-server/
├── production/                    # 🚀 Production-ready code
│   ├── whatsapp_mcp_bridge.py        # Main intelligent webhook
│   └── whatsapp_mcp_tools.py         # WhatsApp MCP server for VS Code
├── legacy/                        # 📦 Archived old versions  
├── .env                          # 🔑 Environment configuration
├── README.md                     # 📖 This documentation
└── setup.ps1                     # ⚙️ Setup script
```

## 🚀 Quick Start Commands

```powershell
# Setup the system
cd whatsapp-gemini-server
.\setup.ps1

# Start intelligent webhook
cd production  
uv run whatsapp_mcp_bridge.py

# In another terminal, expose webhook
ngrok http 5000

# Test in VS Code Gemini Chat
"Send a weather update to +1234567890 via WhatsApp"
```
