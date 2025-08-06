#!/usr/bin/env python3
"""
Start the WhatsApp webhook server
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

async def start_webhook():
    """Start the webhook server"""
    try:
        from whatsapp_gemini import start_webhook_server
        
        print("🚀 Starting WhatsApp webhook server...")
        result = await start_webhook_server(5000)
        print(result)
        
        # Keep the server running
        print("\n⏳ Server is running... Press Ctrl+C to stop")
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting webhook server: {e}")

if __name__ == "__main__":
    asyncio.run(start_webhook())
