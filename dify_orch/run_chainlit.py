#!/usr/bin/env python3
"""
Simple script to run the Chainlit Dify Orchestrator Web UI
"""

import subprocess
import sys
import os

def main():
    """Run the Chainlit application."""
    print("🚀 Starting Chainlit Dify Orchestrator Web UI...")
    print("📁 Working directory:", os.getcwd())
    print("📝 Make sure your .env file is configured!")
    print("🌐 The web interface will open automatically at http://localhost:8000")
    print("-" * 60)
    
    try:
        # Run chainlit with the app file
        subprocess.run([
            sys.executable, "-m", "chainlit", "run", "chainlit_app.py", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--watch"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down Chainlit app...")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Chainlit: {e}")
        print("\n💡 Make sure chainlit is installed:")
        print("   pip install chainlit")
    except FileNotFoundError:
        print("❌ Chainlit not found. Please install it first:")
        print("   pip install chainlit")

if __name__ == "__main__":
    main()
