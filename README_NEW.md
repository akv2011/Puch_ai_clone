# Multi-Server MCP System with WhatsApp Intelligence 🚀

A comprehensive Model Context Protocol (MCP) ecosystem that integrates **WhatsApp messaging**, **Weather APIs**, **Task Management**, and **Google Gemini AI** for intelligent automation and conversation handling.

## 🎯 THE COMPLETE FLOW

```
📱 WhatsApp User
    ↓ (sends message)
🌐 Twilio Webhook → Webhook Receiver (Port 5000)
    ↓ (message logged/processed)  
💻 VS Code Gemini (with MCP servers)
    ↓ (intelligently routes to appropriate tools)
🔧 MCP Servers:
   • weather → get forecasts & alerts
   • task-master-ai → manage tasks & projects  
   • whatsapp-tools → send responses back
    ↓ (sends AI-powered response)
📱 WhatsApp User (receives intelligent reply)
```

## 🏗️ System Architecture

### **3 MCP Servers Working Together:**

1. **Weather Server** (`weather-server/weather.py`)
   - Get weather forecasts by coordinates
   - Get weather alerts by state
   - National Weather Service API integration

2. **Task Master AI** (NPM package)
   - Project management and task tracking
   - AI-powered task creation and organization
   - Multiple API provider support

3. **WhatsApp Tools** (`whatsapp-gemini-server/whatsapp_mcp_tools.py`)
   - Send WhatsApp messages via Twilio
   - Check connection status
   - Handle message formatting and limits

### **Webhook Receiver** (`whatsapp-gemini-server/webhook_receiver.py`)
- Receives incoming WhatsApp messages
- Provides simple auto-replies
- Logs messages for VS Code processing
- Integrates with MCP ecosystem

## 🚀 What You Can Do

### **In VS Code with Gemini:**
```
"Get the weather forecast for New York and send it to +1234567890 via WhatsApp"
```
**Gemini will:**
1. Use `weather` MCP server to get forecast
2. Use `whatsapp-tools` MCP server to send the result
3. Provide intelligent, contextual responses

### **Through WhatsApp:**
- Send messages to your Twilio number
- Get auto-replies via webhook
- Process complex requests using VS Code MCP tools

## 📁 Project Structure

```
Puch_ai_clone/
├── .vscode/
│   └── mcp.json                    # MCP server configuration
├── whatsapp-gemini-server/
│   ├── whatsapp_mcp_tools.py      # WhatsApp MCP server
│   ├── webhook_receiver.py        # Webhook message receiver  
│   ├── whatsapp_master.py         # Integrated demo system
│   ├── whatsapp_simple.py         # Simple webhook (legacy)
│   ├── whatsapp_gemini.py         # VS Code MCP server (legacy)
│   └── .env                       # API credentials
├── weather-server/
│   └── weather-standalone/
│       └── weather.py             # Weather MCP server
└── tests/                         # Test files
```

## ⚡ Quick Start Guide

### 🔧 **Prerequisites**
- Python 3.10+
- uv (Python package manager)
- VS Code with MCP support
- ngrok (for webhook exposure)
- Google Gemini API Key
- Twilio Account (free tier works)

### 📋 **Step 1: Installation**
```powershell
# Clone and setup
git clone <your-repo>
cd Puch_ai_clone

# Install dependencies
cd whatsapp-gemini-server
uv sync
cd ../weather-server/weather-standalone
uv sync
```

### 🔑 **Step 2: API Configuration**
Create `whatsapp-gemini-server/.env`:
```env
# Google Gemini API (get from https://makersuite.google.com/app/apikey)
GEMINI_API_KEY=your_gemini_api_key_here

# Twilio Configuration (get from https://console.twilio.com/)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

### 🚀 **Step 3: Start the System**

#### **Option A: For WhatsApp Auto-Reply (Standalone)**
```powershell
cd whatsapp-gemini-server
uv run python webhook_receiver.py
```
Then expose with ngrok:
```powershell
ngrok http 5000
```

#### **Option B: For VS Code MCP Integration**
1. **Restart VS Code** to load MCP servers
2. **Open Gemini Chat** in VS Code
3. **Available MCP tools:**
   - Weather: `get_forecast`, `get_alerts`
   - WhatsApp: `send_whatsapp`, `get_whatsapp_status`
   - Tasks: Full task management suite

### 🔗 **Step 4: Connect WhatsApp Webhook**
1. Copy your ngrok URL (e.g., `https://abc123.ngrok.io`)
2. Go to [Twilio Console → WhatsApp Sandbox](https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox)
3. Set webhook URL: `https://abc123.ngrok.io/webhook`
4. Send test message to: `+1 415 523 8886`

## 🛠️ Available MCP Tools

### Weather Server (`weather`)
```
get_forecast(latitude, longitude) → Weather forecast
get_alerts(state) → Weather alerts for US state
```

### WhatsApp Tools (`whatsapp-tools`)
```
send_whatsapp(phone_number, message) → Send WhatsApp message
get_whatsapp_status() → Check Twilio connection
```

### Task Master AI (`task-master-ai`)
```
Full task management, project planning, and AI-powered organization
```

## 🎯 Example Usage

### **In VS Code Gemini Chat:**

**Weather + WhatsApp:**
```
"Get the weather forecast for latitude 40.7128, longitude -74.0060 and send it to +1234567890 via WhatsApp"
```

**Task Management:**
```
"Create a new task for implementing user authentication"
```

**Status Check:**
```
"Check the WhatsApp connection status"
```

### **Via WhatsApp:**
- Send: `"help"` → Get available commands
- Send: `"weather in New York"` → Get auto-reply with note about MCP tools
- Send: Any message → Get AI auto-reply

## 🔧 Configuration Files

### **MCP Configuration** (`.vscode/mcp.json`)
```json
{
  "servers": {
    "weather": { /* Weather server config */ },
    "task-master-ai": { /* Task management config */ },
    "whatsapp-tools": { /* WhatsApp tools config */ }
  }
}
```

### **Environment Variables** (`.env`)
```env
GEMINI_API_KEY=your_key_here
TWILIO_ACCOUNT_SID=your_sid_here
TWILIO_AUTH_TOKEN=your_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

## 🚀 Advanced Features

### **Intelligent Routing**
Gemini automatically determines which MCP servers to use based on context:
- Weather queries → Weather server
- Task mentions → Task Master AI
- Message sending → WhatsApp tools
- General queries → Direct Gemini response

### **Multi-Server Coordination**
Example: "Get weather for NYC, create a task to check it daily, and send the forecast to my phone"
1. Uses weather server for forecast
2. Uses task server to create reminder task
3. Uses WhatsApp tools to send message

### **Error Handling**
- Automatic retry logic for API calls
- Graceful fallbacks for server failures
- Character limit handling for WhatsApp
- Comprehensive logging for debugging

## 🧪 Testing

### **Test MCP Servers:**
```powershell
# Test weather server
cd weather-server/weather-standalone
uv run python weather.py

# Test WhatsApp tools
cd whatsapp-gemini-server
uv run python whatsapp_mcp_tools.py
```

### **Test Webhook:**
```powershell
# Start webhook receiver
cd whatsapp-gemini-server
uv run python webhook_receiver.py

# Test endpoint
curl http://localhost:5000/test
```

## 📱 WhatsApp Setup Guide

### **1. Twilio Account Setup:**
1. Sign up at [Twilio](https://www.twilio.com/)
2. Go to [WhatsApp Sandbox](https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox)
3. Note your Account SID and Auth Token
4. WhatsApp number: `+1 415 523 8886`

### **2. Test Connection:**
1. Send "join [your-sandbox-word]" to `+1 415 523 8886`
2. You should receive confirmation
3. Start your webhook receiver
4. Send any message to test auto-reply

## 🎉 Success Indicators

### **MCP Servers Working:**
- ✅ VS Code shows MCP tools in chat
- ✅ No errors in VS Code MCP logs
- ✅ Tools respond correctly when called

### **WhatsApp Integration Working:**
- ✅ Webhook receives POST requests
- ✅ Auto-replies are sent successfully
- ✅ Messages appear in terminal logs

### **End-to-End Flow Working:**
- ✅ Gemini can call multiple MCP tools in sequence
- ✅ Weather data is retrieved and sent via WhatsApp
- ✅ Tasks are created and managed through chat

## 🆘 Troubleshooting

### **MCP Servers Not Loading:**
1. Check `.vscode/mcp.json` syntax
2. Verify file paths in configuration
3. Restart VS Code
4. Check MCP logs in VS Code Output panel

### **WhatsApp Not Receiving:**
1. Verify ngrok is running and URL is correct
2. Check Twilio webhook configuration
3. Test with `/test` endpoint
4. Verify Twilio credentials in `.env`

### **API Errors:**
1. Verify all API keys are correct
2. Check API quotas and limits
3. Review error logs in terminal
4. Test individual components separately

## 🚀 Next Steps

### **Extend the System:**
- Add more MCP servers (email, calendar, etc.)
- Implement user authentication
- Add conversation memory
- Create custom AI personas

### **Production Deployment:**
- Use proper webhook hosting (not ngrok)
- Implement rate limiting
- Add monitoring and alerts
- Set up proper secrets management

---

**🎯 This system gives you the intelligent routing you wanted:** WhatsApp → Gemini → Multiple MCP servers → Intelligent responses back to WhatsApp! 🚀
