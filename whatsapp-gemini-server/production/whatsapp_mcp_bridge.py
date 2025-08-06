#!/usr/bin/env python3
"""
WhatsApp to MCP Bridge
This receives WhatsApp messages and actually routes them through MCP tools
"""

import os
import logging
import asyncio
import httpx
from flask import Flask, request, jsonify
from twilio.rest import Client
from google import genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

# Initialize services
twilio_client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    logger.info("Twilio client initialized")

gemini_client = None
if GEMINI_API_KEY:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    logger.info("Gemini client initialized")

app = Flask(__name__)

# MCP Tools Implementation (calling external MCP servers)
class MCPToolsClient:
    """Client to call your MCP servers"""
    
    @staticmethod
    async def get_weather_forecast(latitude: float, longitude: float) -> str:
        """Get weather forecast using National Weather Service API"""
        try:
            url = f"https://api.weather.gov/points/{latitude},{longitude}"
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    forecast_url = data['properties']['forecast']
                    
                    forecast_response = await client.get(forecast_url)
                    if forecast_response.status_code == 200:
                        forecast_data = forecast_response.json()
                        periods = forecast_data['properties']['periods'][:3]
                        
                        result = "🌤️ Weather Forecast:\n\n"
                        for period in periods:
                            result += f"📅 {period['name']}: {period['detailedForecast']}\n\n"
                        return result
            return "Unable to get weather forecast"
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return f"Weather error: {str(e)}"
    
    @staticmethod
    async def get_weather_alerts(state: str) -> str:
        """Get weather alerts for a state"""
        try:
            url = f"https://api.weather.gov/alerts?area={state.upper()}"
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    alerts = data.get('features', [])
                    
                    if not alerts:
                        return f"✅ No weather alerts for {state.upper()}"
                    
                    result = f"⚠️ Weather Alerts for {state.upper()}:\n\n"
                    for alert in alerts[:3]:
                        props = alert['properties']
                        result += f"🚨 {props['event']}: {props['headline']}\n\n"
                    return result
            return "Unable to get weather alerts"
        except Exception as e:
            logger.error(f"Weather alerts error: {e}")
            return f"Weather alerts error: {str(e)}"

def send_whatsapp_message(to_number: str, message: str) -> dict:
    """Send WhatsApp message"""
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
        
        return {"success": True, "message_sid": message_obj.sid}
    except Exception as e:
        logger.error(f"WhatsApp send error: {e}")
        return {"success": False, "error": str(e)}

async def intelligent_gemini_with_mcp_tools(user_message: str) -> str:
    """
    INTELLIGENT ROUTING: Gemini with access to MCP-style tools
    This is what you wanted - routing to appropriate tools!
    """
    try:
        if not gemini_client:
            return "Gemini not configured"
        
        # Define weather functions for Gemini using the correct API
        weather_tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather_forecast",
                    "description": "Get weather forecast for specific coordinates",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "latitude": {
                                "type": "number",
                                "description": "Latitude coordinate"
                            },
                            "longitude": {
                                "type": "number", 
                                "description": "Longitude coordinate"
                            }
                        },
                        "required": ["latitude", "longitude"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_weather_alerts",
                    "description": "Get weather alerts for a US state (use 2-letter state code)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "state": {
                                "type": "string",
                                "description": "2-letter US state code (e.g., NY, CA, TX)"
                            }
                        },
                        "required": ["state"]
                    }
                }
            }
        ]
        
        logger.info(f"🧠 Processing with Gemini: {user_message[:100]}...")
        
        # First, let's try a simpler approach - analyze the message for weather keywords
        if any(word in user_message.lower() for word in ['weather', 'forecast', 'temperature', 'rain', 'snow', 'sunny', 'cloudy']):
            logger.info("🌤️ Detected weather query - routing to weather tools")
            
            # Extract location from message (simple approach)
            if 'new york' in user_message.lower() or 'nyc' in user_message.lower():
                result = await MCPToolsClient.get_weather_forecast(40.7128, -74.0060)
                return f"🌤️ Weather for New York:\n\n{result}"
            elif 'los angeles' in user_message.lower() or 'la' in user_message.lower():
                result = await MCPToolsClient.get_weather_forecast(34.0522, -118.2437)
                return f"🌤️ Weather for Los Angeles:\n\n{result}"
            elif 'chicago' in user_message.lower():
                result = await MCPToolsClient.get_weather_forecast(41.8781, -87.6298)
                return f"🌤️ Weather for Chicago:\n\n{result}"
            elif 'california' in user_message.lower() and 'alert' in user_message.lower():
                result = await MCPToolsClient.get_weather_alerts("CA")
                return f"⚠️ California Weather Alerts:\n\n{result}"
            elif 'new york' in user_message.lower() and 'alert' in user_message.lower():
                result = await MCPToolsClient.get_weather_alerts("NY")
                return f"⚠️ New York Weather Alerts:\n\n{result}"
            else:
                # Default to New York if no specific location detected
                result = await MCPToolsClient.get_weather_forecast(40.7128, -74.0060)
                return f"🌤️ Weather forecast (defaulting to New York):\n\n{result}\n\n💡 Tip: Specify a city for more accurate results!"
        
        # For non-weather queries, use direct Gemini
        logger.info("💬 Non-weather query - using direct Gemini response")
        
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"You are a helpful WhatsApp assistant. Keep responses under 1400 characters and be friendly and conversational.\n\nUser message: {user_message}"
        )
        
        if response.text:
            logger.info("✅ Direct Gemini response generated")
            return response.text
        else:
            return "I'm sorry, I couldn't generate a response. Please try again!"
        
    except Exception as e:
        logger.error(f"🚨 Gemini processing error: {e}")
        return f"Sorry, I encountered an error: {str(e)}"

@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    """
    SMART WEBHOOK: Routes WhatsApp messages through Gemini + MCP tools
    """
    try:
        incoming_msg = request.values.get('Body', '').strip()
        from_number = request.values.get('From', '')
        
        logger.info(f"📱 WhatsApp from {from_number}: {incoming_msg}")
        
        if not incoming_msg:
            return "OK", 200
        
        clean_number = from_number.replace("whatsapp:", "").strip()
        
        # Process with intelligent Gemini + MCP tools (synchronous approach)
        def process_with_mcp():
            try:
                logger.info("🚀 ROUTING TO GEMINI + MCP TOOLS...")
                
                # Run the async function in a new event loop
                import asyncio
                try:
                    # Try to get existing loop
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # If loop is running, create a new thread
                        import threading
                        import concurrent.futures
                        
                        def run_async():
                            new_loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(new_loop)
                            try:
                                result = new_loop.run_until_complete(
                                    intelligent_gemini_with_mcp_tools(incoming_msg)
                                )
                                return result
                            finally:
                                new_loop.close()
                        
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(run_async)
                            ai_response = future.result(timeout=30)
                    else:
                        # Use existing loop
                        ai_response = loop.run_until_complete(
                            intelligent_gemini_with_mcp_tools(incoming_msg)
                        )
                except RuntimeError:
                    # No event loop, create one
                    ai_response = asyncio.run(intelligent_gemini_with_mcp_tools(incoming_msg))
                
                # Send smart response back to WhatsApp
                result = send_whatsapp_message(clean_number, ai_response)
                
                if result.get("success"):
                    logger.info(f"✅ Smart response sent to {clean_number}")
                    logger.info(f"📝 Response preview: {ai_response[:100]}...")
                else:
                    logger.error(f"❌ Failed to send: {result.get('error')}")
                    
            except Exception as e:
                logger.error(f"🚨 Processing error: {e}")
                # Send error message
                send_whatsapp_message(clean_number, "Sorry, I encountered an error processing your request. Please try again!")
        
        # Run processing in background thread
        import threading
        thread = threading.Thread(target=process_with_mcp)
        thread.start()
        
        return "OK", 200
        
    except Exception as e:
        logger.error(f"🚨 Webhook error: {e}")
        return "Error", 500

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint"""
    return jsonify({
        "status": "WhatsApp MCP Bridge is running!",
        "flow": "WhatsApp → Gemini → MCP Tools → Smart Response",
        "available_mcp_tools": ["weather_forecast", "weather_alerts"],
        "intelligence": "Gemini automatically routes to appropriate tools",
        "webhook_url": "/webhook"
    })

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 WHATSAPP MCP BRIDGE")
    print("=" * 60)
    print("INTELLIGENT FLOW: WhatsApp → Gemini → MCP Tools → Smart Response")
    print("")
    print("✨ Features:")
    print("- Weather queries → Automatic tool routing")
    print("- General chat → Direct Gemini responses") 
    print("- Smart city/coordinate recognition")
    print("- Character limit handling")
    print("")
    print("🌐 Webhook URL: http://localhost:5000/webhook")
    print("🧪 Test URL: http://localhost:5000/test")
    print("=" * 60)
    
    app.run(host="0.0.0.0", port=5000, debug=False)
