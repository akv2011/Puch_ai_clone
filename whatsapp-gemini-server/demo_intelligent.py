#!/usr/bin/env python3
"""
Interactive Demo: Intelligent WhatsApp-Gemini MCP System
Showcases smart routing, fallback mechanisms, and multi-server coordination
"""

import asyncio
import os
import sys
from dotenv import load_dotenv
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

class DemoColors:
    """Terminal colors for better demo presentation"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_header(text):
    """Print a styled header"""
    print(f"\n{DemoColors.BOLD}{DemoColors.CYAN}{'='*60}{DemoColors.END}")
    print(f"{DemoColors.BOLD}{DemoColors.CYAN}{text.center(60)}{DemoColors.END}")
    print(f"{DemoColors.BOLD}{DemoColors.CYAN}{'='*60}{DemoColors.END}\n")

def print_section(text):
    """Print a styled section header"""
    print(f"\n{DemoColors.BOLD}{DemoColors.YELLOW}🔸 {text}{DemoColors.END}")
    print(f"{DemoColors.YELLOW}{'-'*50}{DemoColors.END}")

def print_query(query):
    """Print a user query"""
    print(f"\n{DemoColors.BOLD}{DemoColors.BLUE}👤 User:{DemoColors.END} {query}")

def print_ai_response(response):
    """Print AI response"""
    print(f"{DemoColors.BOLD}{DemoColors.GREEN}🤖 AI:{DemoColors.END} {response}")

def print_system_info(info):
    """Print system information"""
    print(f"{DemoColors.CYAN}ℹ️  {info}{DemoColors.END}")

async def demo_intelligent_routing():
    """Demonstrate intelligent routing capabilities"""
    try:
        print_header("INTELLIGENT MCP ROUTING DEMO")
        
        from whatsapp_gemini_intelligent import intelligent_manager, initialize_intelligent_connections
        
        print_section("System Initialization")
        print("🚀 Starting intelligent MCP system...")
        
        # Initialize connections
        success = await initialize_intelligent_connections()
        
        if not success:
            print(f"{DemoColors.RED}❌ Failed to initialize MCP connections{DemoColors.END}")
            return False
        
        print(f"{DemoColors.GREEN}✅ System initialized successfully!{DemoColors.END}")
        print_system_info(f"Connected servers: {len([s for s in intelligent_manager.servers.values() if s.status.value == 'connected'])}")
        print_system_info(f"Available tools: {len(intelligent_manager.tools)}")
        
        # Demo scenarios
        demo_scenarios = [
            {
                "title": "Weather Query Routing",
                "query": "What's the weather forecast for Tokyo, Japan?",
                "explanation": "This should automatically route to the weather MCP server"
            },
            {
                "title": "Task Management Routing", 
                "query": "Create a task to prepare for tomorrow's presentation",
                "explanation": "This should route to the task-master MCP server"
            },
            {
                "title": "Multi-Intent Query",
                "query": "Check the weather in London and create a task to pack warm clothes",
                "explanation": "This should use BOTH weather and task servers intelligently"
            },
            {
                "title": "General AI Query",
                "query": "Explain the concept of artificial intelligence in simple terms",
                "explanation": "This should use direct Gemini AI (no specific MCP server needed)"
            },
            {
                "title": "Fallback Scenario",
                "query": "What's the best recipe for chocolate chip cookies?",
                "explanation": "This will demonstrate fallback to general AI when no specialized server matches"
            }
        ]
        
        for i, scenario in enumerate(demo_scenarios, 1):
            print_section(f"Demo {i}: {scenario['title']}")
            
            print_system_info(scenario['explanation'])
            print_query(scenario['query'])
            
            # Show intent analysis
            best_servers = intelligent_manager.get_best_servers_for_query(scenario['query'])
            if best_servers:
                print_system_info(f"Intelligent analysis suggests: {', '.join(best_servers)}")
            else:
                print_system_info("No specific server match → will use direct Gemini")
            
            # Get response
            print(f"{DemoColors.YELLOW}🔄 Processing...{DemoColors.END}")
            start_time = time.time()
            
            try:
                response = await intelligent_manager.route_query_intelligently(scenario['query'])
                processing_time = time.time() - start_time
                
                print_ai_response(response[:300] + "..." if len(response) > 300 else response)
                print_system_info(f"Response time: {processing_time:.2f} seconds")
                print(f"{DemoColors.GREEN}✅ Demo {i} completed successfully{DemoColors.END}")
                
            except Exception as e:
                print(f"{DemoColors.RED}❌ Demo {i} failed: {e}{DemoColors.END}")
            
            # Wait between demos for better presentation
            await asyncio.sleep(1)
        
        return True
        
    except ImportError as e:
        print(f"{DemoColors.RED}❌ Import error: {e}{DemoColors.END}")
        print("Make sure to run setup_intelligent.ps1 first!")
        return False
    except Exception as e:
        print(f"{DemoColors.RED}❌ Demo failed: {e}{DemoColors.END}")
        return False

async def demo_fallback_resilience():
    """Demonstrate fallback and error resilience"""
    try:
        print_header("FALLBACK & RESILIENCE DEMO")
        
        from whatsapp_gemini_intelligent import intelligent_manager
        
        print_section("Fallback Mechanism Testing")
        
        # Test queries that should trigger fallbacks
        fallback_tests = [
            {
                "query": "How do I solve a Rubik's cube step by step?",
                "reason": "No specialized MCP server for puzzle solving"
            },
            {
                "query": "What's the best investment strategy for 2024?",
                "reason": "Financial advice not covered by current MCP servers"
            },
            {
                "query": "Translate 'Hello, how are you?' to Spanish",
                "reason": "Translation not in current server capabilities"
            }
        ]
        
        for i, test in enumerate(fallback_tests, 1):
            print(f"\n{DemoColors.BOLD}Fallback Test {i}:{DemoColors.END}")
            print_system_info(f"Reason: {test['reason']}")
            print_query(test['query'])
            
            try:
                response = await intelligent_manager.route_query_intelligently(test['query'])
                print_ai_response(response[:200] + "..." if len(response) > 200 else response)
                print(f"{DemoColors.GREEN}✅ Fallback handled gracefully{DemoColors.END}")
                
            except Exception as e:
                print(f"{DemoColors.RED}❌ Fallback failed: {e}{DemoColors.END}")
        
        return True
        
    except Exception as e:
        print(f"{DemoColors.RED}❌ Fallback demo failed: {e}{DemoColors.END}")
        return False

async def demo_whatsapp_integration():
    """Demonstrate WhatsApp integration with intelligent routing"""
    try:
        print_header("WHATSAPP INTEGRATION DEMO")
        
        # Check if Twilio is configured
        twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
        twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
        
        if not twilio_sid or not twilio_token:
            print_section("WhatsApp Configuration")
            print(f"{DemoColors.YELLOW}⚠️ Twilio credentials not configured{DemoColors.END}")
            print("To enable WhatsApp demo:")
            print("1. Set TWILIO_ACCOUNT_SID in .env")
            print("2. Set TWILIO_AUTH_TOKEN in .env")
            print("3. Configure WhatsApp sandbox at https://console.twilio.com/")
            return True
        
        from whatsapp_gemini_intelligent import send_whatsapp_message
        
        print_section("WhatsApp Intelligent Messaging")
        
        # Demo WhatsApp scenarios
        test_number = "+919360011424"  # Your test number
        
        whatsapp_demos = [
            {
                "scenario": "Weather via WhatsApp",
                "message": "What's the weather like in Mumbai today?",
                "expected": "Should route to weather server and send forecast"
            },
            {
                "scenario": "Task Creation via WhatsApp", 
                "message": "Remind me to call my dentist tomorrow at 2 PM",
                "expected": "Should route to task-master and create reminder"
            },
            {
                "scenario": "General Chat via WhatsApp",
                "message": "Tell me an interesting fact about space",
                "expected": "Should use direct Gemini for general knowledge"
            }
        ]
        
        print(f"📱 Sending intelligent test messages to: {test_number}")
        
        for demo in whatsapp_demos:
            print(f"\n{DemoColors.BOLD}📨 {demo['scenario']}{DemoColors.END}")
            print_system_info(demo['expected'])
            print_query(demo['message'])
            
            try:
                # This would use intelligent routing
                test_msg = f"🧠 Intelligent Demo: {demo['message']}"
                result = send_whatsapp_message(test_number, test_msg)
                
                if result.get("success"):
                    print(f"{DemoColors.GREEN}✅ Message sent successfully!{DemoColors.END}")
                    print_system_info(f"Message SID: {result.get('message_sid')}")
                else:
                    print(f"{DemoColors.RED}❌ Failed to send: {result.get('error')}{DemoColors.END}")
                    
            except Exception as e:
                print(f"{DemoColors.RED}❌ WhatsApp demo failed: {e}{DemoColors.END}")
            
            await asyncio.sleep(2)  # Rate limiting
        
        return True
        
    except Exception as e:
        print(f"{DemoColors.RED}❌ WhatsApp demo failed: {e}{DemoColors.END}")
        return False

async def demo_system_status():
    """Show comprehensive system status"""
    try:
        print_header("SYSTEM STATUS & CAPABILITIES")
        
        from whatsapp_gemini_intelligent import intelligent_manager, MCP_SERVERS
        
        print_section("Server Status Overview")
        
        total_servers = len(MCP_SERVERS)
        connected_servers = sum(1 for config in MCP_SERVERS.values() if config.status.value == 'connected')
        total_tools = len(intelligent_manager.tools)
        
        print(f"📊 System Statistics:")
        print(f"   • Total configured servers: {total_servers}")
        print(f"   • Connected servers: {DemoColors.GREEN}{connected_servers}{DemoColors.END}")
        print(f"   • Available tools: {DemoColors.GREEN}{total_tools}{DemoColors.END}")
        
        print_section("Server Details")
        
        for server_name, config in MCP_SERVERS.items():
            status_color = DemoColors.GREEN if config.status.value == 'connected' else DemoColors.RED
            status_emoji = "✅" if config.status.value == 'connected' else "❌"
            
            print(f"\n{status_emoji} {DemoColors.BOLD}{server_name.upper()}{DemoColors.END}")
            print(f"   Status: {status_color}{config.status.value}{DemoColors.END}")
            print(f"   Description: {config.description}")
            print(f"   Capabilities: {', '.join(config.capabilities)}")
            print(f"   Priority: {config.priority}")
            
            # Show tools for this server
            server_tools = [t for t in intelligent_manager.tools.values() if t["server"] == server_name]
            print(f"   Tools: {len(server_tools)}")
            
            if server_tools:
                for tool in server_tools[:2]:  # Show first 2 tools
                    print(f"     • {tool['original_name']}")
                if len(server_tools) > 2:
                    print(f"     • ... and {len(server_tools) - 2} more")
        
        print_section("Intelligent Routing Capabilities")
        
        capabilities = [
            "🧠 Automatic query intent analysis",
            "🎯 Smart server selection based on capabilities", 
            "🔄 Fallback to alternative servers when needed",
            "⚡ Multi-server coordination for complex queries",
            "🛡️ Enhanced error handling and recovery",
            "📱 WhatsApp integration with intelligent responses",
            "🔧 Real-time server status monitoring",
            "🎨 Natural language interface for all tools"
        ]
        
        for capability in capabilities:
            print(f"   {capability}")
        
        return True
        
    except Exception as e:
        print(f"{DemoColors.RED}❌ Status demo failed: {e}{DemoColors.END}")
        return False

async def interactive_demo():
    """Interactive demo where users can input their own queries"""
    try:
        print_header("INTERACTIVE INTELLIGENT ROUTING")
        
        from whatsapp_gemini_intelligent import intelligent_manager
        
        print_section("Try Your Own Queries!")
        print("Enter queries to see intelligent routing in action.")
        print("Examples:")
        print("  • 'Weather in Paris'")
        print("  • 'Create a task to study Python'") 
        print("  • 'Tell me about quantum computing'")
        print("  • Type 'quit' to exit")
        
        while True:
            try:
                user_input = input(f"\n{DemoColors.BOLD}{DemoColors.BLUE}Your query: {DemoColors.END}").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not user_input:
                    continue
                
                # Show analysis
                best_servers = intelligent_manager.get_best_servers_for_query(user_input)
                if best_servers:
                    print_system_info(f"Routing to: {', '.join(best_servers)}")
                else:
                    print_system_info("Using direct Gemini AI")
                
                # Get response
                print(f"{DemoColors.YELLOW}🔄 Processing...{DemoColors.END}")
                response = await intelligent_manager.route_query_intelligently(user_input)
                print_ai_response(response)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"{DemoColors.RED}❌ Error: {e}{DemoColors.END}")
        
        print(f"\n{DemoColors.GREEN}Thanks for trying the interactive demo!{DemoColors.END}")
        return True
        
    except Exception as e:
        print(f"{DemoColors.RED}❌ Interactive demo failed: {e}{DemoColors.END}")
        return False

async def main():
    """Run comprehensive demo of intelligent MCP system"""
    print_header("INTELLIGENT WHATSAPP-GEMINI MCP SYSTEM")
    print(f"{DemoColors.BOLD}{DemoColors.CYAN}🧠 Enhanced with Smart Routing & AI Orchestration{DemoColors.END}")
    
    # Environment check
    print_section("Environment Check")
    
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not gemini_key:
        print(f"{DemoColors.RED}❌ GEMINI_API_KEY not found{DemoColors.END}")
        print("Please set your Gemini API key in the .env file")
        return
    
    print(f"{DemoColors.GREEN}✅ Environment configured correctly{DemoColors.END}")
    
    # Run demo sections
    demos = [
        ("Intelligent Routing", demo_intelligent_routing),
        ("Fallback & Resilience", demo_fallback_resilience),
        ("System Status", demo_system_status),
        ("WhatsApp Integration", demo_whatsapp_integration),
        ("Interactive Demo", interactive_demo)
    ]
    
    for demo_name, demo_func in demos:
        try:
            print(f"\n{DemoColors.BOLD}Starting {demo_name}...{DemoColors.END}")
            success = await demo_func()
            
            if success:
                print(f"{DemoColors.GREEN}✅ {demo_name} completed successfully{DemoColors.END}")
            else:
                print(f"{DemoColors.YELLOW}⚠️ {demo_name} completed with warnings{DemoColors.END}")
                
        except Exception as e:
            print(f"{DemoColors.RED}❌ {demo_name} failed: {e}{DemoColors.END}")
    
    # Final summary
    print_header("DEMO COMPLETE")
    print(f"{DemoColors.BOLD}{DemoColors.GREEN}🎉 Intelligent MCP System Demo Finished!{DemoColors.END}")
    print("\n🌟 Key Features Demonstrated:")
    print("   ✅ Smart query analysis and automatic routing")
    print("   ✅ Multi-server coordination and tool selection")
    print("   ✅ Robust fallback mechanisms")
    print("   ✅ WhatsApp integration with intelligent responses") 
    print("   ✅ Real-time system monitoring and status")
    print("   ✅ Interactive AI assistance")
    
    print(f"\n📱 {DemoColors.BOLD}Next Steps:{DemoColors.END}")
    print("   1. Use this system in VS Code with MCP")
    print("   2. Integrate with your WhatsApp for AI assistance")
    print("   3. Add more MCP servers to expand capabilities")
    print("   4. Enjoy intelligent AI that knows when to use which tools!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{DemoColors.YELLOW}Demo interrupted by user{DemoColors.END}")
    except Exception as e:
        print(f"\n{DemoColors.RED}Demo failed: {e}{DemoColors.END}")
