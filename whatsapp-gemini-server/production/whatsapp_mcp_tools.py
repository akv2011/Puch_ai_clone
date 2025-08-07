

import os
import logging
from typing import Optional
from twilio.rest import Client
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("whatsapp-tools")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
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
    logger.info("Twilio client initialized for MCP")

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

@mcp.tool()
def send_whatsapp(phone_number: str, message: str) -> str:
    """Send a WhatsApp message to a phone number.
    
    Args:
        phone_number: WhatsApp phone number (e.g., +1234567890)
        message: The message to send
    """
    result = send_whatsapp_message(phone_number, message)
    
    if result["success"]:
        return f"WhatsApp message sent successfully to {phone_number}. Message SID: {result['message_sid']}"
    else:
        return f"Failed to send WhatsApp message: {result['error']}"

@mcp.tool()
def get_whatsapp_status() -> str:
    """Check the status of WhatsApp/Twilio connection."""
    if not twilio_client:
        return "Twilio not configured. Please set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN."
    
    try:
        account = twilio_client.api.accounts(TWILIO_ACCOUNT_SID).fetch()
        return f"WhatsApp/Twilio connected. Account: {account.friendly_name}"
    except Exception as e:
        return f"WhatsApp/Twilio error: {str(e)}"

if __name__ == "__main__":
    logger.info("Starting WhatsApp Tools MCP Server")
    mcp.run(transport='stdio')
