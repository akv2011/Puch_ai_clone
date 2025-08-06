#!/usr/bin/env python3
"""
Test script for WhatsApp-Gemini MCP server
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

async def test_gemini_chat():
    """Test direct Gemini chat functionality"""
    try:
        from whatsapp_gemini import get_gemini_response
        
        print("🤖 Testing Gemini chat...")
        response = await get_gemini_response("Hello! Can you tell me a fun fact about AI?")
        print(f"✅ Gemini Response: {response[:200]}...")
        return True
    except Exception as e:
        print(f"❌ Gemini test failed: {e}")
        return False

def test_twilio_connection():
    """Test Twilio connection"""
    try:
        from twilio.rest import Client
        
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        
        if not account_sid or not auth_token:
            print("⚠️  Twilio credentials not found in environment")
            return False
            
        client = Client(account_sid, auth_token)
        
        # Test by fetching account info
        account = client.api.accounts(account_sid).fetch()
        print(f"✅ Twilio connection successful! Account: {account.friendly_name}")
        return True
        
    except Exception as e:
        print(f"❌ Twilio test failed: {e}")
        return False

async def test_whatsapp_send():
    """Test sending a WhatsApp message"""
    try:
        from whatsapp_gemini import send_whatsapp_message
        
        # Your WhatsApp number from the sandbox
        your_number = "whatsapp:+919360011424"
        test_message = "🤖 Test message from WhatsApp-Gemini MCP server! This is working!"
        
        print(f"📱 Testing WhatsApp send to {your_number}...")
        result = send_whatsapp_message(your_number, test_message)  # Remove await
        
        if result.get("success"):
            print(f"✅ WhatsApp send test passed: Message SID {result.get('message_sid')}")
            return True
        else:
            print(f"⚠️  WhatsApp send failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ WhatsApp send test failed: {e}")
        return False

async def test_complete_flow():
    """Test the complete WhatsApp + Gemini flow"""
    try:
        from whatsapp_gemini import send_whatsapp_with_gemini
        
        your_number = "+919360011424"  # Remove whatsapp: prefix for this function
        test_prompt = "What's the weather like today? Give me a brief, friendly response."
        
        print(f"🔄 Testing complete WhatsApp + Gemini flow...")
        result = await send_whatsapp_with_gemini(your_number, test_prompt)
        
        print(f"✅ Complete flow result: {result[:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ Complete flow test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 Starting WhatsApp-Gemini MCP Server Tests\n")
    
    # Test 1: Environment variables
    print("1. Checking environment variables...")
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
    
    print(f"   GEMINI_API_KEY: {'✅ Set' if gemini_key else '❌ Missing'}")
    print(f"   TWILIO_ACCOUNT_SID: {'✅ Set' if twilio_sid else '❌ Missing'}")
    print(f"   TWILIO_AUTH_TOKEN: {'✅ Set' if twilio_token else '❌ Missing'}")
    print()
    
    # Test 2: Twilio connection
    print("2. Testing Twilio connection...")
    twilio_ok = test_twilio_connection()
    print()
    
    # Test 3: Gemini chat
    print("3. Testing Gemini AI...")
    gemini_ok = await test_gemini_chat()
    print()
    
    # Test 4: WhatsApp send (only if Twilio works)
    if twilio_ok:
        print("4. Testing WhatsApp message send...")
        whatsapp_ok = await test_whatsapp_send()
        print()
        
        # Test 5: Complete flow (only if both work)
        if gemini_ok and whatsapp_ok:
            print("5. Testing complete WhatsApp + Gemini flow...")
            await test_complete_flow()
    
    print("\n🎉 Testing complete!")
    print("\n📱 Next steps:")
    print("   1. Make sure you've joined the Twilio sandbox by sending 'join music-special' to +1 415 523 8886")
    print("   2. Try using the MCP tools in VS Code chat")
    print("   3. Send a message from your WhatsApp to test incoming messages")

if __name__ == "__main__":
    asyncio.run(main())
