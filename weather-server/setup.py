#!/usr/bin/env python3
"""
Setup script for the Weather MCP Server
"""
import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def main():
    """Main setup function."""
    print("🌤️  Setting up Weather MCP Server")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("weather.py"):
        print("❌ Please run this script from the weather-server directory")
        sys.exit(1)
    
    # Install uv if not present
    print("Checking for uv package manager...")
    uv_check = subprocess.run("uv --version", shell=True, capture_output=True)
    if uv_check.returncode != 0:
        print("Installing uv package manager...")
        if sys.platform == "win32":
            run_command(
                'powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"',
                "Installing uv on Windows"
            )
        else:
            run_command(
                "curl -LsSf https://astral.sh/uv/install.sh | sh",
                "Installing uv on Unix"
            )
        print("⚠️  Please restart your terminal and run this script again to use uv")
        return
    
    # Create virtual environment
    run_command("uv venv", "Creating virtual environment")
    
    # Install dependencies
    run_command("uv add mcp httpx", "Installing dependencies")
    
    print("\n🎉 Setup completed successfully!")
    print("\nTo run the server:")
    print("  uv run weather.py")
    print("\nTo configure with Claude Desktop, add this to your claude_desktop_config.json:")
    print(f'''
  "weather": {{
    "command": "uv",
    "args": [
      "--directory",
      "{os.path.abspath('.')}",
      "run",
      "weather.py"
    ]
  }}
''')

if __name__ == "__main__":
    main()
