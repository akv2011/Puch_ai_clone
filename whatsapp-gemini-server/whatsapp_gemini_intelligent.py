#!/usr/bin/env python3
"""
Enhanced WhatsApp-Gemini MCP Server with Intelligent Routing
Features:
- Smart query analysis and server routing
- Fallback mechanisms when servers fail
- Enhanced error handling and recovery
- Dynamic server discovery and management
"""

import os
import logging
import asyncio
import json
from typing import Any, Optional, Dict, List, Tuple
import httpx
from google import genai
from google.genai import types
from twilio.rest import Client
from mcp.server.fastmcp import FastMCP
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv
from flask import Flask, request
import threading
import re
from enum import Enum
from dataclasses import dataclass

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("whatsapp-gemini-intelligent")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

class ServerStatus(Enum):
    CONNECTED = "connected"
    CONNECTING = "connecting"
    DISCONNECTED = "disconnected"
    ERROR = "error"

@dataclass
class MCPServerConfig:
    name: str
    command: str
    args: List[str]
    env: Dict[str, str]
    description: str
    capabilities: List[str]
    priority: int = 1
    status: ServerStatus = ServerStatus.DISCONNECTED

# Enhanced MCP Server Configurations with intelligent routing
MCP_SERVERS = {
    "weather": MCPServerConfig(
        name="weather",
        command="C:\\Users\\arunk\\.local\\bin\\uv.exe",
        args=[
            "--directory",
            "c:\\Users\\arunk\\Puch_ai_clone\\weather-server",
            "run",
            "weather.py"
        ],
        env={},
        description="Weather forecasts, alerts, and climate information",
        capabilities=["weather", "forecast", "temperature", "climate", "rain", "sunny", "cloudy", "storm", "wind"],
        priority=2
    ),
    "task-master": MCPServerConfig(
        name="task-master",
        command="npx",
        args=["-y", "--package=task-master-ai", "task-master-ai"],
        env={
            "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", ""),
            "PERPLEXITY_API_KEY": os.getenv("PERPLEXITY_API_KEY", ""),
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
            "GOOGLE_API_KEY": GEMINI_API_KEY
        },
        description="Task management, project planning, and productivity",
        capabilities=["task", "todo", "project", "reminder", "schedule", "planning", "organize", "productivity"],
        priority=1
    )
}

# Initialize clients
twilio_client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    logger.info("Twilio client initialized successfully")

gemini_client = None
if GEMINI_API_KEY:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    logger.info("Gemini API configured successfully")

class IntelligentMCPManager:
    """Enhanced MCP manager with intelligent routing and fallback mechanisms"""
    
    def __init__(self):
        self.servers = {}
        self.tools = {}
        self.sessions = {}
        
        # Query analysis patterns
        self.capability_patterns = {
            "weather": [
                r"\bweather\b", r"\btemperature\b", r"\bforecast\b", r"\bclimate\b",
                r"\brain\b", r"\bsunny\b", r"\bcloudy\b", r"\bstorm\b", r"\bwind\b",
                r"\bhot\b", r"\bcold\b", r"\bdegree\b", r"\bcelsius\b", r"\bfahrenheit\b"
            ],
            "task": [
                r"\btask\b", r"\btodo\b", r"\bremind\b", r"\bschedule\b", r"\bplan\b",
                r"\bproject\b", r"\borganiz\b", r"\bcreate.*task\b", r"\badd.*task\b",
                r"\bdeadline\b", r"\bpriority\b", r"\bproductivity\b"
            ],
            "whatsapp": [
                r"\bsend\b", r"\bmessage\b", r"\bwhatsapp\b", r"\bchat\b", r"\btext\b",
                r"\bcommunicat\b", r"\bnotify\b"
            ]
        }
    
    async def connect_to_server(self, server_name: str, config: MCPServerConfig) -> bool:
        """Connect to an MCP server with enhanced error handling"""
        config.status = ServerStatus.CONNECTING
        
        try:
            logger.info(f"Connecting to MCP server: {server_name}")
            
            server_params = StdioServerParameters(
                command=config.command,
                args=config.args,
                env=config.env,
                cwd=None
            )
            
            # Start server connection with timeout
            read, write = await asyncio.wait_for(
                stdio_client(server_params).__aenter__(),
                timeout=30.0
            )
            
            session = await ClientSession(read, write).__aenter__()
            await session.initialize()
            
            # Discover tools
            mcp_tools = await session.list_tools()
            
            # Store server info
            self.servers[server_name] = config
            self.sessions[server_name] = {
                "session": session,
                "read": read,
                "write": write,
                "config": config
            }
            
            # Register tools with enhanced metadata
            for tool in mcp_tools.tools:
                tool_name = f"{server_name}_{tool.name}"
                self.tools[tool_name] = {
                    "original_name": tool.name,
                    "description": f"[{server_name.upper()}] {tool.description}",
                    "server": server_name,
                    "schema": tool.inputSchema,
                    "session": session,
                    "capabilities": config.capabilities,
                    "priority": config.priority
                }
            
            config.status = ServerStatus.CONNECTED
            logger.info(f"✅ Connected to {server_name} - {len(mcp_tools.tools)} tools available")
            return True
            
        except asyncio.TimeoutError:
            config.status = ServerStatus.ERROR
            logger.error(f"❌ Timeout connecting to {server_name}")
            return False
        except Exception as e:
            config.status = ServerStatus.ERROR
            logger.error(f"❌ Failed to connect to {server_name}: {e}")
            return False
    
    def analyze_query_intent(self, query: str) -> List[Tuple[str, float]]:
        """
        Analyze user query and return ranked server capabilities
        Returns list of (capability, confidence_score) tuples
        """
        query_lower = query.lower()
        scores = {}
        
        for capability, patterns in self.capability_patterns.items():
            score = 0.0
            
            for pattern in patterns:
                matches = len(re.findall(pattern, query_lower))
                score += matches * 1.0
            
            # Boost score if multiple related keywords found
            if score > 1:
                score *= 1.5
                
            if score > 0:
                scores[capability] = score
        
        # Sort by confidence
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        logger.info(f"Query intent analysis for '{query}': {ranked}")
        return ranked
    
    def get_best_servers_for_query(self, query: str) -> List[str]:
        """Get the best servers to handle a query, ordered by preference"""
        intent_scores = self.analyze_query_intent(query)
        
        if not intent_scores:
            return []
        
        server_candidates = []
        used_servers = set()
        
        # Find servers that match the identified intents
        for capability, confidence in intent_scores:
            for server_name, config in self.servers.items():
                if (config.status == ServerStatus.CONNECTED and 
                    capability in [cap.lower() for cap in config.capabilities] and
                    server_name not in used_servers):
                    
                    server_candidates.append((server_name, confidence * config.priority))
                    used_servers.add(server_name)
        
        # Sort by combined score
        server_candidates.sort(key=lambda x: x[1], reverse=True)
        return [server for server, score in server_candidates]
    
    async def route_query_intelligently(self, query: str, context: Optional[str] = None) -> str:
        """
        Route query to the most appropriate server with fallback mechanisms
        """
        try:
            # Get best servers for this query
            best_servers = self.get_best_servers_for_query(query)
            
            if not best_servers:
                logger.info("No specific server match, using direct Gemini response")
                return await self.get_direct_gemini_response(query, context)
            
            # Try servers in order of preference
            for server_name in best_servers:
                try:
                    logger.info(f"🎯 Trying server: {server_name}")
                    result = await self.try_server_with_gemini(server_name, query, context)
                    
                    if result and not result.startswith("❌") and "UNABLE_TO_HANDLE" not in result:
                        logger.info(f"✅ Successfully handled by {server_name}")
                        return result
                    else:
                        logger.warning(f"⚠️ Server {server_name} couldn't handle query, trying next...")
                        
                except Exception as e:
                    logger.error(f"❌ Error with server {server_name}: {e}")
                    continue
            
            # All specific servers failed, use direct Gemini
            logger.info("🔄 Falling back to direct Gemini response")
            fallback_context = f"Note: I tried to use specialized tools for this query but they weren't available. Providing general assistance instead.\n\n{context or ''}"
            return await self.get_direct_gemini_response(query, fallback_context)
            
        except Exception as e:
            logger.error(f"Error in intelligent routing: {e}")
            return f"❌ I encountered an error while processing your request. Please try again or rephrase your question."
    
    async def try_server_with_gemini(self, server_name: str, query: str, context: Optional[str] = None) -> str:
        """Try to handle query with a specific server using Gemini function calling"""
        try:
            # Get tools for this server only
            server_tools = []
            for tool_name, tool_info in self.tools.items():
                if tool_info["server"] == server_name:
                    parameters = {
                        k: v for k, v in tool_info["schema"].items()
                        if k not in ["additionalProperties", "$schema"]
                    }
                    
                    function_declaration = {
                        "name": tool_name,
                        "description": tool_info["description"],
                        "parameters": parameters
                    }
                    
                    server_tools.append(types.Tool(function_declarations=[function_declaration]))
            
            if not server_tools:
                return "❌ No tools available for this server"
            
            # Enhanced prompt with context
            base_prompt = query
            if context:
                base_prompt = f"Context: {context}\n\nUser query: {query}"
            
            server_prompt = f"""
You are an AI assistant with access to {server_name} server tools. Your task is to help the user with their query.

IMPORTANT INSTRUCTIONS:
1. If the query matches your available tools, use them to provide accurate information
2. If the query doesn't match your tools or capabilities, respond EXACTLY with: "❌ UNABLE_TO_HANDLE"
3. Always provide natural, helpful responses when you can assist
4. Be concise but informative

Available capabilities: {', '.join(self.servers[server_name].capabilities)}

User query: {base_prompt}
"""
            
            # Call Gemini with server-specific tools
            response = gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=server_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    tools=server_tools,
                ),
            )
            
            # Handle function calls
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        function_call = part.function_call
                        tool_name = function_call.name
                        arguments = dict(function_call.args) if function_call.args else {}
                        
                        logger.info(f"🔧 Calling {tool_name} with arguments: {arguments}")
                        
                        # Execute the tool
                        tool_result = await self.call_tool(tool_name, arguments)
                        
                        # Get natural language response
                        final_prompt = f"""
User asked: {query}
Tool executed: {tool_name}
Tool result: {tool_result}

Please provide a natural, helpful response to the user based on this information.
Make it conversational and informative.
"""
                        
                        final_response = gemini_client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=final_prompt,
                            config=types.GenerateContentConfig(temperature=0.3)
                        )
                        
                        return final_response.text if final_response.text else str(tool_result)
            
            # Return direct response if no function calls
            return response.text if response.text else "❌ UNABLE_TO_HANDLE"
            
        except Exception as e:
            logger.error(f"Error trying server {server_name}: {e}")
            return f"❌ Error with {server_name}: {str(e)}"
    
    async def call_tool(self, tool_name: str, arguments: Dict) -> Any:
        """Call a specific MCP tool with enhanced error handling"""
        try:
            if tool_name not in self.tools:
                return f"❌ Tool '{tool_name}' not found"
            
            tool_info = self.tools[tool_name]
            session = tool_info["session"]
            original_name = tool_info["original_name"]
            
            logger.info(f"🛠️ Executing {original_name} with args: {arguments}")
            
            result = await session.call_tool(original_name, arguments=arguments)
            
            if result.content:
                return result.content[0].text
            else:
                return "Tool executed successfully but returned no content"
                
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return f"❌ Tool execution failed: {str(e)}"
    
    async def get_direct_gemini_response(self, query: str, context: Optional[str] = None) -> str:
        """Get direct response from Gemini without MCP tools"""
        try:
            prompt = query
            if context:
                prompt = f"{context}\n\nUser query: {query}"
            
            response = gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=1000
                )
            )
            
            return response.text if response.text else "I couldn't generate a response to your query."
            
        except Exception as e:
            logger.error(f"Error getting direct Gemini response: {e}")
            return f"❌ Error generating AI response: {str(e)}"
    
    def get_tools_for_gemini(self) -> List[types.Tool]:
        """Convert all MCP tools to Gemini function format"""
        gemini_tools = []
        
        for tool_name, tool_info in self.tools.items():
            parameters = {
                k: v for k, v in tool_info["schema"].items()
                if k not in ["additionalProperties", "$schema"]
            }
            
            function_declaration = {
                "name": tool_name,
                "description": tool_info["description"],
                "parameters": parameters
            }
            
            gemini_tools.append(types.Tool(function_declarations=[function_declaration]))
        
        return gemini_tools

# Initialize the intelligent MCP manager
intelligent_manager = IntelligentMCPManager()

async def initialize_intelligent_connections():
    """Initialize all MCP server connections with intelligent management"""
    logger.info("🚀 Starting intelligent MCP server connections...")
    
    connection_tasks = []
    for server_name, config in MCP_SERVERS.items():
        task = intelligent_manager.connect_to_server(server_name, config)
        connection_tasks.append(task)
    
    # Connect to all servers concurrently
    results = await asyncio.gather(*connection_tasks, return_exceptions=True)
    
    connected_count = sum(1 for result in results if result is True)
    total_servers = len(MCP_SERVERS)
    
    logger.info(f"📊 Connected to {connected_count}/{total_servers} MCP servers")
    logger.info(f"🛠️ Total tools available: {len(intelligent_manager.tools)}")
    
    return connected_count > 0

def send_whatsapp_message(to_number: str, message: str) -> dict:
    """Send WhatsApp message with enhanced error handling"""
    try:
        if not twilio_client:
            return {"success": False, "error": "Twilio not configured"}
        
        # Clean phone number
        clean_number = to_number.replace("whatsapp:", "").strip()
        if not clean_number.startswith("+"):
            clean_number = f"+{clean_number}"
        
        whatsapp_number = f"whatsapp:{clean_number}"
        
        logger.info(f"📱 Sending WhatsApp message to {whatsapp_number}")
        
        message_instance = twilio_client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=whatsapp_number
        )
        
        logger.info(f"✅ Message sent successfully: {message_instance.sid}")
        return {
            "success": True,
            "message_sid": message_instance.sid,
            "to": whatsapp_number
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to send WhatsApp message: {e}")
        return {"success": False, "error": str(e)}

# Enhanced MCP Tools with intelligent routing
@mcp.tool()
async def send_whatsapp_with_intelligent_ai(phone_number: str, user_message: str, context: Optional[str] = None) -> str:
    """Send WhatsApp message after processing through Gemini with intelligent MCP routing."""
    try:
        # Use intelligent routing for AI response
        ai_response = await intelligent_manager.route_query_intelligently(user_message, context)
        
        # Send via WhatsApp
        result = send_whatsapp_message(phone_number, ai_response)
        
        if result["success"]:
            return f"✅ Sent intelligent AI response to {phone_number}\\nMessage: {ai_response[:100]}..."
        else:
            return f"❌ Failed to send WhatsApp: {result['error']}"
            
    except Exception as e:
        logger.error(f"Error in intelligent WhatsApp send: {e}")
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def chat_with_intelligent_gemini(message: str, context: Optional[str] = None) -> str:
    """Chat with Gemini using intelligent MCP routing for enhanced capabilities."""
    try:
        return await intelligent_manager.route_query_intelligently(message, context)
    except Exception as e:
        logger.error(f"Error in intelligent chat: {e}")
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def get_intelligent_server_status() -> str:
    """Get detailed status of all MCP servers and intelligent routing capabilities."""
    try:
        connected_servers = sum(1 for config in MCP_SERVERS.values() if config.status == ServerStatus.CONNECTED)
        total_tools = len(intelligent_manager.tools)
        
        status_report = f"🧠 Intelligent MCP System Status\\n"
        status_report += f"📊 Servers: {connected_servers}/{len(MCP_SERVERS)} connected\\n"
        status_report += f"🛠️ Total tools: {total_tools}\\n\\n"
        
        for server_name, config in MCP_SERVERS.items():
            status_emoji = "✅" if config.status == ServerStatus.CONNECTED else "❌"
            server_tools = [t for t in intelligent_manager.tools.values() if t["server"] == server_name]
            
            status_report += f"{status_emoji} **{server_name.upper()}** ({config.status.value})\\n"
            status_report += f"   📝 {config.description}\\n"
            status_report += f"   🎯 Capabilities: {', '.join(config.capabilities)}\\n"
            status_report += f"   🛠️ Tools: {len(server_tools)}\\n\\n"
        
        # Add routing intelligence info
        status_report += "🧠 **Intelligent Routing Features:**\\n"
        status_report += "   • Automatic query analysis and intent detection\\n"
        status_report += "   • Smart server selection based on capabilities\\n"
        status_report += "   • Fallback mechanisms when servers fail\\n"
        status_report += "   • Enhanced error handling and recovery\\n"
        
        return status_report
        
    except Exception as e:
        return f"❌ Error getting status: {str(e)}"

@mcp.tool()
async def list_intelligent_capabilities() -> str:
    """List all available MCP capabilities and intelligent routing features."""
    try:
        result = "🧠 **Intelligent MCP System Capabilities**\\n\\n"
        
        # Server capabilities
        for server_name, config in MCP_SERVERS.items():
            if config.status == ServerStatus.CONNECTED:
                result += f"✅ **{server_name.upper()} SERVER**\\n"
                result += f"   🎯 Handles: {', '.join(config.capabilities)}\\n"
                
                server_tools = [t for t in intelligent_manager.tools.values() if t["server"] == server_name]
                for tool in server_tools:
                    result += f"   🛠️ {tool['original_name']}: {tool['description']}\\n"
                result += "\\n"
        
        # Routing intelligence
        result += "🧠 **Intelligent Routing Features:**\\n"
        result += "• **Query Analysis**: Automatically detects user intent\\n"
        result += "• **Smart Routing**: Routes queries to best available server\\n"
        result += "• **Fallback System**: Uses alternative servers when needed\\n"
        result += "• **Error Recovery**: Graceful handling of server failures\\n"
        result += "• **Context Preservation**: Maintains conversation context\\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error listing capabilities: {str(e)}"

@mcp.tool()
async def send_whatsapp_direct(phone_number: str, message: str) -> str:
    """Send direct WhatsApp message without AI processing."""
    try:
        result = send_whatsapp_message(phone_number, message)
        
        if result["success"]:
            return f"✅ Direct message sent to {phone_number}\\nSID: {result['message_sid']}"
        else:
            return f"❌ Failed to send: {result['error']}"
            
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Flask webhook with intelligent processing
webhook_app = Flask(__name__)

@webhook_app.route('/webhook', methods=['POST'])
def intelligent_whatsapp_webhook():
    """Enhanced webhook with intelligent MCP routing"""
    try:
        incoming_msg = request.values.get('Body', '').strip()
        from_number = request.values.get('From', '')
        
        logger.info(f"📨 Received WhatsApp message from {from_number}: {incoming_msg}")
        
        if not incoming_msg:
            return "OK", 200
        
        clean_number = from_number.replace("whatsapp:", "").strip()
        
        async def process_with_intelligence():
            try:
                # Use intelligent routing for response
                context = "You are a helpful WhatsApp assistant with access to various specialized tools. Keep responses concise and friendly."
                ai_response = await intelligent_manager.route_query_intelligently(incoming_msg, context)
                
                if ai_response:
                    result = send_whatsapp_message(clean_number, f"🤖 {ai_response}")
                    
                    if result.get("success"):
                        logger.info(f"✅ Intelligent response sent to {clean_number}")
                    else:
                        logger.error(f"❌ Failed to send response: {result.get('error')}")
            
            except Exception as e:
                logger.error(f"❌ Error in intelligent processing: {e}")
                try:
                    send_whatsapp_message(clean_number, "Sorry, I encountered an error. Please try again.")
                except:
                    pass
        
        # Process asynchronously
        asyncio.create_task(process_with_intelligence())
        
        return "OK", 200
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        return "Error", 500

@mcp.tool()
async def start_intelligent_webhook_server(port: int = 5000) -> str:
    """Start enhanced webhook server with intelligent processing."""
    try:
        def run_webhook():
            webhook_app.run(host='0.0.0.0', port=port, debug=False)
        
        thread = threading.Thread(target=run_webhook, daemon=True)
        thread.start()
        
        return f"✅ Intelligent webhook server started on port {port}\\nIncoming messages will be processed with smart MCP routing!"
        
    except Exception as e:
        return f"❌ Error starting webhook server: {str(e)}"

@mcp.tool()
async def setup_intelligent_webhook_instructions() -> str:
    """Get setup instructions for the intelligent WhatsApp webhook."""
    return f"""
🧠 **Enhanced WhatsApp-Gemini MCP Webhook Setup**

**Features:**
✅ Intelligent query analysis and routing
✅ Automatic server selection based on content
✅ Fallback mechanisms for reliability
✅ Enhanced error handling

**Setup Steps:**

1. **Start the webhook server:**
   Use the 'start_intelligent_webhook_server' tool

2. **Configure Twilio webhook:**
   - Go to Twilio Console → WhatsApp → Sandbox
   - Set webhook URL: http://your-server:5000/webhook
   - Set HTTP method: POST

3. **Test the system:**
   - Send weather queries: "What's the weather in Tokyo?"
   - Send task queries: "Create a task to learn Python"
   - Send general queries: "Tell me a joke"

**Intelligence Features:**
🧠 **Smart Routing**: Automatically detects if you're asking about weather, tasks, or general questions
🔄 **Fallback System**: If weather server is down, falls back to general AI
⚡ **Multi-Tool Support**: Can handle complex queries requiring multiple tools
🛠️ **Error Recovery**: Graceful handling of server failures

**Available Capabilities:**
• Weather forecasts and alerts
• Task management and planning  
• General AI assistance
• WhatsApp integration
• And more as you add MCP servers!

Connected servers: {list(MCP_SERVERS.keys())}
Total tools: {len(intelligent_manager.tools)}

🎉 Your intelligent MCP system is ready to handle diverse queries smartly!
"""

# Startup function
async def startup_intelligent_system():
    """Initialize the intelligent MCP system"""
    logger.info("🧠 Starting Intelligent WhatsApp-Gemini MCP System")
    await initialize_intelligent_connections()

if __name__ == "__main__":
    # Initialize the intelligent system
    asyncio.run(startup_intelligent_system())
    
    # Start the MCP server
    logger.info("🚀 Starting intelligent MCP server...")
    mcp.run(transport='stdio')
