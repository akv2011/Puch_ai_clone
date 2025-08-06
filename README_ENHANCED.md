# Enhanced WhatsApp-Gemini MCP Server with Multi-Server Control 🚀

A revolutionary Model Context Protocol (MCP) server that enables **Gemini AI to intelligently control and route to multiple MCP servers**, providing a unified interface for weather, task management, and WhatsApp messaging through natural language.

## 🌟 What's New in Enhanced Version

### **Revolutionary Multi-Server Architecture**
- **🧠 Intelligent Routing**: Gemini automatically routes queries to appropriate MCP servers
- **🔄 Dynamic Tool Discovery**: Automatically discovers and integrates tools from multiple servers
- **🎯 Function Calling**: Uses Gemini 2.5's function calling to seamlessly interact with tools
- **📡 Real-time Integration**: Connect to weather, task management, and other services in real-time

### **Enhanced Capabilities**
```
User: "What's the weather in Tokyo and create a task to pack for the trip?"
Enhanced Gemini: 
1. Routes weather query to weather server → Gets Tokyo forecast
2. Routes task creation to task-master server → Creates packing task
3. Combines responses in natural language
```

## 🎯 Key Features

### ✅ **Multi-MCP Server Control**
- **Weather Server**: Real-time weather forecasts and alerts
- **Task-Master Server**: Intelligent task and project management
- **WhatsApp Integration**: AI-powered messaging with tool access
- **Extensible Architecture**: Easy to add more MCP servers

### ✅ **Intelligent Query Routing**
```
"Weather in Paris" → Routes to Weather MCP
"Create a task" → Routes to Task-Master MCP  
"Tell me a joke" → Direct Gemini response
"Weather + Task" → Routes to both MCPs automatically
```

### ✅ **Enhanced WhatsApp Auto-Reply**
- Send weather queries via WhatsApp and get real-time forecasts
- Create and manage tasks through WhatsApp conversations
- Natural language interface for all MCP tools
- Automatic tool selection based on message content

## 🏗️ Architecture

```
WhatsApp User
     ↓
Twilio Webhook
     ↓
Enhanced Gemini (with Function Calling)
     ↓
┌─────────────────────────────────────┐
│  MCP Client Manager                 │
├─────────────────────────────────────┤
│  Weather MCP    │  Task-Master MCP  │
│  Tools:         │  Tools:           │
│  • get_forecast │  • add_task       │
│  • get_alerts   │  • get_tasks      │
└─────────────────────────────────────┘
     ↓
Real-time APIs (Weather, Task Storage)
```

## ⚡ Quick Start

### 1. Enhanced Setup
```powershell
# Run the enhanced setup script
powershell -ExecutionPolicy Bypass -File setup-enhanced.ps1
```

### 2. Test Enhanced Functionality
```powershell
cd whatsapp-gemini-server
uv run test_whatsapp_enhanced.py
```

### 3. Demo Multi-Server Capabilities
```powershell
uv run demo_enhanced.py
```

## 🛠️ Enhanced MCP Tools Available

### **WhatsApp-Gemini Enhanced Server**
| Tool | Description |
|------|-------------|
| `send_whatsapp_with_gemini_enhanced` | Send AI messages with multi-MCP tool access |
| `chat_with_gemini_enhanced` | Chat with Gemini that can use all MCP tools |
| `list_available_mcp_tools` | Discover all tools from connected servers |
| `call_mcp_tool_directly` | Call any MCP tool with JSON arguments |
| `get_server_status` | Check status of all connected services |

### **Auto-Connected MCP Servers**
- **Weather Server**: `get_forecast`, `get_alerts`
- **Task-Master Server**: `add_task`, `get_tasks`, `update_task`, etc.

## 📱 Enhanced WhatsApp Usage Examples

### Weather Queries
```
You → WhatsApp: "What's the weather like in London today?"
AI → WhatsApp: "🌤️ London Weather: 18°C, partly cloudy with light winds..."
```

### Task Management
```
You → WhatsApp: "Create a task to review quarterly reports"
AI → WhatsApp: "✅ Task created: 'Review quarterly reports' added to your task list"
```

### Combined Queries
```
You → WhatsApp: "Check weather in Miami and add a task to book flight tickets"
AI → WhatsApp: "🌴 Miami: 28°C, sunny ☀️
✅ Task created: 'Book flight tickets' 
Perfect weather for travel planning!"
```

## 🔧 VS Code Integration

Your `.vscode/mcp.json` now includes:

```json
{
  "servers": {
    "whatsapp-gemini-enhanced": {
      "command": "uv",
      "args": ["run", "whatsapp_gemini_enhanced.py"],
      "env": {
        "GEMINI_API_KEY": "your_key",
        "TWILIO_ACCOUNT_SID": "your_sid"
      }
    },
    "weather": { "command": "uv", "args": ["run", "weather.py"] },
    "task-master-ai": { "command": "npx", "args": ["task-master-ai"] }
  }
}
```

## 🧪 Testing Enhanced Features

### Test Multi-Server Discovery
```python
# Test tool discovery
tools = await list_available_mcp_tools()
print(tools)  # Shows all tools from all connected servers
```

### Test Intelligent Routing
```python
# This will automatically route to weather server
response = await chat_with_gemini_enhanced("What's the weather in Tokyo?")

# This will automatically route to task-master server  
response = await chat_with_gemini_enhanced("Create a task to learn Python")
```

### Test Enhanced WhatsApp
```python
# This combines weather + task management automatically
await send_whatsapp_with_gemini_enhanced(
    "+1234567890",
    "Check weather in Paris and create travel planning task"
)
```

## 🎯 How Intelligent Routing Works

1. **Query Analysis**: Gemini analyzes your natural language input
2. **Tool Selection**: Function calling identifies relevant MCP tools
3. **Multi-Tool Execution**: Can call multiple tools in sequence
4. **Response Synthesis**: Combines results into coherent response
5. **Natural Output**: Returns human-friendly response

### Example Flow:
```
User: "Weather in NYC and create task for umbrella shopping"

1. Gemini identifies two actions needed:
   - Weather query → Selects weather_get_forecast
   - Task creation → Selects task_master_add_task

2. Executes both tools:
   - Calls weather server with NYC coordinates
   - Calls task-master with umbrella task

3. Synthesizes response:
   "🌧️ NYC: 15°C, rain expected
   ✅ Task created: 'Buy umbrella' 
   Good thinking ahead!"
```

## 🚀 Advanced Features

### Custom MCP Server Integration
Add your own MCP servers to the configuration:

```python
MCP_SERVERS = {
    "your-custom-server": {
        "command": "python",
        "args": ["your_server.py"],
        "description": "Your custom functionality"
    }
}
```

### Dynamic Tool Loading
Tools are discovered automatically when servers start, making the system self-configuring and expandable.

### Error Handling & Fallbacks
- If a specific MCP server is unavailable, Gemini provides graceful fallbacks
- Connection failures are handled transparently
- Tool discovery continues to work even if some servers are offline

## 📊 Performance & Scalability

- **Concurrent MCP Connections**: Multiple servers run simultaneously
- **Async Tool Execution**: Non-blocking tool calls for better performance  
- **Intelligent Caching**: Tool discovery results are cached for efficiency
- **Resource Management**: Automatic cleanup of server connections

## 🔒 Security Features

- **Environment Variable Protection**: API keys secured in environment
- **Server Isolation**: Each MCP server runs in isolation
- **Input Validation**: All tool inputs are validated before execution
- **Error Sanitization**: Sensitive information filtered from error messages

## 🎉 What You Can Do Now

### Via WhatsApp:
- **"Weather forecast for this weekend in Berlin"**
- **"Add a task to plan vacation itinerary"**  
- **"Create reminders for important meetings"**
- **"Check weather and create outdoor activity tasks"**

### Via VS Code:
- Use enhanced chat with multi-server capabilities
- Discover and call tools from any connected MCP server
- Build complex workflows combining multiple services
- Monitor status of all connected services

## 🚀 Future Enhancements

- **Voice Integration**: Voice messages through WhatsApp
- **Calendar Integration**: MCP server for calendar management
- **Email Integration**: MCP server for email operations
- **Custom Workflows**: Chain multiple MCP operations
- **Multi-Language Support**: Responses in multiple languages

---

**🎯 This enhanced system transforms Gemini from a simple chatbot into an intelligent orchestrator that can seamlessly control multiple specialized services through natural language!**

Happy coding with your enhanced multi-server MCP system! 🚀
