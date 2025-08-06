#!/usr/bin/env python3
"""
WhatsApp-Gemini Master Controller
This is the MAIN file that handles the complete flow:
WhatsApp → Gemini → MCP Servers → WhatsApp
"""

import os
import logging
import asyncio
from typing import Any, Optional, Dict, List
import httpx
from google import genai
from twilio.rest import Client
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import threading
import json

# Load environment variables
load_dotenv()

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

# Initialize services
twilio_client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    logger.info("Twilio client initialized")

gemini_client = None
if GEMINI_API_KEY:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    logger.info("Gemini client initialized")

# Available MCP tools (simulate the tools from your MCP servers)
class MCPTools:
    """Simulated MCP tools that Gemini can call"""
    
    @staticmethod
    async def get_weather_forecast(latitude: float, longitude: float) -> str:
        """Get weather forecast for coordinates"""
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
                        
                        result = "Weather Forecast:\n"
                        for period in periods:
                            result += f"{period['name']}: {period['detailedForecast']}\n\n"
                        return result
            return "Unable to get weather forecast"
        except Exception as e:
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
                        return f"No weather alerts for {state.upper()}"
                    
                    result = f"Weather Alerts for {state.upper()}:\n"
                    for alert in alerts[:3]:
                        props = alert['properties']
                        result += f"- {props['event']}: {props['headline']}\n"
                    return result
            return "Unable to get weather alerts"
        except Exception as e:
            return f"Weather alerts error: {str(e)}"

# Flask app for WhatsApp webhook
app = Flask(__name__)

def send_whatsapp_message(to_number: str, message: str) -> dict:
    """Send WhatsApp message via Twilio"""
    try:
        if not twilio_client:
            return {"success": False, "error": "Twilio not configured"}
        
        if not to_number.startswith("whatsapp:"):
            to_number = f"whatsapp:{to_number}"
        
        # Ensure message is under WhatsApp limit
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

async def intelligent_gemini_response(user_message: str, phone_number: str) -> str:
    """
    MAIN INTELLIGENCE: Gemini decides which MCP tools to use
    This is where the magic happens!
    """
    try:
        if not gemini_client:
            return "Gemini not configured"
        
        # Define available functions for Gemini
        weather_forecast_func = genai.protos.FunctionDeclaration(
            name="get_weather_forecast",
            description="Get weather forecast for a location",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "latitude": genai.protos.Schema(type=genai.protos.Type.NUMBER),
                    "longitude": genai.protos.Schema(type=genai.protos.Type.NUMBER),
                },
                required=["latitude", "longitude"]
            )
        )
        
        weather_alerts_func = genai.protos.FunctionDeclaration(
            name="get_weather_alerts",
            description="Get weather alerts for a US state",
            parameters=genai.protos.Schema(
                type=genai.protos.Type.OBJECT,
                properties={
                    "state": genai.protos.Schema(type=genai.protos.Type.STRING),
                },
                required=["state"]
            )
        )
        
        # Create tool config
        tool = genai.protos.Tool(
            function_declarations=[weather_forecast_func, weather_alerts_func]
        )
        
        # Model with function calling
        model = genai.GenerativeModel(
            'gemini-2.5-flash',
            tools=[tool],
            system_instruction="""You are a helpful WhatsApp assistant with access to weather tools. 
            
When users ask about weather:
- For weather forecasts, use get_weather_forecast with coordinates
- For weather alerts, use get_weather_alerts with state code
- For New York: use latitude=40.7128, longitude=-74.0060
- For California alerts: use state="CA"

Keep responses concise for WhatsApp (under 1400 characters).
Always call the appropriate function when weather is mentioned."""
        )
        
        logger.info(f"Processing with Gemini: {user_message[:100]}...")
        
        # Generate response with function calling
        response = model.generate_content(user_message)
        
        # Check if Gemini wants to call functions
        if response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    func_name = part.function_call.name
                    func_args = part.function_call.args
                    
                    logger.info(f"Gemini calling function: {func_name} with args: {func_args}")
                    
                    # Call the appropriate MCP tool
                    if func_name == "get_weather_forecast":
                        result = await MCPTools.get_weather_forecast(
                            latitude=func_args["latitude"],
                            longitude=func_args["longitude"]
                        )
                    elif func_name == "get_weather_alerts":
                        result = await MCPTools.get_weather_alerts(
                            state=func_args["state"]
                        )
                    else:
                        result = "Unknown function called"
                    
                    # Send function result back to Gemini
                    function_response = genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=func_name,
                            response={"result": result}
                        )
                    )
                    
                    # Get final response from Gemini
                    final_response = model.generate_content([
                        user_message,
                        response.candidates[0].content,
                        genai.protos.Content(parts=[function_response])
                    ])
                    
                    return final_response.text
        
        # No function call needed, return direct response
        return response.text if response.text else "No response from Gemini"
        
    except Exception as e:
        logger.error(f"Gemini processing error: {e}")
        return f"Sorry, I encountered an error: {str(e)}"

@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    """
    MAIN WEBHOOK: Receives WhatsApp messages and orchestrates the flow
    """
    try:
        # Get message data
        incoming_msg = request.values.get('Body', '').strip()
        from_number = request.values.get('From', '')
        
        logger.info(f"WhatsApp message from {from_number}: {incoming_msg}")
        
        if not incoming_msg:
            return "OK", 200
        
        # Extract clean phone number
        clean_number = from_number.replace("whatsapp:", "").strip()
        
        # Process with intelligent Gemini (this is where MCP tools get called!)
        async def process_message():
            try:
                ai_response = await intelligent_gemini_response(incoming_msg, clean_number)
                
                # Send response back to WhatsApp
                result = send_whatsapp_message(clean_number, ai_response)
                
                if result.get("success"):
                    logger.info(f"Response sent successfully to {clean_number}")
                else:
                    logger.error(f"Failed to send response: {result.get('error')}")
                    
            except Exception as e:
                logger.error(f"Message processing error: {e}")
                # Send error message
                send_whatsapp_message(clean_number, "Sorry, I encountered an error. Please try again.")
        
        # Run async processing
        asyncio.create_task(process_message())
        
        return "OK", 200
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return "Error", 500

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint"""
    return jsonify({
        "status": "WhatsApp-Gemini Master Controller is running!",
        "flow": "WhatsApp → Gemini → MCP Tools → WhatsApp",
        "available_tools": ["weather_forecast", "weather_alerts"],
        "endpoint": "/webhook"
    })

if __name__ == "__main__":
    print("=" * 60)
    print("WHATSAPP-GEMINI MASTER CONTROLLER")
    print("=" * 60)
    print("FLOW: WhatsApp → Gemini → MCP Tools → WhatsApp")
    print("")
    print("Available MCP Tools:")
    print("- Weather Forecast (coordinates)")
    print("- Weather Alerts (state)")
    print("")
    print("Webhook URL: http://localhost:5000/webhook")
    print("Test URL: http://localhost:5000/test")
    print("=" * 60)
    
    app.run(host="0.0.0.0", port=5000, debug=False)
