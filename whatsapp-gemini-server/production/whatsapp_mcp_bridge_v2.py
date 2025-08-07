#!/usr/bin/env python3
"""
Simplified WhatsApp MCP Bridge using Gemini's Function Calling
Inspired by: https://medium.com/google-cloud/model-context-protocol-mcp-with-google-gemini-2-5-pro-a-deep-dive-full-code-4f5b7c8b7b5c

This approach lets Gemini automatically discover and call all MCP tools without manual routing.
"""

import os
import asyncio
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from twilio.rest import Client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize Gemini client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# Initialize Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

twilio_client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    logger.info("Twilio client initialized")

def send_whatsapp_message(to_number: str, message: str) -> dict:
    """Send WhatsApp message via Twilio"""
    try:
        if not twilio_client:
            return {"success": False, "error": "Twilio not configured"}
        
        if not to_number.startswith("whatsapp:"):
            to_number = f"whatsapp:{to_number}"
        
        # WhatsApp character limit
        if len(message) > 1600:
            message = message[:1597] + "..."
        
        message_obj = twilio_client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=to_number
        )
        
        return {
            "success": True,
            "message_sid": message_obj.sid,
            "status": message_obj.status
        }
    except Exception as e:
        logger.error(f"WhatsApp send error: {e}")
        return {"success": False, "error": str(e)}

# MCP Server configurations
MCP_SERVERS = [
    {
        "name": "weather",
        "params": StdioServerParameters(
            command="C:/Users/arunk/Puch_ai_clone/.venv/Scripts/python.exe",
            args=[
                "C:\\Users\\arunk\\Puch_ai_clone\\weather-server-new\\weather_mcp_server.py"
            ],
            env={"OPENWEATHER_API_KEY": os.getenv("OPENWEATHER_API_KEY", "YOUR_OPENWEATHER_API_KEY_HERE")}
        )
    },
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
            env={"FINANCIAL_DATASETS_API_KEY": os.getenv("FINANCIAL_DATASETS_API_KEY", "714f22c9-a28c-4a13-8e9b-d4876ae1b5c0")}
        )
    }
]

async def get_all_mcp_tools():
    """Discover all tools from all MCP servers"""
    all_tools = []
    
    for server_config in MCP_SERVERS:
        try:
            logger.info(f"🔍 Discovering tools from {server_config['name']} MCP server...")
            
            async with stdio_client(server_config["params"]) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    mcp_tools = await session.list_tools()
                    
                    for tool in mcp_tools.tools:
                        # Convert MCP tool to Gemini function declaration format
                        gemini_tool = types.Tool(
                            function_declarations=[
                                {
                                    "name": tool.name,
                                    "description": tool.description,
                                    "parameters": {
                                        k: v
                                        for k, v in tool.inputSchema.items()
                                        if k not in ["additionalProperties", "$schema"]
                                    },
                                }
                            ]
                        )
                        all_tools.append((gemini_tool, server_config, tool.name))
                        logger.info(f"✅ Discovered tool: {tool.name} from {server_config['name']}")
                        
        except Exception as e:
            logger.error(f"❌ Failed to connect to {server_config['name']}: {e}")
    
    return all_tools

async def execute_mcp_tool(server_config, tool_name, arguments):
    """Execute a specific MCP tool with given arguments"""
    try:
        logger.info(f"🛠️ Executing {tool_name} on {server_config['name']} with args: {arguments}")
        
        async with stdio_client(server_config["params"]) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments=arguments)
                
                if hasattr(result, 'content') and result.content:
                    return result.content[0].text if result.content[0].text else str(result.content)
                else:
                    return str(result)
                    
    except Exception as e:
        logger.error(f"❌ Tool execution failed: {e}")
        return f"Error executing {tool_name}: {str(e)}"

async def process_with_gemini_mcp(user_message: str):
    """Process user message using Gemini with all available MCP tools"""
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
        
        # Get all available MCP tools
        tools_data = await get_all_mcp_tools()
        gemini_tools = [tool_data[0] for tool_data in tools_data]
        
        if not gemini_tools:
            logger.warning("⚠️ No MCP tools available, using direct Gemini response")
            response = gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"You are a helpful WhatsApp assistant. Current time: {current_time}. Keep responses under 1400 characters.\n\nUser: {user_message}"
            )
            return response.text if response.text else "Sorry, I couldn't process your request."
        
        logger.info(f"🚀 Using Gemini with {len(gemini_tools)} MCP tools available")
        
        # Send to Gemini with all available tools
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"You are a helpful WhatsApp assistant. Current time: {current_time}. Use available tools when needed to provide accurate, real-time information. Keep responses under 1400 characters and be conversational.\n\nUser message: {user_message}",
            config=types.GenerateContentConfig(
                temperature=0.1,
                tools=gemini_tools,
            ),
        )
        
        # Check if Gemini wants to call any functions
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    function_call = part.function_call
                    logger.info(f"🔧 Gemini requested function call: {function_call.name}")
                    
                    # Find the corresponding server for this tool
                    server_config = None
                    for tool_data in tools_data:
                        if tool_data[2] == function_call.name:  # tool_data[2] is tool_name
                            server_config = tool_data[1]
                            break
                    
                    if server_config:
                        # Execute the MCP tool
                        tool_result = await execute_mcp_tool(
                            server_config, 
                            function_call.name, 
                            dict(function_call.args)
                        )
                        
                        # Send result back to Gemini for final response
                        final_response = gemini_client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=f"Based on the tool result below, provide a helpful WhatsApp response to the user. Keep it under 1400 characters, include time/date info, and be conversational.\n\nUser question: {user_message}\n\nTool result: {tool_result}\n\nTime: {current_time}"
                        )
                        
                        return final_response.text if final_response.text else tool_result
                    else:
                        logger.error(f"❌ No server found for tool: {function_call.name}")
        
        # If no function calls, return direct Gemini response
        return response.text if response.text else "I couldn't process your request right now."
        
    except Exception as e:
        logger.error(f"🚨 Gemini MCP processing error: {e}")
        return f"Sorry, I encountered an error: {str(e)}"

@app.route('/webhook', methods=['POST'])
def webhook():
    """WhatsApp webhook endpoint"""
    try:
        incoming_msg = request.values.get('Body', '').strip()
        from_number = request.values.get('From', '')
        
        logger.info(f"📱 WhatsApp from {from_number}: {incoming_msg}")
        
        if not incoming_msg:
            return "OK", 200
        
        clean_number = from_number.replace("whatsapp:", "").strip()
        
        # Process with Gemini + MCP tools in background
        def process_message():
            try:
                # Create new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    ai_response = loop.run_until_complete(
                        process_with_gemini_mcp(incoming_msg)
                    )
                    
                    # Send response back to WhatsApp
                    result = send_whatsapp_message(clean_number, ai_response)
                    
                    if result.get("success"):
                        logger.info(f"✅ Response sent to {clean_number}")
                        logger.info(f"📝 Response: {ai_response[:100]}...")
                    else:
                        logger.error(f"❌ Failed to send: {result.get('error')}")
                        
                finally:
                    loop.close()
                    
            except Exception as e:
                logger.error(f"🚨 Processing error: {e}")
                send_whatsapp_message(clean_number, "Sorry, I encountered an error. Please try again!")
        
        # Run in background thread
        import threading
        thread = threading.Thread(target=process_message)
        thread.start()
        
        return "OK", 200
        
    except Exception as e:
        logger.error(f"🚨 Webhook error: {e}")
        return "Error", 500

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint"""
    return jsonify({
        "status": "WhatsApp MCP Bridge v2 is running!",
        "approach": "Gemini Function Calling + MCP Auto-Discovery",
        "mcp_servers": [server["name"] for server in MCP_SERVERS],
        "features": [
            "Auto-discovers all MCP tools",
            "Gemini decides which tools to use",
            "No manual keyword detection",
            "Real-time tool execution"
        ]
    })

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 WHATSAPP MCP BRIDGE V2 - FUNCTION CALLING")
    print("=" * 60)
    print("APPROACH: Gemini Auto-Discovery + Function Calling")
    print("")
    print("✨ How it works:")
    print("1. Auto-discovers tools from all MCP servers")
    print("2. Gemini analyzes user message") 
    print("3. Gemini automatically calls appropriate tools")
    print("4. Returns intelligent, data-rich responses")
    print("")
    print("🔧 MCP Servers:")
    for server in MCP_SERVERS:
        print(f"   • {server['name']}")
    print("")
    print("🌐 Webhook URL: http://localhost:5000/webhook")
    print("🧪 Test URL: http://localhost:5000/test")
    print("=" * 60)
    
    app.run(host="0.0.0.0", port=5000, debug=False)
