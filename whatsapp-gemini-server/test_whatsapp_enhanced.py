#!/usr/bin/env python3
"""
Test script for Enhanced WhatsApp-Gemini MCP server with multi-server support
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

async def test_enhanced_gemini_chat():
    """Test enhanced Gemini chat functionality with MCP tools"""
    try:
        from whatsapp_gemini_enhanced import get_gemini_response_with_tools, mcp_manager, initialize_mcp_connections
        
        print("🤖 Testing Enhanced Gemini chat with MCP tools...")
        
        # Initialize MCP connections first
        await initialize_mcp_connections()
        
        # Test weather query
        response = await get_gemini_response_with_tools("What's the weather forecast for New York?")
        print(f"✅ Weather Query Response: {response[:200]}...")
        
        # Test general AI query
        response2 = await get_gemini_response_with_tools("Tell me a fun fact about AI and machine learning")
        print(f"✅ General AI Response: {response2[:200]}...")
        
        return True
    except Exception as e:
        print(f"❌ Enhanced Gemini test failed: {e}")
        return False

async def test_mcp_tool_discovery():
    """Test MCP tool discovery and listing"""
    try:
        from whatsapp_gemini_enhanced import mcp_manager, initialize_mcp_connections
        
        print("🔍 Testing MCP tool discovery...")
        
        # Initialize connections
        await initialize_mcp_connections()
        
        # List available tools
        if mcp_manager.tools:
            print(f"✅ Discovered {len(mcp_manager.tools)} MCP tools:")
            for tool_name, tool_info in mcp_manager.tools.items():
                print(f"   - {tool_name}: {tool_info['description'][:100]}...")
        else:
            print("⚠️ No MCP tools discovered")
        
        return len(mcp_manager.tools) > 0
        
    except Exception as e:
        print(f"❌ MCP tool discovery test failed: {e}")
        return False

async def test_direct_mcp_tool_call():
    """Test calling MCP tools directly"""
    try:
        from whatsapp_gemini_enhanced import mcp_manager, initialize_mcp_connections
        
        print("🛠️ Testing direct MCP tool calls...")
        
        # Initialize connections
        await initialize_mcp_connections()
        
        if not mcp_manager.tools:
            print("⚠️ No tools available for testing")
            return False
        
        # Try to call a weather tool if available
        weather_tools = [name for name in mcp_manager.tools.keys() if 'weather' in name.lower()]
        
        if weather_tools:
            tool_name = weather_tools[0]
            print(f"📡 Testing weather tool: {tool_name}")
            
            # Try with sample coordinates (New York)
            result = await mcp_manager.call_tool(tool_name, {
                "latitude": 40.7128,
                "longitude": -74.0060
            })
            
            print(f"✅ Weather tool result: {str(result)[:200]}...")
            return True
        else:
            print("⚠️ No weather tools found for testing")
            return False
            
    except Exception as e:
        print(f"❌ Direct MCP tool call test failed: {e}")
        return False

def test_twilio_connection():
    """Test Twilio connection"""
    try:
        from twilio.rest import Client
        
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        
        if not account_sid or not auth_token:
            print("⚠️ Twilio credentials not found in environment")
            return False
            
        client = Client(account_sid, auth_token)
        
        # Test by fetching account info
        account = client.api.accounts(account_sid).fetch()
        print(f"✅ Twilio connection successful! Account: {account.friendly_name}")
        return True
        
    except Exception as e:
        print(f"❌ Twilio test failed: {e}")
        return False

async def test_enhanced_whatsapp_send():
    """Test sending a WhatsApp message with enhanced AI"""
    try:
        from whatsapp_gemini_enhanced import send_whatsapp_with_gemini_enhanced, initialize_mcp_connections
        
        # Initialize MCP connections first
        await initialize_mcp_connections()
        
        # Your WhatsApp number from the sandbox
        your_number = "+919360011424"
        test_message = "What's the weather like today in Mumbai? Give me a brief, friendly response."
        
        print(f"📱 Testing Enhanced WhatsApp send with weather query to {your_number}...")
        result = await send_whatsapp_with_gemini_enhanced(your_number, test_message)
        
        print(f"✅ Enhanced WhatsApp send result: {result[:300]}...")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced WhatsApp send test failed: {e}")
        return False

async def test_mcp_tools_listing():
    """Test the MCP tools listing function"""
    try:
        from whatsapp_gemini_enhanced import list_available_mcp_tools, initialize_mcp_connections
        
        print("📋 Testing MCP tools listing...")
        
        # Initialize connections
        await initialize_mcp_connections()
        
        # Get tools list
        tools_list = await list_available_mcp_tools()
        print(f"✅ MCP Tools List:\n{tools_list}")
        return True
        
    except Exception as e:
        print(f"❌ MCP tools listing test failed: {e}")
        return False

async def main():
    """Run all enhanced tests"""
    print("🧪 Starting Enhanced WhatsApp-Gemini MCP Server Tests\n")
    
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
    
    # Test 3: MCP tool discovery
    print("3. Testing MCP tool discovery...")
    mcp_tools_ok = await test_mcp_tool_discovery()
    print()
    
    # Test 4: MCP tools listing
    print("4. Testing MCP tools listing...")
    tools_listing_ok = await test_mcp_tools_listing()
    print()
    
    # Test 5: Enhanced Gemini chat
    print("5. Testing Enhanced Gemini AI with MCP tools...")
    enhanced_gemini_ok = await test_enhanced_gemini_chat()
    print()
    
    # Test 6: Direct MCP tool calls
    print("6. Testing direct MCP tool calls...")
    direct_tool_ok = await test_direct_mcp_tool_call()
    print()
    
    # Test 7: Enhanced WhatsApp send (only if Twilio works)
    if twilio_ok:
        print("7. Testing Enhanced WhatsApp send with MCP tools...")
        enhanced_whatsapp_ok = await test_enhanced_whatsapp_send()
        print()
    
    print("\n🎉 Enhanced testing complete!")
    print("\n📱 New Enhanced Features:")
    print("   ✨ Gemini can now access weather forecasts via MCP")
    print("   ✨ Gemini can now manage tasks via task-master MCP")
    print("   ✨ Automatic tool discovery and routing")
    print("   ✨ Enhanced WhatsApp responses with real-time data")
    print("\n📱 Next steps:")
    print("   1. Make sure you've joined the Twilio sandbox")
    print("   2. Try asking weather questions through WhatsApp")
    print("   3. Try task management commands through WhatsApp")
    print("   4. Use the enhanced MCP tools in VS Code chat")

if __name__ == "__main__":
    asyncio.run(main())
