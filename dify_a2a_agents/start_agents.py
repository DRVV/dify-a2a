"""Multi-agent launcher script for Dify A2A system."""

import asyncio
import subprocess
import sys
import time
import os
from pathlib import Path

# Add project to path
sys.path.append(str(Path(__file__).parent))

from config.agents import AGENTS_CONFIG


class AgentLauncher:
    """Manages launching and monitoring A2A agents."""
    
    def __init__(self):
        self.processes = {}
        self.base_dir = Path(__file__).parent
    
    def start_agent(self, agent_name: str) -> subprocess.Popen:
        """Start a single agent."""
        agent_dir = self.base_dir / agent_name
        if agent_name == "research":
            agent_dir = self.base_dir / "research_agent"
        elif agent_name == "analysis":
            agent_dir = self.base_dir / "analysis_agent"
        elif agent_name == "code":
            agent_dir = self.base_dir / "code_agent"
        
        server_script = agent_dir / "server.py"
        
        if not server_script.exists():
            print(f"❌ Server script not found for {agent_name}: {server_script}")
            return None
        
        print(f"🚀 Starting {agent_name} agent...")
        
        # Start the agent process
        process = subprocess.Popen(
            [sys.executable, str(server_script)],
            cwd=str(agent_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        return process
    
    def start_all_agents(self):
        """Start all configured agents."""
        print("🎯 Starting Dify A2A Multi-Agent System")
        print("=" * 50)
        
        # Start agents in order (orchestrator last since it needs others)
        agent_order = ["research", "analysis", "code", "orchestrator"]
        
        for agent_name in agent_order:
            if agent_name in AGENTS_CONFIG:
                process = self.start_agent(agent_name)
                if process:
                    self.processes[agent_name] = process
                    config = AGENTS_CONFIG[agent_name]
                    print(f"✅ {agent_name.title()} Agent started on port {config.port}")
                    
                    # Wait a moment between starts
                    time.sleep(1)
                else:
                    print(f"❌ Failed to start {agent_name} agent")
        
        if self.processes:
            print("\n🎉 All agents started successfully!")
            print("\nAgent URLs:")
            for agent_name, process in self.processes.items():
                config = AGENTS_CONFIG[agent_name]
                print(f"  {agent_name.title()}: http://localhost:{config.port}/")
            
            print("\n📋 To test the system:")
            print("  python test_client.py")
            print("\n⏹️  To stop all agents: Ctrl+C")
            
            self.monitor_agents()
        else:
            print("❌ No agents started successfully")
    
    def monitor_agents(self):
        """Monitor running agents."""
        try:
            while True:
                # Check if any processes have died
                for agent_name, process in list(self.processes.items()):
                    if process.poll() is not None:
                        print(f"⚠️  {agent_name} agent stopped")
                        del self.processes[agent_name]
                
                if not self.processes:
                    print("❌ All agents have stopped")
                    break
                
                time.sleep(5)  # Check every 5 seconds
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping all agents...")
            self.stop_all_agents()
    
    def stop_all_agents(self):
        """Stop all running agents."""
        for agent_name, process in self.processes.items():
            print(f"⏹️  Stopping {agent_name} agent...")
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"🔨 Force killing {agent_name} agent...")
                process.kill()
        
        self.processes.clear()
        print("✅ All agents stopped")


def main():
    """Main launcher function."""
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️  python-dotenv not installed. Environment variables from .env won't be loaded.")
    
    # Check if A2A SDK is installed
    try:
        import a2a
    except ImportError:
        print("❌ A2A SDK not installed. Please install requirements:")
        print("   pip install a2a-sdk")
        sys.exit(1)
    
    # Verify Dify configuration
    # Check if agent-specific API keys are configured
    missing_keys = []
    for agent_name, config in AGENTS_CONFIG.items():
        if not config.dify_api_key:
            missing_keys.append(f"{agent_name.upper()}_API_KEY")
    
    if missing_keys:
        print(f"⚠️  Missing API keys: {', '.join(missing_keys)}")
        print("   Please copy .env.example to .env and configure agent-specific API keys.")
    
    launcher = AgentLauncher()
    launcher.start_all_agents()


if __name__ == "__main__":
    main()
