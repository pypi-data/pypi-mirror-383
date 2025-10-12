#!/usr/bin/env python3
"""
Setup script for fully automated LogIQ monitoring.

This script helps set up the LogIQ CLI tool for fully automated monitoring
without requiring manual password prompts.
"""

import os
import sys
import getpass
from pathlib import Path

def setup_automated_monitoring():
    """Setup fully automated monitoring for LogIQ."""
    print("🔧 LogIQ Automated Monitoring Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("cli_tool.py").exists():
        print("❌ Error: cli_tool.py not found in current directory")
        print("   Please run this script from the aiagent directory")
        return False
    
    print("This script will help you set up fully automated monitoring.")
    print("You'll need to provide your LogIQ password once, and then monitoring")
    print("will run automatically without further prompts.\n")
    
    # Get password from user
    password = getpass.getpass("🔑 Enter your LogIQ password: ")
    
    if not password:
        print("❌ Error: Password cannot be empty")
        return False
    
    print("\n📋 Setup Steps:")
    print("1. Enabling automated monitoring in CLI tool...")
    
    # Enable automated monitoring
    import subprocess
    try:
        result = subprocess.run([
            sys.executable, "cli_tool.py", "monitor", "--dynamic", "--enable-auto"
        ], input=f"{password}\n", text=True, capture_output=True)
        
        if result.returncode == 0:
            print("✅ Automated monitoring enabled successfully!")
        else:
            print(f"❌ Failed to enable automated monitoring: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running CLI tool: {e}")
        return False
    
    print("\n2. Setting up environment variable...")
    
    # Set environment variable
    env_var_name = "LOGIQ_AUTO_PASSWORD"
    env_var_value = password
    
    print(f"\n🔧 To complete the setup, set the environment variable:")
    print(f"   Windows (PowerShell):")
    print(f"   $env:{env_var_name} = '{env_var_value}'")
    print(f"   ")
    print(f"   Windows (Command Prompt):")
    print(f"   set {env_var_name}={env_var_value}")
    print(f"   ")
    print(f"   Linux/macOS:")
    print(f"   export {env_var_name}='{env_var_value}'")
    
    print(f"\n💡 For permanent setup, add the above to your shell profile:")
    print(f"   - Windows: Add to environment variables in System Properties")
    print(f"   - Linux/macOS: Add to ~/.bashrc or ~/.zshrc")
    
    print(f"\n🚀 Once the environment variable is set, you can run:")
    print(f"   python cli_tool.py monitor --dynamic --interval 300")
    print(f"   ")
    print(f"   And it will run completely automatically!")
    
    return True

if __name__ == "__main__":
    setup_automated_monitoring()
