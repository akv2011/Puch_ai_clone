#!/usr/bin/env python3
"""
Demonstration of Enhanced WhatsApp-Gemini MCP Server
This script shows how Gemini can control other MCP servers
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

async def demo_multi_server_capability():
    """Demonstrate Gemini controlling multiple MCP servers"""
    
    print("🌟 Enhanced WhatsApp-Gemini MCP Server Demo")
    print("=" * 60)
    
    try:
        from whatsapp_gemini_enhanced import (
            get_gemini_response_with_tools,
            mcp_manager,
            initialize_mcp_connections,
            list_available_mcp_tools
        )
        
        print("1. 🔧 Initializing MCP server connections...")
        await initialize_mcp_connections()
        
        print(f"✅ Connected to {len(mcp_manager.servers)} MCP servers")
        print(f"✅ Discovered {len(mcp_manager.tools)} total tools")
        
        print("\n2. 📋 Available MCP Tools:")
        tools_list = await list_available_mcp_tools()
        print(tools_list)
        
        print("\n3. 🧪 Testing Multi-Server Queries:")
        
        # Test 1: Weather query (should route to weather server)
        print("\n   🌤️ Weather Query Test:")
        weather_query = "What's the weather forecast for Mumbai, India?"
        print(f"   Query: {weather_query}")
        
        weather_response = await get_gemini_response_with_tools(weather_query)
        print(f"   Response: {weather_response[:300]}...")
        
        # Test 2: Task management query (should route to task-master)
        print("\n   📝 Task Management Test:")
        task_query = "Create a task to learn about MCP servers and how they work"
        print(f"   Query: {task_query}")
        
        task_response = await get_gemini_response_with_tools(task_query)
        print(f"   Response: {task_response[:300]}...")
        
        # Test 3: General AI query (should use Gemini directly)
        print("\n   🤖 General AI Test:")
        ai_query = "Explain the concept of Model Context Protocol in simple terms"
        print(f"   Query: {ai_query}")
        
        ai_response = await get_gemini_response_with_tools(ai_query)
        print(f"   Response: {ai_response[:300]}...")
        
        print("\n4. 🎯 How This Works:")
        print("   • Gemini analyzes your natural language query")
        print("   • It automatically selects the appropriate MCP tool")
        print("   • The tool call is routed to the correct server")
        print("   • Results are processed and returned to you")
        print("   • All through natural conversation!")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

async def demo_whatsapp_integration():
    """Demonstrate WhatsApp integration with enhanced capabilities"""
    
    print("\n5. 📱 WhatsApp Integration Demo:")
    
    try:
        from whatsapp_gemini_enhanced import send_whatsapp_with_gemini_enhanced
        
        # Test phone number (replace with your number)
        test_number = "+919360011424"
        
        print(f"   📤 Sending enhanced WhatsApp message to {test_number}")
        
        # This message will trigger weather tool usage
        test_message = "Hi! Can you check the weather for Delhi and create a task to plan outdoor activities if it's nice?"
        
        result = await send_whatsapp_with_gemini_enhanced(
            test_number, 
            test_message,
            "You are a helpful assistant with access to weather and task management tools"
        )
        
        print(f"   ✅ WhatsApp Demo Result: {result[:400]}...")
        
        return True
        
    except Exception as e:
        print(f"   ❌ WhatsApp demo failed: {e}")
        return False

async def demo_routing_intelligence():
    """Demonstrate intelligent routing capabilities"""
    
    print("\n6. 🧠 Intelligent Routing Demo:")
    
    try:
        from whatsapp_gemini_enhanced import get_gemini_response_with_tools
        
        # Test queries that should route to different servers
        test_queries = [
            {
                "query": "What's the temperature in Tokyo right now?",
                "expected_route": "weather server",
                "tool_type": "weather"
            },
            {
                "query": "Add a task to my project to research AI trends",
                "expected_route": "task-master server", 
                "tool_type": "task"
            },
            {
                "query": "Tell me a joke about programmers",
                "expected_route": "direct Gemini",
                "tool_type": "none"
            }
        ]
        
        for i, test in enumerate(test_queries, 1):
            print(f"\n   Test {i}: {test['expected_route']}")
            print(f"   Query: {test['query']}")
            
            response = await get_gemini_response_with_tools(test['query'])
            print(f"   Response: {response[:200]}...")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Routing demo failed: {e}")
        return False

async def main():
    """Run the complete demonstration"""
    
    print("🎬 Starting Enhanced WhatsApp-Gemini MCP Server Demonstration\n")
    
    # Check environment
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not gemini_key:
        print("❌ GEMINI_API_KEY not found. Please set it in your .env file.")
        return
    
    try:
        # Demo 1: Multi-server capability
        await demo_multi_server_capability()
        
        # Demo 2: WhatsApp integration (optional)
        if os.getenv("TWILIO_ACCOUNT_SID"):
            await demo_whatsapp_integration()
        else:
            print("\n📱 WhatsApp demo skipped (Twilio not configured)")
        
        # Demo 3: Routing intelligence
        await demo_routing_intelligence()
        
        print("\n🎉 Demo Complete!")
        print("\n🌟 Key Benefits of Enhanced Version:")
        print("   ✨ Single Gemini interface controls multiple specialized servers")
        print("   ✨ Automatic tool discovery and intelligent routing")
        print("   ✨ Natural language queries get routed to appropriate tools")
        print("   ✨ Enhanced WhatsApp responses with real-time data")
        print("   ✨ Expandable architecture for adding more MCP servers")
        
        print("\n🔧 Usage in VS Code:")
        print("   • Use @send_whatsapp_with_gemini_enhanced for enhanced messaging")
        print("   • Use @chat_with_gemini_enhanced for AI with tool access")
        print("   • Use @list_available_mcp_tools to see what's available")
        print("   • Use @get_server_status to check all services")
        
        print("\n📱 WhatsApp Usage:")
        print("   • Send weather queries: 'What's the weather in New York?'")
        print("   • Send task commands: 'Create a task to learn Python'")
        print("   • Send general questions: 'Explain quantum computing'")
        print("   • Gemini will automatically route to the right tool!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
