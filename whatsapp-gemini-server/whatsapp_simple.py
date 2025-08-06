#!/usr/bin/env python3
"""
Simple WhatsApp-Gemini server with MCP weather integration
"""

import asyncio
import os
import threading
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from dotenv import load_dotenv
from google import genai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google.genai import types
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhatsAppBot:
    def __init__(self):
        # Initialize Twilio
        self.twilio_client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
        
        # Initialize Gemini
        self.gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        # Weather server config
        self.weather_server_params = StdioServerParameters(
            command="C:\\Users\\arunk\\.local\\bin\\uv.exe",
            args=[
                "--directory",
                "c:\\Users\\arunk\\Puch_ai_clone\\weather-server\\weather-standalone",
                "run",
                "python",
                "weather.py"
            ],
        )
        
        logger.info("WhatsApp bot initialized successfully")
    
    async def get_weather_tools(self):
        """Get weather tools from MCP server"""
        try:
            async with stdio_client(self.weather_server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    mcp_tools = await session.list_tools()
                    
                    tools = [
                        types.Tool(
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
                        for tool in mcp_tools.tools
                    ]
                    
                    return tools, session
        except Exception as e:
            logger.error(f"Failed to get weather tools: {e}")
            return [], None
    
    def truncate_message(self, message: str, max_length: int = 1500) -> str:
        """Truncate message to fit WhatsApp limits"""
        if len(message) <= max_length:
            return message
        
        # Try to cut at sentence boundary
        truncated = message[:max_length-50]
        last_period = truncated.rfind('.')
        last_newline = truncated.rfind('\n')
        
        cut_point = max(last_period, last_newline)
        if cut_point > max_length // 2:  # If we found a good cut point
            return truncated[:cut_point + 1] + "\n\n...(message truncated)"
        else:
            return truncated + "...(truncated)"
    
    async def process_message(self, message: str):
        """Process incoming WhatsApp message with Gemini + MCP"""
        try:
            # System prompt for WhatsApp responses
            system_prompt = """You are a helpful WhatsApp assistant with access to weather tools and general knowledge.

IMPORTANT CONSTRAINTS:
- Keep responses under 1400 characters (WhatsApp limit is 1600)
- Be concise, friendly, and helpful
- Use emojis sparingly
- If weather info is requested, use available tools
- For general questions, provide brief but informative answers

Guidelines:
- Weather queries: Use MCP weather tools when available
- General queries: Provide direct, concise responses
- Always aim for clarity over length
"""
            
            # Check if message is weather-related
            weather_keywords = ["weather", "forecast", "temperature", "rain", "sunny", "cloudy", "alert"]
            is_weather_query = any(keyword in message.lower() for keyword in weather_keywords)
            
            if is_weather_query:
                logger.info("Processing weather query with MCP tools")
                
                async with stdio_client(self.weather_server_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        
                        # Get tools
                        mcp_tools = await session.list_tools()
                        tools = [
                            types.Tool(
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
                            for tool in mcp_tools.tools
                        ]
                        
                        # Get Gemini response with tools and system prompt
                        enhanced_prompt = f"{system_prompt}\n\nUser query: {message}\n\nIf you need coordinates for weather, use these popular cities: NYC (40.7128, -74.0060), LA (34.0522, -118.2437), Chicago (41.8781, -87.6298), Miami (25.7617, -80.1918), SF (37.7749, -122.4194)"
                        
                        response = self.gemini_client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=enhanced_prompt,
                            config=types.GenerateContentConfig(
                                temperature=0,
                                tools=tools,
                                max_output_tokens=800,  # Limit tokens to control length
                            ),
                        )
                        
                        # Check for function calls
                        if hasattr(response.candidates[0].content, 'parts'):
                            for part in response.candidates[0].content.parts:
                                if hasattr(part, 'function_call'):
                                    function_call = part.function_call
                                    logger.info(f"Executing: {function_call.name}")
                                    
                                    # Execute the function call
                                    result = await session.call_tool(
                                        function_call.name, 
                                        arguments=dict(function_call.args)
                                    )
                                    
                                    # Format weather response with character limits
                                    weather_response = f"🌤️ Weather Update:\n\n{result.content[0].text}"
                                    return self.truncate_message(weather_response)
                        
                        # Truncate regular response
                        return self.truncate_message(response.text if response.text else "I couldn't get weather information.")
            
            else:
                # Regular Gemini response for non-weather queries with system prompt
                enhanced_prompt = f"{system_prompt}\n\nUser query: {message}"
                
                response = self.gemini_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=enhanced_prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.3,
                        max_output_tokens=600,  # Shorter for general responses
                    )
                )
                return self.truncate_message(response.text if response.text else "I couldn't generate a response.")
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return "Sorry, I encountered an error. Please try again with a shorter message."
    
    def send_whatsapp_message(self, to_number: str, message: str):
        """Send message via WhatsApp"""
        try:
            # Truncate message if too long (WhatsApp limit is 1600 characters)
            if len(message) > 1500:
                truncated_message = message[:1450] + "...\n\n📝 (Message truncated due to length limit)"
            else:
                truncated_message = message
            
            self.twilio_client.messages.create(
                body=truncated_message,
                from_=os.getenv("TWILIO_WHATSAPP_NUMBER"),
                to=f"whatsapp:{to_number}"
            )
            logger.info(f"Message sent to {to_number}")
        except Exception as e:
            logger.error(f"Failed to send message: {e}")

# Initialize bot
bot = WhatsAppBot()

# Flask app for webhook
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming WhatsApp messages"""
    try:
        # Get message details
        from_number = request.form.get("From", "").replace("whatsapp:", "")
        message_body = request.form.get("Body", "")
        
        logger.info(f"Received message from {from_number}: {message_body}")
        
        # Process message synchronously in background
        import threading
        
        def process_and_send():
            try:
                # Create new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                async def handle_message():
                    response = await bot.process_message(message_body)
                    bot.send_whatsapp_message(from_number, response)
                
                loop.run_until_complete(handle_message())
                loop.close()
                
            except Exception as e:
                logger.error(f"Background processing error: {e}")
        
        # Start background thread
        thread = threading.Thread(target=process_and_send)
        thread.daemon = True
        thread.start()
        
        # Return empty TwiML response immediately
        resp = MessagingResponse()
        return str(resp)
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        resp = MessagingResponse()
        return str(resp)

@app.route("/test", methods=["GET", "POST"])
def test():
    """Test endpoint"""
    return jsonify({"status": "WhatsApp bot is running!", "mcp": "weather tools available"})

if __name__ == "__main__":
    print("Starting WhatsApp-Gemini MCP Bot")
    print("Ready to receive WhatsApp messages!")
    print("Weather tools available via MCP")
    print("Webhook endpoint: /webhook")
    print("Test endpoint: /test")
    
    # Run Flask app
    app.run(host="0.0.0.0", port=5000, debug=False)
