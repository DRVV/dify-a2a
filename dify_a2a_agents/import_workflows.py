#!/usr/bin/env python3
"""
Import Dify workflows for A2A Multi-Agent System
Each workflow requires its own API key from Dify.
"""

import json
import os
import sys
import requests
from pathlib import Path
from typing import Dict, Optional, Tuple


class DifyWorkflowImporter:
    def __init__(self, base_url: str = "http://localhost"):
        self.base_url = base_url.rstrip('/')
        # Remove /v1 from base_url for console API access if present
        console_base = self.base_url
        if console_base.endswith('/v1'):
            console_base = console_base[:-3]
        
        # Try multiple possible import endpoints
        self.import_endpoints = [
            f"{console_base}/console/api/apps/import",
            f"{console_base}/api/apps/import", 
            f"{console_base}/console/api/apps",
            f"{console_base}/api/apps",
            f"{console_base}/console/api/app/import",
            f"{console_base}/api/app/import"
        ]
        self.workflow_ids = {}
        self.api_keys = {}
        
    def import_workflow(self, workflow_path: str, workflow_name: str, api_key: str) -> Optional[str]:
        """Import a workflow with its specific API key and return the workflow ID"""
        try:
            # Read workflow JSON with UTF-8 encoding
            with open(workflow_path, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)
            
            # Prepare headers
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            print(f"Importing {workflow_name} workflow...")
            
            # Try each endpoint until one works
            last_error = None
            for i, import_url in enumerate(self.import_endpoints):
                try:
                    print(f"  Trying endpoint {i+1}/{len(self.import_endpoints)}: {import_url}")
                    
                    # Make API request
                    response = requests.post(
                        import_url,
                        headers=headers,
                        json=workflow_data,
                        timeout=30
                    )
                    
                    if response.status_code == 200 or response.status_code == 201:
                        result = response.json()
                        # Extract workflow ID from response
                        workflow_id = result.get('app', {}).get('id') or result.get('id')
                        if workflow_id:
                            print(f"✅ Successfully imported {workflow_name}: {workflow_id}")
                            return workflow_id
                        else:
                            print(f"⚠️  Import successful but no ID found in response for {workflow_name}")
                            print(f"Response: {json.dumps(result, indent=2)}")
                            return None
                    elif response.status_code == 404:
                        print(f"  Endpoint not found (404), trying next...")
                        continue
                    else:
                        print(f"  Failed with status {response.status_code}: {response.text[:200]}")
                        last_error = f"Status {response.status_code}: {response.text}"
                        continue
                        
                except requests.exceptions.RequestException as e:
                    print(f"  Network error: {str(e)[:100]}")
                    last_error = str(e)
                    continue
            
            # If we get here, all endpoints failed
            print(f"❌ Failed to import {workflow_name} using any endpoint")
            if last_error:
                print(f"Last error: {last_error}")
            return None
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON error reading {workflow_path}: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error importing {workflow_name}: {e}")
            return None
    
    def collect_api_keys(self) -> bool:
        """Collect API keys for each agent from user input or environment"""
        agents = [
            ("orchestrator", "ORCHESTRATOR_API_KEY", "Orchestrator Agent"),
            ("research", "RESEARCH_API_KEY", "Research Agent"),
            ("analysis", "ANALYSIS_API_KEY", "Analysis Agent"),
            ("code", "CODE_API_KEY", "Code Agent")
        ]
        
        print("🔑 API Key Collection")
        print("Each agent workflow requires its own API key from Dify.")
        print("You can find API keys in Dify Console > Apps > [App Name] > API Access")
        print("=" * 60)
        
        for agent_name, env_var, display_name in agents:
            # Try to get from environment first
            api_key = os.environ.get(env_var)
            
            if api_key and api_key != "your_" + agent_name.lower() + "_api_key":
                print(f"✅ Found {display_name} API key in environment")
                self.api_keys[agent_name] = api_key
            else:
                # Prompt user for API key
                while True:
                    api_key = input(f"Enter API key for {display_name}: ").strip()
                    if api_key:
                        self.api_keys[agent_name] = api_key
                        break
                    else:
                        print("❌ API key cannot be empty. Please try again.")
        
        print(f"\n✅ Collected API keys for {len(self.api_keys)} agents")
        return len(self.api_keys) == len(agents)
    
    def import_all_workflows(self) -> bool:
        """Import all workflows with their respective API keys"""
        workflows = [
            ("workflows/orchestrator_workflow.json", "orchestrator", "ORCHESTRATOR_WORKFLOW_ID"),
            ("workflows/research_workflow.json", "research", "RESEARCH_WORKFLOW_ID"),
            ("workflows/analysis_workflow.json", "analysis", "ANALYSIS_WORKFLOW_ID"),
            ("workflows/code_workflow.json", "code", "CODE_WORKFLOW_ID")
        ]
        
        print("\n🚀 Starting workflow import process...")
        print(f"Target Dify instance: {self.base_url}")
        print("=" * 60)
        
        success_count = 0
        for workflow_path, agent_name, workflow_id_env in workflows:
            if not os.path.exists(workflow_path):
                print(f"❌ Workflow file not found: {workflow_path}")
                continue
            
            if agent_name not in self.api_keys:
                print(f"❌ No API key found for {agent_name} agent")
                continue
                
            api_key = self.api_keys[agent_name]
            workflow_id = self.import_workflow(workflow_path, agent_name, api_key)
            
            if workflow_id:
                self.workflow_ids[workflow_id_env] = workflow_id
                success_count += 1
            
            print()  # Empty line for readability
        
        print("=" * 60)
        print(f"Import completed: {success_count}/{len(workflows)} workflows imported successfully")
        
        if self.workflow_ids:
            self.update_env_file()
        
        return success_count == len(workflows)
    
    def update_env_file(self):
        """Update .env file with workflow IDs and API keys"""
        env_path = ".env"
        env_example_path = ".env.example"
        
        # Read existing .env or create from .env.example
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                env_content = f.read()
        elif os.path.exists(env_example_path):
            with open(env_example_path, 'r') as f:
                env_content = f.read()
            print(f"📝 Created .env from {env_example_path}")
        else:
            env_content = ""
            print("📝 Creating new .env file")
        
        # Prepare all variables to update
        all_updates = {}
        
        # Add workflow IDs
        all_updates.update(self.workflow_ids)
        
        # Add API keys
        api_key_mapping = {
            "orchestrator": "ORCHESTRATOR_API_KEY",
            "research": "RESEARCH_API_KEY", 
            "analysis": "ANALYSIS_API_KEY",
            "code": "CODE_API_KEY"
        }
        
        for agent_name, api_key in self.api_keys.items():
            if agent_name in api_key_mapping:
                all_updates[api_key_mapping[agent_name]] = api_key
        
        # Update environment content
        lines = env_content.split('\n')
        updated_lines = []
        updated_vars = set()
        
        for line in lines:
            line_updated = False
            for env_var, value in all_updates.items():
                if line.startswith(f"{env_var}=") or line.startswith(f"#{env_var}="):
                    updated_lines.append(f"{env_var}={value}")
                    updated_vars.add(env_var)
                    line_updated = True
                    break
            
            if not line_updated:
                updated_lines.append(line)
        
        # Add any missing variables
        for env_var, value in all_updates.items():
            if env_var not in updated_vars:
                updated_lines.append(f"{env_var}={value}")
        
        # Write updated .env file
        with open(env_path, 'w') as f:
            f.write('\n'.join(updated_lines))
        
        print(f"\n📝 Updated {env_path} with the following:")
        print("Workflow IDs:")
        for env_var, workflow_id in self.workflow_ids.items():
            print(f"   {env_var}={workflow_id}")
        
        print("API Keys:")
        for agent_name, env_var in api_key_mapping.items():
            if agent_name in self.api_keys:
                masked_key = self.api_keys[agent_name][:8] + "..." + self.api_keys[agent_name][-4:] if len(self.api_keys[agent_name]) > 12 else "***"
                print(f"   {env_var}={masked_key}")


def check_dify_connectivity(base_url: str) -> bool:
    """Check if Dify instance is accessible"""
    # Extract the root URL for health check (remove /v1 if present)
    root_url = base_url.rstrip('/')
    if root_url.endswith('/v1'):
        root_url = root_url[:-3]
    
    # Try multiple common health check endpoints
    health_endpoints = [
        f"{root_url}/health",
        f"{root_url}/api/health", 
        f"{root_url}/console/api/health",
        f"{root_url}"  # Just try the root URL
    ]
    
    print(f"🔍 Checking Dify connectivity...")
    
    for health_url in health_endpoints:
        try:
            response = requests.get(health_url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Dify instance is accessible at {root_url}")
                return True
            elif response.status_code in [401, 403]:
                # Authentication required but server is responding
                print(f"✅ Dify instance is accessible at {root_url} (auth required)")
                return True
                
        except requests.exceptions.RequestException:
            continue
    
    print(f"⚠️  Warning: Could not verify Dify connectivity at {root_url}")
    print("This might be normal if Dify doesn't expose a public health endpoint.")
    return False


def main():
    """Main function"""
    print("🤖 Dify A2A Multi-Agent Workflow Importer")
    print("This tool imports workflows for each agent with their individual API keys")
    print("=" * 70)
    
    # Get base URL
    base_url = os.environ.get('DIFY_BASE_URL', 'http://localhost')
    custom_url = input(f"Dify base URL (default: {base_url}): ").strip()
    if custom_url:
        base_url = custom_url
    
    # Verify Dify is accessible
    if not check_dify_connectivity(base_url):
        continue_anyway = input("Continue anyway? (y/N): ").strip().lower()
        if continue_anyway != 'y':
            print("❌ Exiting due to connectivity issues")
            sys.exit(1)
    
    # Create importer and collect API keys
    importer = DifyWorkflowImporter(base_url)
    
    if not importer.collect_api_keys():
        print("❌ Failed to collect all required API keys")
        sys.exit(1)
    
    # Import workflows
    success = importer.import_all_workflows()
    
    if success:
        print("\n🎉 All workflows imported successfully!")
        print("\nNext steps:")
        print("1. Verify workflows in Dify dashboard")
        print("2. Configure LLM providers if needed") 
        print("3. Test workflows individually")
        print("4. Run the A2A agent system: python start_agents.py")
    else:
        print("\n⚠️  Some workflows failed to import. Please check the errors above.")
        print("Common issues:")
        print("- Incorrect API keys")
        print("- Dify instance not running or accessible")
        print("- Invalid workflow JSON files")
        print("- Network connectivity problems")
        print("\nTroubleshooting:")
        print("1. Verify API keys in Dify Console > Apps > [App Name] > API Access")
        print("2. Check that Dify is running and accessible")
        print("3. Review workflow JSON files for syntax errors")


if __name__ == "__main__":
    main()
