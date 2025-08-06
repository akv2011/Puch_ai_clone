#!/usr/bin/env python3
"""
WhatsApp Webhook Receiver
This receives WhatsApp messages and can optionally forward them to VS Code Gemini
Run this separately from the MCP servers
"""

import os
import logging
from flask import Flask, request, jsonify
from twilio.rest import Client
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
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

# Initialize Twilio
twilio_client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    logger.info("Twilio client initialized for webhook")

app = Flask(__name__)

def send_whatsapp_message(to_number: str, message: str) -> dict:
    """Send WhatsApp message"""
    try:
        if not twilio_client:
            return {"success": False, "error": "Twilio not configured"}
        
        if not to_number.startswith("whatsapp:"):
            to_number = f"whatsapp:{to_number}"
        
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

@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    """
    Receive WhatsApp messages
    
    FLOW OPTIONS:
    1. Auto-reply with simple message
    2. Log message for manual processing in VS Code
    3. Forward to external AI service
    """
    try:
        incoming_msg = request.values.get('Body', '').strip()
        from_number = request.values.get('From', '')
        
        logger.info(f"WhatsApp received from {from_number}: {incoming_msg}")
        
        if not incoming_msg:
            return "OK", 200
        
        clean_number = from_number.replace("whatsapp:", "").strip()
        
        # SIMPLE AUTO-REPLY (you can customize this)
        if "help" in incoming_msg.lower():
            reply = """Hello! I'm your AI assistant.

Available commands:
- Ask about weather: "What's the weather in [location]?"
- General questions: Just ask me anything!
- Type "help" for this message

I'm connected to multiple AI tools and can help with various tasks."""
        
        elif "weather" in incoming_msg.lower():
            reply = f"I received your weather question: '{incoming_msg}'. Let me check that for you! (Weather tools are available via VS Code MCP)"
        
        else:
            reply = f"I received your message: '{incoming_msg}'. Processing with AI tools... (You can process this in VS Code using the MCP tools!)"
        
        # Send reply
        result = send_whatsapp_message(clean_number, reply)
        
        if result.get("success"):
            logger.info(f"Auto-reply sent to {clean_number}")
        else:
            logger.error(f"Failed to send auto-reply: {result.get('error')}")
        
        return "OK", 200
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return "Error", 500

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint"""
    return jsonify({
        "status": "WhatsApp Webhook Receiver is running!",
        "purpose": "Receives WhatsApp messages and can forward to VS Code MCP",
        "mcp_servers_available": ["weather", "task-master-ai", "whatsapp-tools"],
        "webhook_url": "/webhook"
    })

@app.route('/send', methods=['POST'])
def manual_send():
    """Manual send endpoint for testing"""
    try:
        data = request.get_json()
        phone = data.get('phone')
        message = data.get('message')
        
        if not phone or not message:
            return jsonify({"error": "Missing phone or message"}), 400
        
        result = send_whatsapp_message(phone, message)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("=" * 60)
    print("WHATSAPP WEBHOOK RECEIVER")
    print("=" * 60)
    print("Purpose: Receive WhatsApp messages")
    print("Integration: Works with VS Code MCP servers")
    print("")
    print("Available MCP servers in VS Code:")
    print("- weather (weather forecasts & alerts)")
    print("- task-master-ai (task management)")
    print("- whatsapp-tools (send messages)")
    print("")
    print("Webhook URL: http://localhost:5000/webhook")
    print("Test URL: http://localhost:5000/test")
    print("Manual Send: POST /send {phone, message}")
    print("=" * 60)
    
    app.run(host="0.0.0.0", port=5000, debug=False)
