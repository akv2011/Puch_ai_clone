#!/usr/bin/env python3
"""
Simple test script for WhatsApp-Gemini MCP integration
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
from google import genai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables
load_dotenv()

async def test_weather_server():
    """Test the weather server directly"""
    print("🌤️ Testing weather server...")
    
    server_params = StdioServerParameters(
        command="C:\\Users\\arunk\\.local\\bin\\uv.exe",
        args=[
            "--directory",
            "c:\\Users\\arunk\\Puch_ai_clone\\weather-server\\weather-standalone",
            "run",
            "python",
            "weather.py"
        ],
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # List available tools
                tools_result = await session.list_tools()
                print(f"✅ Weather server tools: {[tool.name for tool in tools_result.tools]}")
                
                # Test get_forecast tool
                result = await session.call_tool("get_forecast", {"latitude": 40.7128, "longitude": -74.0060})
                print(f"✅ Weather forecast test: {result.content[0].text[:100]}...")
                
                return True
    except Exception as e:
        print(f"❌ Weather server error: {e}")
        return False

async def test_gemini_integration():
    """Test Gemini API integration"""
    print("🤖 Testing Gemini integration...")
    
    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Say hello and that you're working with MCP tools"
        )
        
        print(f"✅ Gemini response: {response.text[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Gemini error: {e}")
        return False

async def test_gemini_with_weather_tools():
    """Test Gemini with weather tools integration"""
    print("🌡️ Testing Gemini + Weather tools...")
    
    server_params = StdioServerParameters(
        command="C:\\Users\\arunk\\.local\\bin\\uv.exe",
        args=[
            "--directory",
            "c:\\Users\\arunk\\Puch_ai_clone\\weather-server\\weather-standalone",
            "run",
            "python",
            "weather.py"
        ],
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Get tools
                mcp_tools = await session.list_tools()
                
                # Convert to Gemini format
                from google.genai import types
                tools = [
                    types.Tool(
                        function_declarations=[
                            {
                                "name": tool.name,
                                "description": tool.description,
                                "parameters": {
                                    k: v
                                    for k, v in tool.inputSchema.items()
                                    if k not in ["additionalProperties", "$schema"]
                                },
                            }
                        ]
                    )
                    for tool in mcp_tools.tools
                ]
                
                # Initialize Gemini client
                client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
                
                # Test query
                prompt = "What's the weather forecast for New York City? Use latitude 40.7128 and longitude -74.0060"
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0,
                        tools=tools,
                    ),
                )
                
                # Check if Gemini wants to use a tool
                if hasattr(response.candidates[0].content, 'parts'):
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, 'function_call'):
                            function_call = part.function_call
                            print(f"🔧 Gemini wants to call: {function_call.name}")
                            print(f"📋 With args: {dict(function_call.args)}")
                            
                            # Execute the function call
                            result = await session.call_tool(
                                function_call.name, 
                                arguments=dict(function_call.args)
                            )
                            
                            print(f"✅ Weather result: {result.content[0].text[:200]}...")
                            return True
                
                print(f"✅ Gemini response: {response.text[:100]}...")
                return True
                
    except Exception as e:
        print(f"❌ Gemini + Weather error: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 Running Simple MCP Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Gemini Integration", test_gemini_integration),
        ("Weather Server", test_weather_server),
        ("Gemini + Weather Tools", test_gemini_with_weather_tools),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")

if __name__ == "__main__":
    asyncio.run(main())
