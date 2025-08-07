# 🔌 How to Add New MCP Servers to Your WhatsApp AI System

This guide shows you how to add any MCP server from GitHub to expand your WhatsApp AI capabilities with new tools and functions.

## 🌟 **Examples of Available MCP Servers**

### **Currently Integrated:**
- ✅ **Financial Datasets** - Stock prices, crypto data, company financials
- ✅ **Weather Forecast** - 8-day weather forecasts, current conditions
- ✅ **Task Master AI** - Task management and productivity tools
- ✅ **WhatsApp Tools** - Message sending and communication

### **Popular MCP Servers You Can Add:**
- 🗄️ **Database connectors** (PostgreSQL, MySQL, SQLite)
- 🔍 **Search engines** (Google, Bing, DuckDuckGo)
- 📁 **File management** (Google Drive, Dropbox, local files)
- 🌐 **Web scraping** and content extraction
- 📊 **Analytics** and data visualization
- 🤖 **AI model integrations** (Claude, GPT, local models)
- 📧 **Email and notifications** (Gmail, Outlook, Slack)

## 📋 **Step-by-Step Guide to Add Any MCP Server**

### **Step 1: Find an MCP Server** 🔍

**Popular Sources:**
- GitHub: Search for `mcp-server` or `model-context-protocol`
- MCP Registry: https://github.com/modelcontextprotocol
- Community lists and awesome-mcp repositories

**Example Searches:**
```bash
# GitHub search examples
site:github.com "mcp server" database
site:github.com "model context protocol" search
site:github.com mcp-server email
```

### **Step 2: Clone the MCP Server** 📦

```bash
# Navigate to your project directory
cd C:\Users\[YOUR_USERNAME]\Puch_ai_clone

# Clone the MCP server repository
git clone https://github.com/[AUTHOR]/[MCP-SERVER-NAME].git

# Example: Financial Datasets Server
git clone https://github.com/ktanaka101/financial-datasets-mcp-server.git financial-datasets-server

# Example: Weather Server  
git clone https://github.com/rossshannon/weekly-weather-mcp.git weather-server-new
```

### **Step 3: Install Dependencies** 🔧

**For Python MCP Servers:**
```bash
cd [MCP-SERVER-DIRECTORY]
pip install -r requirements.txt
# OR
uv add [package-names]
```

**For Node.js MCP Servers:**
```bash
cd [MCP-SERVER-DIRECTORY]
npm install
# OR
npx install [package-names]
```

### **Step 4: Configure API Keys** 🔑

Most MCP servers need API keys or configuration:

1. **Check the server's README** for required API keys
2. **Get API keys** from the respective services
3. **Add to your environment** files

**Example - Financial Server:**
```bash
# Get API key from: https://financialdatasets.ai
FINANCIAL_DATASETS_API_KEY=your_api_key_here
```

**Example - Weather Server:**
```bash
# Get API key from: https://openweathermap.org/api
OPENWEATHER_API_KEY=your_api_key_here
```

### **Step 5: Update MCP Configuration** ⚙️

Add the new server to `.vscode/mcp.json`:

```json
{
  "servers": {
    "your-new-server": {
      "command": "path_to_executable",
      "args": ["path_to_server_script"],
      "env": {
        "API_KEY": "your_api_key_here"
      },
      "type": "stdio"
    }
  }
}
```

**Real Examples:**

**Python MCP Server:**
```json
"financial-datasets": {
  "command": "C:\\Users\\[USERNAME]\\.local\\bin\\uv.exe",
  "args": [
    "--directory",
    "c:\\Users\\[USERNAME]\\Puch_ai_clone\\financial-datasets-server",
    "run",
    "python",
    "server.py"
  ],
  "env": {
    "FINANCIAL_DATASETS_API_KEY": "your_api_key_here"
  },
  "type": "stdio"
}
```

**Node.js MCP Server:**
```json
"task-master-ai": {
  "command": "npx",
  "args": ["-y", "--package=task-master-ai", "task-master-ai"],
  "env": {
    "OPENAI_API_KEY": "your_openai_key_here"
  },
  "type": "stdio"
}
```

### **Step 6: Update WhatsApp Bridge** 🤖

Add the server to your WhatsApp bridge configuration in `whatsapp_mcp_bridge_v2.py`:

```python
MCP_SERVERS = [
    # Existing servers...
    {
        "name": "your-new-server",
        "params": StdioServerParameters(
            command="path_to_executable",
            args=["path_to_server_script"],
            env={"API_KEY": os.getenv("API_KEY", "fallback_value")}
        )
    }
]
```

**Real Example:**
```python
{
    "name": "financial-datasets",
    "params": StdioServerParameters(
        command="C:\\Users\\arunk\\.local\\bin\\uv.exe",
        args=[
            "--directory", 
            "C:\\Users\\arunk\\Puch_ai_clone\\financial-datasets-server",
            "run",
            "python",
            "server.py"
        ],
        env={"FINANCIAL_DATASETS_API_KEY": os.getenv("FINANCIAL_DATASETS_API_KEY")}
    )
}
```

### **Step 7: Test the Integration** 🧪

1. **Restart your WhatsApp bridge:**
```bash
cd whatsapp-gemini-server/production
python whatsapp_mcp_bridge_v2.py
```

2. **Check the logs** for successful tool discovery:
```
✅ Discovered tool: [tool_name] from [server_name]
```

3. **Test via WhatsApp** with queries related to your new server's functionality

## 🎯 **Detailed Examples**

### **Example 1: Adding Financial Data Server**

```bash
# Step 1: Clone
git clone https://github.com/ktanaka101/financial-datasets-mcp-server.git financial-datasets-server

# Step 2: Install
cd financial-datasets-server
uv add requests aiohttp

# Step 3: Get API Key
# Visit: https://financialdatasets.ai
# Copy your API key

# Step 4: Configure
# Add to .vscode/mcp.json and whatsapp_mcp_bridge_v2.py (see above)

# Step 5: Test
# WhatsApp: "Apple stock price"
# WhatsApp: "Bitcoin current price"
```

### **Example 2: Adding Weather Server**

```bash
# Step 1: Clone
git clone https://github.com/rossshannon/weekly-weather-mcp.git weather-server-new

# Step 2: Install
cd weather-server-new
pip install -r requirements.txt

# Step 3: Get API Key
# Visit: https://openweathermap.org/api
# Subscribe to "One Call API 3.0" (free tier)

# Step 4: Configure
# Add OPENWEATHER_API_KEY to configuration files

# Step 5: Test
# WhatsApp: "Weather in Chennai"
# WhatsApp: "Weather forecast for Mumbai this week"
```

## 🔧 **Common Configuration Patterns**

### **Python Servers:**
```json
{
  "command": "python", 
  "args": ["server.py"],
  "env": {"API_KEY": "value"}
}
```

### **Node.js Servers:**
```json
{
  "command": "node",
  "args": ["index.js"],
  "env": {"API_KEY": "value"}
}
```

### **UV-managed Python:**
```json
{
  "command": "C:\\Users\\[USER]\\.local\\bin\\uv.exe",
  "args": ["--directory", "path", "run", "python", "script.py"]
}
```

### **NPX Packages:**
```json
{
  "command": "npx",
  "args": ["-y", "--package=package-name", "command"]
}
```

## 🚨 **Important Notes**

### **Security:**
- ✅ **Always add MCP server directories to `.gitignore`**
- ✅ **Never commit API keys to git**
- ✅ **Use `.env` files and `.example` templates**
- ✅ **Keep sensitive data in environment variables**

### **Performance:**
- ⚡ **More MCP servers = longer discovery time**
- ⚡ **Consider disabling unused servers**
- ⚡ **Monitor API rate limits**

### **Compatibility:**
- 🔍 **Check MCP server documentation**
- 🔍 **Verify Python/Node.js version requirements**
- 🔍 **Test tools individually before integration**

## 📚 **Finding More MCP Servers**

### **GitHub Search Queries:**
```
"model context protocol" OR "mcp server" language:python
"model context protocol" OR "mcp server" language:javascript
mcp-server topic:ai topic:tools
```

### **Popular Categories:**
- **Data & APIs**: Financial, weather, news, social media
- **Productivity**: Calendar, email, task management, notes
- **Development**: Git, databases, deployment, monitoring
- **AI & ML**: Model integrations, vector stores, embeddings
- **Communication**: Slack, Discord, WhatsApp, SMS

## 🎉 **Success Indicators**

When successfully added, you should see:
1. ✅ **Tool discovery logs** in WhatsApp bridge
2. ✅ **Gemini auto-routing** to new tools
3. ✅ **Successful API responses** via WhatsApp
4. ✅ **No authentication errors** in logs

The WhatsApp AI system will automatically discover and use all tools from all configured MCP servers - no manual routing needed! 🤖✨
