#!/usr/bin/env python3
"""
Interactive demo script for MCP integration
"""

import asyncio
import os
from dotenv import load_dotenv
from google import genai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google.genai import types

load_dotenv()

class MCPDemo:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        
    async def demo_weather_query(self, query: str):
        """Demo weather queries with Gemini + MCP"""
        print(f"🌤️ Query: {query}")
        
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
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Get tools
                mcp_tools = await session.list_tools()
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
                
                # Get Gemini response
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=query,
                    config=types.GenerateContentConfig(
                        temperature=0,
                        tools=tools,
                    ),
                )
                
                # Handle function calls
                if hasattr(response.candidates[0].content, 'parts'):
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, 'function_call'):
                            function_call = part.function_call
                            print(f"🔧 Calling: {function_call.name}")
                            print(f"📋 Args: {dict(function_call.args)}")
                            
                            # Execute tool
                            result = await session.call_tool(
                                function_call.name, 
                                arguments=dict(function_call.args)
                            )
                            
                            print(f"📊 Result:")
                            print(result.content[0].text)
                            return result.content[0].text
                
                print(f"💬 Gemini says: {response.text}")
                return response.text

async def main():
    """Interactive demo"""
    demo = MCPDemo()
    
    print("🎯 MCP Integration Demo")
    print("=" * 50)
    
    # Demo queries
    queries = [
        "What's the weather forecast for San Francisco? Use coordinates 37.7749, -122.4194",
        "Get weather alerts for California (CA)",
        "What's the weather like in Miami? Use coordinates 25.7617, -80.1918",
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n📝 Demo {i}:")
        try:
            await demo.demo_weather_query(query)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        if i < len(queries):
            print("\n" + "-" * 30)
    
    print("\n✨ Demo complete!")
    print("\n🔍 What happened:")
    print("• Gemini analyzed your natural language")
    print("• Automatically selected the right MCP tool")
    print("• Filled in parameters from your query")
    print("• Executed the weather API call")
    print("• Returned real weather data")

if __name__ == "__main__":
    asyncio.run(main())
