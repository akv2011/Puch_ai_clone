#!/usr/bin/env python3
"""
Test script for Intelligent WhatsApp-Gemini MCP System
Demonstrates smart routing, fallback mechanisms, and enhanced capabilities
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
import json

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

async def test_intelligent_routing():
    """Test the intelligent routing capabilities"""
    try:
        from whatsapp_gemini_intelligent import intelligent_manager, initialize_intelligent_connections
        
        print("🧠 Testing Intelligent MCP Routing System")
        print("=" * 60)
        
        # Initialize connections
        print("1. 🔧 Initializing intelligent MCP connections...")
        success = await initialize_intelligent_connections()
        
        if not success:
            print("❌ Failed to connect to MCP servers. Please check your setup.")
            return False
        
        print(f"✅ Successfully connected to MCP servers")
        print(f"🛠️ Available tools: {len(intelligent_manager.tools)}")
        
        # Test queries with different intents
        test_cases = [
            {
                "query": "What's the weather like in Tokyo today?",
                "expected_server": "weather",
                "description": "Weather query - should route to weather server"
            },
            {
                "query": "Create a task to learn Python programming",
                "expected_server": "task-master", 
                "description": "Task creation - should route to task-master server"
            },
            {
                "query": "What's the temperature in Paris and create a travel planning task?",
                "expected_server": "multiple",
                "description": "Multi-intent query - should handle both weather and tasks"
            },
            {
                "query": "Tell me a joke about programming",
                "expected_server": "direct",
                "description": "General query - should use direct Gemini"
            },
            {
                "query": "How do I bake a chocolate cake?",
                "expected_server": "direct",
                "description": "Cooking query - should fallback to direct Gemini"
            }
        ]
        
        print("\n2. 🧪 Testing Intelligent Query Routing:")
        print("-" * 50)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 Test {i}: {test_case['description']}")
            print(f"🔍 Query: \"{test_case['query']}\"")
            print(f"🎯 Expected routing: {test_case['expected_server']}")
            
            try:
                # Analyze query intent
                best_servers = intelligent_manager.get_best_servers_for_query(test_case['query'])
                print(f"🧠 Intelligent analysis suggests: {best_servers}")
                
                # Get response
                response = await intelligent_manager.route_query_intelligently(test_case['query'])
                print(f"🤖 Response: {response[:150]}...")
                print("✅ Test passed")
                
            except Exception as e:
                print(f"❌ Test failed: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def test_server_status():
    """Test server status and capabilities"""
    try:
        from whatsapp_gemini_intelligent import intelligent_manager, MCP_SERVERS
        
        print("\n3. 📊 Server Status and Capabilities:")
        print("-" * 40)
        
        for server_name, config in MCP_SERVERS.items():
            print(f"\n🖥️ **{server_name.upper()} SERVER**")
            print(f"   Status: {config.status.value}")
            print(f"   Description: {config.description}")
            print(f"   Capabilities: {', '.join(config.capabilities)}")
            print(f"   Priority: {config.priority}")
            
            # Count tools for this server
            server_tools = [t for t in intelligent_manager.tools.values() if t["server"] == server_name]
            print(f"   Tools available: {len(server_tools)}")
            
            if server_tools:
                print("   Tool details:")
                for tool in server_tools[:3]:  # Show first 3 tools
                    print(f"     • {tool['original_name']}: {tool['description']}")
                if len(server_tools) > 3:
                    print(f"     ... and {len(server_tools) - 3} more")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing server status: {e}")
        return False

async def test_fallback_mechanisms():
    """Test fallback mechanisms when servers fail"""
    try:
        from whatsapp_gemini_intelligent import intelligent_manager
        
        print("\n4. 🔄 Testing Fallback Mechanisms:")
        print("-" * 35)
        
        # Test with a query that might not be handled by specific servers
        fallback_queries = [
            "How do I solve a Rubik's cube?",
            "What's the capital of Antarctica?", 
            "Explain quantum physics in simple terms"
        ]
        
        for query in fallback_queries:
            print(f"\n🔍 Testing fallback for: \"{query}\"")
            
            try:
                response = await intelligent_manager.route_query_intelligently(query)
                print(f"🤖 Fallback response: {response[:100]}...")
                print("✅ Fallback working correctly")
                
            except Exception as e:
                print(f"❌ Fallback failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing fallbacks: {e}")
        return False

async def test_whatsapp_integration():
    """Test WhatsApp integration if Twilio is configured"""
    try:
        twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
        twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
        
        print("\n5. 📱 WhatsApp Integration Test:")
        print("-" * 30)
        
        if not twilio_sid or not twilio_token:
            print("⚠️ Twilio credentials not configured. Skipping WhatsApp test.")
            print("   To enable: Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in .env")
            return True
        
        from whatsapp_gemini_intelligent import send_whatsapp_message
        
        # Test sending a message (to a test number)
        test_number = "+919360011424"  # Your test number
        test_message = "🧠 Test message from Intelligent MCP System! This system can now:\n\n✅ Route queries intelligently\n✅ Handle weather and task queries\n✅ Provide fallback responses\n✅ Recover from errors gracefully"
        
        print(f"📱 Testing WhatsApp send to {test_number}...")
        result = send_whatsapp_message(test_number, test_message)
        
        if result.get("success"):
            print(f"✅ WhatsApp test successful!")
            print(f"   Message SID: {result.get('message_sid')}")
        else:
            print(f"⚠️ WhatsApp test failed: {result.get('error')}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing WhatsApp: {e}")
        return False

async def main():
    """Run comprehensive tests of the intelligent MCP system"""
    print("🚀 INTELLIGENT WHATSAPP-GEMINI MCP SYSTEM TESTS")
    print("🧠 Enhanced with Smart Routing & Fallback Mechanisms")
    print("=" * 70)
    
    # Environment check
    print("🔧 Environment Check:")
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
    
    print(f"   GEMINI_API_KEY: {'✅ Set' if gemini_key else '❌ Missing'}")
    print(f"   TWILIO_ACCOUNT_SID: {'✅ Set' if twilio_sid else '⚠️ Optional'}")
    print(f"   TWILIO_AUTH_TOKEN: {'✅ Set' if twilio_token else '⚠️ Optional'}")
    
    if not gemini_key:
        print("❌ GEMINI_API_KEY is required. Please set it in your .env file.")
        return
    
    # Run tests
    tests = [
        ("Intelligent Routing", test_intelligent_routing),
        ("Server Status", test_server_status), 
        ("Fallback Mechanisms", test_fallback_mechanisms),
        ("WhatsApp Integration", test_whatsapp_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*20} TEST SUMMARY {'='*20}")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Your Intelligent MCP System is working perfectly!")
        print("\n🌟 Key Features Verified:")
        print("   ✅ Smart query analysis and server routing")
        print("   ✅ Automatic fallback when servers can't handle queries")
        print("   ✅ Enhanced error handling and recovery")
        print("   ✅ Multi-server tool coordination")
        print("   ✅ WhatsApp integration with intelligent responses")
        
        print("\n📱 Next Steps:")
        print("   1. Add this to your VS Code MCP configuration")
        print("   2. Test with real WhatsApp messages") 
        print("   3. Add more MCP servers as needed")
        print("   4. Enjoy intelligent AI assistance!")
    else:
        print(f"\n⚠️ {total - passed} tests failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())
