#!/usr/bin/env python3
"""
Intelligent MCP Router for Gemini
Provides smart routing and fallback mechanisms for MCP servers
"""

import os
import logging
import asyncio
import json
from typing import Any, Optional, Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum
import re

from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ServerStatus(Enum):
    CONNECTED = "connected"
    CONNECTING = "connecting"
    DISCONNECTED = "disconnected"
    ERROR = "error"

@dataclass
class MCPServerConfig:
    name: str
    command: str
    args: List[str]
    env: Dict[str, str]
    description: str
    capabilities: List[str]  # e.g., ["weather", "forecasting", "alerts"]
    priority: int = 1  # Higher priority = preferred server
    fallback_servers: List[str] = None  # Fallback server names
    status: ServerStatus = ServerStatus.DISCONNECTED

@dataclass
class ToolInfo:
    name: str
    original_name: str
    description: str
    server_name: str
    schema: Dict
    session: Any
    capabilities: List[str]

class IntelligentMCPRouter:
    """
    Intelligent router that analyzes user queries and routes them to appropriate MCP servers
    with fallback mechanisms and error recovery
    """
    
    def __init__(self, gemini_api_key: str):
        self.gemini_client = genai.Client(api_key=gemini_api_key)
        self.servers: Dict[str, MCPServerConfig] = {}
        self.tools: Dict[str, ToolInfo] = {}
        self.sessions: Dict[str, Any] = {}
        self.server_capabilities = {
            "weather": ["weather", "forecast", "temperature", "rain", "sunny", "cloudy", "climate"],
            "task": ["task", "todo", "project", "reminder", "schedule", "planning", "organize"],
            "whatsapp": ["whatsapp", "message", "send", "chat", "communicate", "text"],
            "general": ["help", "explain", "define", "what", "how", "why", "tell", "joke", "story"]
        }
        
    def register_server(self, config: MCPServerConfig):
        """Register a new MCP server configuration"""
        self.servers[config.name] = config
        logger.info(f"Registered MCP server: {config.name} with capabilities: {config.capabilities}")
    
    async def connect_to_server(self, server_name: str) -> bool:
        """Connect to a specific MCP server"""
        if server_name not in self.servers:
            logger.error(f"Server {server_name} not registered")
            return False
            
        config = self.servers[server_name]
        config.status = ServerStatus.CONNECTING
        
        try:
            logger.info(f"Connecting to MCP server: {server_name}")
            
            # Create server parameters
            server_params = StdioServerParameters(
                command=config.command,
                args=config.args,
                env=config.env,
                cwd=None
            )
            
            # Start the server connection
            read, write = await stdio_client(server_params).__aenter__()
            session = await ClientSession(read, write).__aenter__()
            await session.initialize()
            
            # Discover tools
            mcp_tools = await session.list_tools()
            
            # Store session
            self.sessions[server_name] = {
                "session": session,
                "read": read,
                "write": write,
                "config": config
            }
            
            # Register tools
            for tool in mcp_tools.tools:
                tool_name = f"{server_name}_{tool.name}"
                self.tools[tool_name] = ToolInfo(
                    name=tool_name,
                    original_name=tool.name,
                    description=f"[{server_name.upper()}] {tool.description}",
                    server_name=server_name,
                    schema=tool.inputSchema,
                    session=session,
                    capabilities=config.capabilities
                )
            
            config.status = ServerStatus.CONNECTED
            logger.info(f"Successfully connected to {server_name} with {len(mcp_tools.tools)} tools")
            return True
            
        except Exception as e:
            config.status = ServerStatus.ERROR
            logger.error(f"Failed to connect to {server_name}: {e}")
            return False
    
    async def connect_all_servers(self):
        """Connect to all registered servers"""
        tasks = []
        for server_name in self.servers.keys():
            tasks.append(self.connect_to_server(server_name))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        connected_count = sum(1 for result in results if result is True)
        logger.info(f"Connected to {connected_count}/{len(self.servers)} MCP servers")
        
        return connected_count > 0
    
    def analyze_query(self, query: str) -> List[Tuple[str, float]]:
        """
        Analyze a user query and return ranked servers based on capability match
        Returns list of (server_name, confidence_score) tuples
        """
        query_lower = query.lower()
        server_scores = {}
        
        for server_name, config in self.servers.items():
            if config.status != ServerStatus.CONNECTED:
                continue
                
            score = 0.0
            
            # Check capability keywords
            for capability in config.capabilities:
                if capability.lower() in query_lower:
                    score += 1.0
            
            # Check tool descriptions
            for tool_name, tool_info in self.tools.items():
                if tool_info.server_name == server_name:
                    # Check if query keywords match tool descriptions
                    tool_desc_lower = tool_info.description.lower()
                    words = re.findall(r'\w+', query_lower)
                    for word in words:
                        if len(word) > 3 and word in tool_desc_lower:
                            score += 0.5
            
            # Apply priority multiplier
            score *= config.priority
            
            if score > 0:
                server_scores[server_name] = score
        
        # Sort by score (highest first)
        ranked_servers = sorted(server_scores.items(), key=lambda x: x[1], reverse=True)
        
        logger.info(f"Query analysis for '{query}': {ranked_servers}")
        return ranked_servers
    
    async def route_query(self, query: str, context: Optional[str] = None) -> str:
        """
        Intelligently route a query to the best available MCP server with fallback
        """
        try:
            # Analyze query to find best servers
            ranked_servers = self.analyze_query(query)
            
            if not ranked_servers:
                # No specific server match, use direct Gemini
                return await self.get_direct_gemini_response(query, context)
            
            # Try servers in order of preference
            for server_name, confidence in ranked_servers:
                try:
                    result = await self.try_server_with_gemini(server_name, query, context)
                    if result and not result.startswith("❌"):
                        logger.info(f"Successfully routed query to {server_name} (confidence: {confidence:.2f})")
                        return result
                    else:
                        logger.warning(f"Server {server_name} couldn't handle query, trying fallbacks...")
                        
                except Exception as e:
                    logger.error(f"Error with server {server_name}: {e}")
                    continue
            
            # If all servers failed, try direct Gemini
            logger.info("All MCP servers failed, falling back to direct Gemini response")
            return await self.get_direct_gemini_response(query, context)
            
        except Exception as e:
            logger.error(f"Error in route_query: {e}")
            return f"❌ I encountered an error while processing your request: {str(e)}"
    
    async def try_server_with_gemini(self, server_name: str, query: str, context: Optional[str] = None) -> str:
        """Try to handle a query with a specific server using Gemini function calling"""
        try:
            # Get tools for this server
            server_tools = []
            for tool_name, tool_info in self.tools.items():
                if tool_info.server_name == server_name:
                    # Convert to Gemini format
                    parameters = {
                        k: v for k, v in tool_info.schema.items()
                        if k not in ["additionalProperties", "$schema"]
                    }
                    
                    function_declaration = {
                        "name": tool_name,
                        "description": tool_info.description,
                        "parameters": parameters
                    }
                    
                    server_tools.append(types.Tool(function_declarations=[function_declaration]))
            
            if not server_tools:
                return f"❌ No tools available for server {server_name}"
            
            # Prepare prompt
            prompt = query
            if context:
                prompt = f"Context: {context}\n\nUser query: {query}"
            
            # Add server-specific instructions
            server_context = f"""
            You have access to {server_name} server tools. Please use these tools to answer the user's query.
            If the tools don't match the query, respond with "❌ UNABLE_TO_HANDLE" so we can try other servers.
            
            {prompt}
            """
            
            # Generate content with server-specific tools
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=server_context,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    tools=server_tools,
                ),
            )
            
            # Check if Gemini wants to call a function
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        function_call = part.function_call
                        tool_name = function_call.name
                        arguments = dict(function_call.args) if function_call.args else {}
                        
                        logger.info(f"Calling {tool_name} on server {server_name}")
                        
                        # Call the tool
                        tool_result = await self.call_tool(tool_name, arguments)
                        
                        # Get final response from Gemini
                        final_prompt = f"""
                        User question: {query}
                        Tool used: {tool_name}
                        Tool result: {tool_result}
                        
                        Please provide a helpful, natural response based on this information.
                        """
                        
                        final_response = self.gemini_client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=final_prompt
                        )
                        
                        return final_response.text if final_response.text else str(tool_result)
            
            # Check if Gemini indicated it can't handle this
            if response.text and "UNABLE_TO_HANDLE" in response.text:
                return "❌ Server cannot handle this query"
                
            # Return direct response if no function calls
            return response.text if response.text else "❌ No response generated"
            
        except Exception as e:
            logger.error(f"Error trying server {server_name}: {e}")
            return f"❌ Error with server {server_name}: {str(e)}"
    
    async def call_tool(self, tool_name: str, arguments: Dict) -> Any:
        """Call a specific MCP tool"""
        try:
            if tool_name not in self.tools:
                return f"❌ Tool '{tool_name}' not found"
            
            tool_info = self.tools[tool_name]
            session = tool_info.session
            original_name = tool_info.original_name
            
            logger.info(f"Calling tool {original_name} with args: {arguments}")
            
            result = await session.call_tool(original_name, arguments=arguments)
            return result.content[0].text if result.content else "No result"
            
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return f"❌ Error calling tool: {str(e)}"
    
    async def get_direct_gemini_response(self, query: str, context: Optional[str] = None) -> str:
        """Get a direct response from Gemini without MCP tools"""
        try:
            prompt = query
            if context:
                prompt = f"Context: {context}\n\nUser query: {query}"
            
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.7)
            )
            
            return response.text if response.text else "I couldn't generate a response."
            
        except Exception as e:
            logger.error(f"Error getting direct Gemini response: {e}")
            return f"❌ Error getting AI response: {str(e)}"
    
    def get_server_status(self) -> Dict[str, Any]:
        """Get status of all registered servers"""
        status = {
            "total_servers": len(self.servers),
            "connected_servers": sum(1 for s in self.servers.values() if s.status == ServerStatus.CONNECTED),
            "total_tools": len(self.tools),
            "servers": {}
        }
        
        for name, config in self.servers.items():
            server_tools = [t for t in self.tools.values() if t.server_name == name]
            status["servers"][name] = {
                "status": config.status.value,
                "description": config.description,
                "capabilities": config.capabilities,
                "tools_count": len(server_tools),
                "tools": [t.original_name for t in server_tools]
            }
        
        return status
    
    def list_available_tools(self) -> str:
        """List all available tools from connected servers"""
        if not self.tools:
            return "❌ No MCP tools available. Servers may not be connected."
        
        tools_by_server = {}
        for tool_name, tool_info in self.tools.items():
            server = tool_info.server_name
            if server not in tools_by_server:
                tools_by_server[server] = []
            tools_by_server[server].append({
                "name": tool_info.original_name,
                "description": tool_info.description
            })
        
        result = f"📋 Available MCP Tools ({len(self.tools)} total from {len(tools_by_server)} servers):\n\n"
        
        for server_name, tools in tools_by_server.items():
            config = self.servers.get(server_name)
            status_emoji = "✅" if config and config.status == ServerStatus.CONNECTED else "❌"
            result += f"{status_emoji} **{server_name.upper()} SERVER** ({len(tools)} tools)\n"
            result += f"   Capabilities: {', '.join(config.capabilities if config else ['unknown'])}\n"
            
            for tool in tools:
                result += f"   🛠️ {tool['name']}: {tool['description']}\n"
            result += "\n"
        
        return result

# Example usage and configuration
def create_default_router() -> IntelligentMCPRouter:
    """Create a router with default MCP server configurations"""
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not gemini_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    router = IntelligentMCPRouter(gemini_key)
    
    # Weather server configuration
    weather_config = MCPServerConfig(
        name="weather",
        command="C:\\Users\\arunk\\.local\\bin\\uv.exe",
        args=[
            "--directory",
            "c:\\Users\\arunk\\Puch_ai_clone\\weather-server",
            "run",
            "weather.py"
        ],
        env={},
        description="Weather forecasts and alerts",
        capabilities=["weather", "forecast", "temperature", "climate", "rain", "sunny", "cloudy"],
        priority=2
    )
    
    # Task management server configuration
    task_config = MCPServerConfig(
        name="task-master",
        command="npx",
        args=["-y", "--package=task-master-ai", "task-master-ai"],
        env={
            "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", ""),
            "PERPLEXITY_API_KEY": os.getenv("PERPLEXITY_API_KEY", ""),
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
            "GOOGLE_API_KEY": gemini_key
        },
        description="Task management and project planning",
        capabilities=["task", "todo", "project", "reminder", "schedule", "planning", "organize"],
        priority=1
    )
    
    # Register servers
    router.register_server(weather_config)
    router.register_server(task_config)
    
    return router

if __name__ == "__main__":
    async def test_router():
        router = create_default_router()
        
        # Connect to servers
        print("🔧 Connecting to MCP servers...")
        await router.connect_all_servers()
        
        # Show status
        print("\n📊 Server Status:")
        status = router.get_server_status()
        for name, info in status["servers"].items():
            print(f"  {name}: {info['status']} ({info['tools_count']} tools)")
        
        # Test queries
        test_queries = [
            "What's the weather in Tokyo?",
            "Create a task to learn Python",
            "Tell me a joke about programming",
            "Check weather in London and create a travel task"
        ]
        
        print("\n🧪 Testing intelligent routing:")
        for query in test_queries:
            print(f"\n💬 Query: {query}")
            response = await router.route_query(query)
            print(f"🤖 Response: {response[:200]}...")
    
    asyncio.run(test_router())
