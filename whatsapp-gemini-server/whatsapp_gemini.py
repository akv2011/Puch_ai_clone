import os
import logging
from typing import Any, Optional
import httpx
from google import genai
from google.genai import types
from twilio.rest import Client
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from flask import Flask, request
import threading

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("whatsapp-gemini")

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
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")  # Twilio Sandbox default

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

async def get_gemini_response(message: str, context: Optional[str] = None) -> str:
    """Get response from Gemini LLM."""
    try:
        if not gemini_client:
            return "Gemini API key not configured. Please set GEMINI_API_KEY environment variable."
        
        # Prepare the prompt with context if provided
        prompt = message
        if context:
            prompt = f"Context: {context}\n\nUser message: {message}"
        
        logger.info(f"Sending prompt to Gemini: {prompt[:100]}...")
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        if response.text:
            logger.info("Received response from Gemini")
            return response.text
        else:
            return "No response received from Gemini"
            
    except Exception as e:
        logger.error(f"Error getting Gemini response: {e}")
        return f"Error getting AI response: {str(e)}"

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
async def send_whatsapp_with_gemini(phone_number: str, user_message: str, context: Optional[str] = None) -> str:
    """Send a message to WhatsApp after processing it through Gemini LLM.

    Args:
        phone_number: WhatsApp phone number (e.g., +1234567890)
        user_message: The message to process with Gemini
        context: Optional context to provide to Gemini for better responses
    """
    try:
        # Get AI response from Gemini
        logger.info(f"Processing message with Gemini: {user_message[:50]}...")
        ai_response = await get_gemini_response(user_message, context)
        
        # Send the AI response via WhatsApp
        result = send_whatsapp_message(phone_number, ai_response)
        
        if result["success"]:
            return f"""Message sent successfully!
            
To: {phone_number}
AI Response: {ai_response[:200]}{'...' if len(ai_response) > 200 else ''}
Message SID: {result.get('message_sid')}
Status: {result.get('status')}"""
        else:
            return f"Failed to send WhatsApp message: {result['error']}"
            
    except Exception as e:
        logger.error(f"Error in send_whatsapp_with_gemini: {e}")
        return f"Error: {str(e)}"

@mcp.tool()
async def chat_with_gemini(message: str, context: Optional[str] = None) -> str:
    """Chat with Gemini LLM without sending to WhatsApp.

    Args:
        message: Your message or question for Gemini
        context: Optional context to provide for better responses
    """
    return await get_gemini_response(message, context)

@mcp.tool()
async def send_whatsapp_direct(phone_number: str, message: str) -> str:
    """Send a direct message to WhatsApp without AI processing.

    Args:
        phone_number: WhatsApp phone number (e.g., +1234567890)
        message: The message to send directly
    """
    result = send_whatsapp_message(phone_number, message)
    
    if result["success"]:
        return f"""Direct message sent!
        
To: {phone_number}
Message: {message}
Message SID: {result.get('message_sid')}
Status: {result.get('status')}"""
    else:
        return f"Failed to send message: {result['error']}"

@mcp.tool()
async def get_server_status() -> str:
    """Check the status of all configured services."""
    status = []
    
    # Check Gemini API
    if GEMINI_API_KEY:
        try:
            model = genai.GenerativeModel('gemini-pro')
            test_response = model.generate_content("Say hello")
            if test_response.text:
                status.append("Gemini LLM: Connected and working")
            else:
                status.append("Gemini LLM: Connected but not responding properly")
        except Exception as e:
            status.append(f"Gemini LLM: Error - {str(e)}")
    else:
        status.append("Gemini LLM: API key not configured")
    
    # Check Twilio
    if twilio_client:
        try:
            account = twilio_client.api.accounts(TWILIO_ACCOUNT_SID).fetch()
            status.append(f"Twilio WhatsApp: Connected (Account: {account.friendly_name})")
        except Exception as e:
            status.append(f"Twilio WhatsApp: Error - {str(e)}")
    else:
        status.append("Twilio WhatsApp: Credentials not configured")
    
    return "\n".join(status)

# Flask app for webhook handling
webhook_app = Flask(__name__)

@webhook_app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages and auto-reply with Gemini responses."""
    try:
        # Get incoming message data from Twilio
        incoming_msg = request.values.get('Body', '').strip()
        from_number = request.values.get('From', '')
        to_number = request.values.get('To', '')
        
        logger.info(f"Received WhatsApp message from {from_number}: {incoming_msg}")
        logger.info(f"Message details - From: {from_number}, To: {to_number}")
        
        if not incoming_msg:
            logger.info("No message body, returning OK")
            return "OK", 200
            
        # Extract phone number for processing
        clean_number = from_number.replace("whatsapp:", "").strip()
        logger.info(f"Clean number extracted: {clean_number}")
        
        # Simple synchronous approach - get AI response first
        try:
            logger.info("Getting Gemini response...")
            
            # Use synchronous approach for webhook
            if not gemini_client:
                logger.error("Gemini client not available")
                return "OK", 200
                
            # Get AI response directly (sync way)
            prompt = f"Context: You are a helpful WhatsApp assistant. Keep responses concise and friendly.\n\nUser message: {incoming_msg}"
            
            logger.info(f"Sending to Gemini: {prompt[:100]}...")
            response = gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            if response.text:
                ai_response = response.text
                logger.info(f"Got AI response: {ai_response[:100]}...")
                
                # Send response back to WhatsApp
                logger.info(f"Sending WhatsApp message to {clean_number}")
                result = send_whatsapp_message(clean_number, f"AI: {ai_response}")
                
                if result.get("success"):
                    logger.info(f"Successfully sent reply to {clean_number}")
                else:
                    logger.error(f"Failed to send WhatsApp: {result.get('error')}")
            else:
                logger.error("No response from Gemini")
                
        except Exception as e:
            logger.error(f"Error in processing: {str(e)}")
            # Send simple error message
            try:
                send_whatsapp_message(clean_number, "Sorry, I encountered an error. Please try again.")
                logger.info("Sent error message")
            except Exception as send_error:
                logger.error(f"Failed to send error message: {send_error}")
        
        return "OK", 200
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
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
        
        return f"Webhook server started on port {port}!\nYour webhook URL: http://localhost:{port}/webhook\n\nNext steps:\n1. Use ngrok to expose your local server: ngrok http {port}\n2. Copy the ngrok URL\n3. Set it in Twilio Console > WhatsApp > Sandbox > Webhook URL"
        
    except Exception as e:
        return f"Error starting webhook server: {str(e)}"

@mcp.tool()
async def setup_webhook_instructions() -> str:
    """Get detailed instructions for setting up the WhatsApp webhook."""
    return """
🔧 WhatsApp Auto-Reply Setup Instructions:

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

5. **Test the setup:**
   - Send a message to your Twilio WhatsApp number: +1 415 523 8886
   - Your message will be processed by Gemini AI
   - You'll receive an AI-generated response automatically!

🎉 Once set up, you can have full conversations with AI through WhatsApp!
"""

if __name__ == "__main__":
    logger.info("Starting WhatsApp-Gemini MCP Server")
    mcp.run(transport='stdio')
