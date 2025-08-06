import os
import logging
import asyncio
import json
from typing import Any, Optional, Dict, List
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
import subprocess

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("whatsapp-gemini-enhanced")

# Configure logging to stderr (important for MCP servers)
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

# MCP Server Configurations - Add your other MCP servers here
MCP_SERVERS = {
    "weather": {
        "command": "C:\\Users\\arunk\\.local\\bin\\uv.exe",
        "args": [
            "--directory",
            "c:\\Users\\arunk\\Puch_ai_clone\\weather-server",
            "run",
            "weather.py"
        ],
        "description": "Weather forecasts and alerts"
    },
    "task-master": {
        "command": "npx",
        "args": ["-y", "--package=task-master-ai", "task-master-ai"],
        "env": {
            "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
            "PERPLEXITY_API_KEY": os.getenv("PERPLEXITY_API_KEY"),
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
            "GOOGLE_API_KEY": GEMINI_API_KEY
        },
        "description": "Task management and project planning"
    }
}

# Initialize services
twilio_client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    logger.info("Twilio client initialized successfully")
else:
    logger.warning("Twilio credentials not found. WhatsApp sending will not work.")

gemini_client = None
if GEMINI_API_KEY:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    logger.info("Gemini API configured successfully")
else:
    logger.warning("Gemini API key not found. AI responses will not work.")

# Global storage for MCP tools and sessions
available_tools = {}
active_sessions = {}

class MCPClientManager:
    """Manages connections to multiple MCP servers"""
    
    def __init__(self):
        self.servers = {}
        self.tools = {}
        
    async def connect_to_server(self, server_name: str, config: Dict) -> bool:
        """Connect to an MCP server and discover its tools"""
        try:
            logger.info(f"Connecting to MCP server: {server_name}")
            
            # Create server parameters
            server_params = StdioServerParameters(
                command=config["command"],
                args=config.get("args", []),
                env=config.get("env", {}),
                cwd=config.get("cwd")
            )
            
            # Start the server connection
            read, write = await stdio_client(server_params).__aenter__()
            session = await ClientSession(read, write).__aenter__()
            await session.initialize()
            
            # Discover tools
            mcp_tools = await session.list_tools()
            
            # Store session and tools
            self.servers[server_name] = {
                "session": session,
                "read": read,
                "write": write,
                "config": config
            }
            
            # Convert tools to Gemini format
            server_tools = {}
            for tool in mcp_tools.tools:
                tool_name = f"{server_name}_{tool.name}"
                server_tools[tool_name] = {
                    "original_name": tool.name,
                    "description": f"[{server_name.upper()}] {tool.description}",
                    "server": server_name,
                    "schema": tool.inputSchema,
                    "session": session
                }
            
            self.tools.update(server_tools)
            logger.info(f"Connected to {server_name} with {len(server_tools)} tools")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to {server_name}: {e}")
            return False
    
    async def call_tool(self, tool_name: str, arguments: Dict) -> Any:
        """Call a tool on the appropriate MCP server"""
        try:
            if tool_name not in self.tools:
                return f"❌ Tool '{tool_name}' not found"
            
            tool_info = self.tools[tool_name]
            session = tool_info["session"]
            original_name = tool_info["original_name"]
            
            logger.info(f"Calling tool {original_name} on {tool_info['server']} with args: {arguments}")
            
            result = await session.call_tool(original_name, arguments=arguments)
            return result.content[0].text if result.content else "No result"
            
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return f"❌ Error calling tool: {str(e)}"
    
    def get_tools_for_gemini(self) -> List[types.Tool]:
        """Convert MCP tools to Gemini function format"""
        gemini_tools = []
        
        for tool_name, tool_info in self.tools.items():
            # Clean up the schema for Gemini
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

# Initialize MCP client manager
mcp_manager = MCPClientManager()

async def initialize_mcp_connections():
    """Initialize connections to all configured MCP servers"""
    logger.info("Initializing MCP server connections...")
    
    for server_name, config in MCP_SERVERS.items():
        await mcp_manager.connect_to_server(server_name, config)
    
    logger.info(f"MCP initialization complete. Available tools: {list(mcp_manager.tools.keys())}")

async def get_gemini_response_with_tools(message: str, context: Optional[str] = None) -> str:
    """Get response from Gemini LLM with access to MCP tools."""
    try:
        if not gemini_client:
            return "❌ Gemini API key not configured. Please set GEMINI_API_KEY environment variable."
        
        # Prepare the prompt with context if provided
        prompt = message
        if context:
            prompt = f"Context: {context}\n\nUser message: {message}"
        
        # Get available tools for Gemini
        tools = mcp_manager.get_tools_for_gemini()
        
        logger.info(f"Sending prompt to Gemini with {len(tools)} available tools: {prompt[:100]}...")
        
        # Generate content with tools
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                tools=tools if tools else None,
            ),
        )
        
        # Check if Gemini wants to call a function
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    function_call = part.function_call
                    tool_name = function_call.name
                    arguments = dict(function_call.args) if function_call.args else {}
                    
                    logger.info(f"Gemini wants to call tool: {tool_name} with args: {arguments}")
                    
                    # Call the MCP tool
                    tool_result = await mcp_manager.call_tool(tool_name, arguments)
                    
                    # Send the result back to Gemini for a final response
                    final_prompt = f"""
                    Original user question: {message}
                    
                    Tool used: {tool_name}
                    Tool result: {tool_result}
                    
                    Please provide a helpful response to the user based on this information.
                    """
                    
                    final_response = gemini_client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=final_prompt
                    )
                    
                    return final_response.text if final_response.text else f"Tool result: {tool_result}"
        
        # Regular text response
        if response.text:
            logger.info("Received text response from Gemini")
            return response.text
        else:
            return "❌ No response received from Gemini"
            
    except Exception as e:
        logger.error(f"Error getting Gemini response: {e}")
        return f"❌ Error getting AI response: {str(e)}"

async def get_gemini_response(message: str, context: Optional[str] = None) -> str:
    """Get response from Gemini LLM (legacy function for compatibility)."""
    return await get_gemini_response_with_tools(message, context)

def send_whatsapp_message(to_number: str, message: str) -> dict:
    """Send a WhatsApp message using Twilio."""
    try:
        if not twilio_client:
            return {
                "success": False,
                "error": "Twilio not configured. Please set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN."
            }
        
        # Ensure the number is in WhatsApp format
        if not to_number.startswith("whatsapp:"):
            to_number = f"whatsapp:{to_number}"
        
        logger.info(f"Sending WhatsApp message to {to_number}")
        message_obj = twilio_client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=to_number
        )
        
        logger.info(f"Message sent successfully. SID: {message_obj.sid}")
        return {
            "success": True,
            "message_sid": message_obj.sid,
            "status": message_obj.status
        }
        
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def send_whatsapp_with_gemini_enhanced(phone_number: str, user_message: str, context: Optional[str] = None) -> str:
    """Send a message to WhatsApp after processing it through Gemini LLM with access to all MCP tools.

    Args:
        phone_number: WhatsApp phone number (e.g., +1234567890)
        user_message: The message to process with Gemini
        context: Optional context to provide to Gemini for better responses
    """
    try:
        # Get AI response from Gemini with tools
        logger.info(f"Processing message with Gemini and MCP tools: {user_message[:50]}...")
        ai_response = await get_gemini_response_with_tools(user_message, context)
        
        # Send the AI response via WhatsApp
        result = send_whatsapp_message(phone_number, ai_response)
        
        if result["success"]:
            return f"""✅ Enhanced message sent successfully!
            
📱 To: {phone_number}
🤖 AI Response (with MCP tools): {ai_response[:200]}{'...' if len(ai_response) > 200 else ''}
📋 Message SID: {result.get('message_sid')}
📊 Status: {result.get('status')}
🛠️ Available tools: {len(mcp_manager.tools)}"""
        else:
            return f"❌ Failed to send WhatsApp message: {result['error']}"
            
    except Exception as e:
        logger.error(f"Error in send_whatsapp_with_gemini_enhanced: {e}")
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def chat_with_gemini_enhanced(message: str, context: Optional[str] = None) -> str:
    """Chat with Gemini LLM with access to all MCP tools without sending to WhatsApp.

    Args:
        message: Your message or question for Gemini
        context: Optional context to provide for better responses
    """
    return await get_gemini_response_with_tools(message, context)

@mcp.tool()
async def list_available_mcp_tools() -> str:
    """List all available MCP tools from connected servers."""
    if not mcp_manager.tools:
        return "❌ No MCP tools available. Servers may not be connected."
    
    tool_list = []
    servers = set()
    
    for tool_name, tool_info in mcp_manager.tools.items():
        servers.add(tool_info['server'])
        tool_list.append(f"🛠️ {tool_name}: {tool_info['description']}")
    
    result = f"📋 Available MCP Tools ({len(mcp_manager.tools)} total from {len(servers)} servers):\n\n"
    result += "\n".join(tool_list)
    result += f"\n\n🖥️ Connected servers: {', '.join(servers)}"
    
    return result

@mcp.tool()
async def call_mcp_tool_directly(tool_name: str, arguments: str) -> str:
    """Call an MCP tool directly with JSON arguments.

    Args:
        tool_name: Name of the MCP tool to call
        arguments: JSON string of arguments for the tool
    """
    try:
        # Parse arguments
        args = json.loads(arguments) if arguments else {}
        
        # Call the tool
        result = await mcp_manager.call_tool(tool_name, args)
        
        return f"✅ Tool '{tool_name}' executed successfully:\n\n{result}"
        
    except json.JSONDecodeError:
        return f"❌ Invalid JSON arguments: {arguments}"
    except Exception as e:
        return f"❌ Error calling tool '{tool_name}': {str(e)}"

@mcp.tool()
async def send_whatsapp_with_gemini(phone_number: str, user_message: str, context: Optional[str] = None) -> str:
    """Send a message to WhatsApp after processing it through Gemini LLM (legacy function).

    Args:
        phone_number: WhatsApp phone number (e.g., +1234567890)
        user_message: The message to process with Gemini
        context: Optional context to provide to Gemini for better responses
    """
    return await send_whatsapp_with_gemini_enhanced(phone_number, user_message, context)

@mcp.tool()
async def chat_with_gemini(message: str, context: Optional[str] = None) -> str:
    """Chat with Gemini LLM without sending to WhatsApp (legacy function).

    Args:
        message: Your message or question for Gemini
        context: Optional context to provide for better responses
    """
    return await chat_with_gemini_enhanced(message, context)

@mcp.tool()
async def send_whatsapp_direct(phone_number: str, message: str) -> str:
    """Send a direct message to WhatsApp without AI processing.

    Args:
        phone_number: WhatsApp phone number (e.g., +1234567890)
        message: The message to send directly
    """
    result = send_whatsapp_message(phone_number, message)
    
    if result["success"]:
        return f"""✅ Direct message sent!
        
📱 To: {phone_number}
💬 Message: {message}
📋 Message SID: {result.get('message_sid')}
📊 Status: {result.get('status')}"""
    else:
        return f"❌ Failed to send message: {result['error']}"

@mcp.tool()
async def get_server_status() -> str:
    """Check the status of all configured services."""
    status = []
    
    # Check Gemini API
    if GEMINI_API_KEY:
        try:
            test_response = gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents="Say hello"
            )
            if test_response.text:
                status.append("✅ Gemini LLM: Connected and working")
            else:
                status.append("⚠️ Gemini LLM: Connected but not responding properly")
        except Exception as e:
            status.append(f"❌ Gemini LLM: Error - {str(e)}")
    else:
        status.append("❌ Gemini LLM: API key not configured")
    
    # Check Twilio
    if twilio_client:
        try:
            account = twilio_client.api.accounts(TWILIO_ACCOUNT_SID).fetch()
            status.append(f"✅ Twilio WhatsApp: Connected (Account: {account.friendly_name})")
        except Exception as e:
            status.append(f"❌ Twilio WhatsApp: Error - {str(e)}")
    else:
        status.append("❌ Twilio WhatsApp: Credentials not configured")
    
    # Check MCP servers
    status.append(f"\n🖥️ MCP Servers Status:")
    for server_name, config in MCP_SERVERS.items():
        if server_name in mcp_manager.servers:
            server_tools = [name for name, info in mcp_manager.tools.items() if info['server'] == server_name]
            status.append(f"✅ {server_name}: Connected ({len(server_tools)} tools)")
        else:
            status.append(f"❌ {server_name}: Not connected")
    
    status.append(f"\n🛠️ Total MCP Tools Available: {len(mcp_manager.tools)}")
    
    return "\n".join(status)

# Flask app for webhook handling
webhook_app = Flask(__name__)

@webhook_app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages and auto-reply with Gemini responses (with MCP tools)."""
    try:
        # Get incoming message data from Twilio
        incoming_msg = request.values.get('Body', '').strip()
        from_number = request.values.get('From', '')
        to_number = request.values.get('To', '')
        
        logger.info(f"📨 Received WhatsApp message from {from_number}: {incoming_msg}")
        
        if not incoming_msg:
            return "OK", 200
            
        # Extract phone number for processing
        clean_number = from_number.replace("whatsapp:", "").strip()
        
        # Process with Gemini + MCP tools in a background task
        async def process_message():
            try:
                if not gemini_client:
                    return
                
                # Get AI response with MCP tools
                prompt = f"Context: You are a helpful WhatsApp assistant with access to various tools. Keep responses concise and friendly. If you need weather information, use weather tools. If you need task management, use task-master tools.\n\nUser message: {incoming_msg}"
                
                ai_response = await get_gemini_response_with_tools(prompt)
                
                if ai_response:
                    # Send response back to WhatsApp
                    result = send_whatsapp_message(clean_number, f"🤖 {ai_response}")
                    
                    if result.get("success"):
                        logger.info(f"✅ Successfully sent enhanced reply to {clean_number}")
                    else:
                        logger.error(f"❌ Failed to send WhatsApp: {result.get('error')}")
                        
            except Exception as e:
                logger.error(f"❌ Error in async processing: {str(e)}")
                try:
                    send_whatsapp_message(clean_number, "Sorry, I encountered an error. Please try again.")
                except:
                    pass
        
        # Run async processing
        asyncio.create_task(process_message())
        
        return "OK", 200
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        return "Error", 500

@mcp.tool()
async def start_webhook_server(port: int = 5000) -> str:
    """Start the webhook server to receive incoming WhatsApp messages.
    
    Args:
        port: Port number for the webhook server (default: 5000)
    """
    try:
        def run_webhook():
            webhook_app.run(host='0.0.0.0', port=port, debug=False)
        
        # Start webhook server in a separate thread
        webhook_thread = threading.Thread(target=run_webhook, daemon=True)
        webhook_thread.start()
        
        return f"✅ Enhanced webhook server started on port {port}!\n📡 Your webhook URL: http://localhost:{port}/webhook\n\n🔧 Next steps:\n1. Use ngrok to expose your local server: ngrok http {port}\n2. Copy the ngrok URL\n3. Set it in Twilio Console > WhatsApp > Sandbox > Webhook URL\n\n🛠️ This webhook now has access to {len(mcp_manager.tools)} MCP tools!"
        
    except Exception as e:
        return f"❌ Error starting webhook server: {str(e)}"

@mcp.tool()
async def setup_webhook_instructions() -> str:
    """Get detailed instructions for setting up the WhatsApp webhook."""
    return f"""
🔧 Enhanced WhatsApp Auto-Reply Setup Instructions:

1. **Start the webhook server:**
   Use the start_webhook_server tool or run: start_webhook_server 5000

2. **Install ngrok (if not installed):**
   Download from: https://ngrok.com/download
   Or: choco install ngrok (Windows)

3. **Expose your local server:**
   Open a new terminal and run: ngrok http 5000
   Copy the HTTPS URL (e.g., https://abc123.ngrok.io)

4. **Configure Twilio Webhook:**
   - Go to: https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox
   - In "When a message comes in" field, enter: https://abc123.ngrok.io/webhook
   - Method: POST
   - Click Save

5. **Test the enhanced setup:**
   - Send a message to your Twilio WhatsApp number: +1 415 523 8886
   - Try weather queries like "What's the weather in New York?"
   - Try task management like "Create a task to learn Python"
   - Your messages will be processed by Gemini AI with access to {len(mcp_manager.tools)} MCP tools!

🎉 Once set up, you can have conversations with AI that can use weather, task management, and other tools through WhatsApp!

🛠️ Available MCP Tools: {len(mcp_manager.tools)}
🖥️ Connected Servers: {list(MCP_SERVERS.keys())}
"""

# Startup function to initialize MCP connections
async def startup():
    """Initialize all MCP connections on startup"""
    await initialize_mcp_connections()

if __name__ == "__main__":
    logger.info("Starting Enhanced WhatsApp-Gemini MCP Server")
    
    # Initialize MCP connections
    asyncio.run(startup())
    
    # Start the MCP server
    mcp.run(transport='stdio')
