"""Dify API client for interacting with Dify workflows from A2A agents."""

import asyncio
import json
import uuid
from typing import Any, Dict, List, Optional

import aiohttp


class DifyWorkflowClient:
    """Client for interacting with Dify workflows via API."""
    
    def __init__(self, base_url: str = "http://localhost/v1", api_key: str = ""):
        """Initialize the Dify client.
        
        Args:
            base_url: Dify API base URL
            api_key: Dify API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self.session is None or self.session.closed:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def close(self):
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def run_workflow(
        self, 
        workflow_id: str, 
        inputs: Dict[str, Any],
        user_id: str = "a2a-agent"
    ) -> Dict[str, Any]:
        """Execute a Dify workflow.
        
        Args:
            workflow_id: ID of the workflow to run
            inputs: Input parameters for the workflow
            user_id: User identifier for the request
            
        Returns:
            Workflow execution result
        """
        session = await self._get_session()
        
        payload = {
            "inputs": inputs,
            "response_mode": "blocking",
            "user": user_id
        }
        
        url = f"{self.base_url}/workflows/run"
        
        async with session.post(url, json=payload) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Dify API error {response.status}: {error_text}")
            
            return await response.json()
    
    async def chat_with_app(
        self,
        app_id: str,
        query: str,
        conversation_id: Optional[str] = None,
        user_id: str = "a2a-agent"
    ) -> Dict[str, Any]:
        """Chat with a Dify chatflow app.
        
        Args:
            app_id: ID of the chat app
            query: User query/message
            conversation_id: Optional conversation ID for continuity
            user_id: User identifier for the request
            
        Returns:
            Chat response
        """
        session = await self._get_session()
        
        payload = {
            "inputs": {},
            "query": query,
            "response_mode": "blocking",
            "user": user_id
        }
        
        if conversation_id:
            payload["conversation_id"] = conversation_id
        
        url = f"{self.base_url}/chat-messages"
        
        async with session.post(url, json=payload) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Dify API error {response.status}: {error_text}")
            
            return await response.json()


class DifyA2AExecutor:
    """Base class for A2A agent executors that use Dify workflows."""
    
    def __init__(self, dify_client: DifyWorkflowClient):
        """Initialize with Dify client.
        
        Args:
            dify_client: Configured Dify workflow client
        """
        self.dify_client = dify_client
    
    async def process_with_dify(
        self,
        workflow_id: str,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Process user input using a Dify workflow.
        
        Args:
            workflow_id: ID of the Dify workflow to execute
            user_input: User's input text
            context: Additional context for the workflow
            
        Returns:
            Processed response text
        """
        inputs = {
            "user_input": user_input,
            **(context or {})
        }
        
        try:
            result = await self.dify_client.run_workflow(workflow_id, inputs)
            
            # Extract the main output from Dify response
            if "data" in result and "outputs" in result["data"]:
                outputs = result["data"]["outputs"]
                # Return the first output value or concatenate all text outputs
                if isinstance(outputs, dict):
                    for key, value in outputs.items():
                        if isinstance(value, str) and value.strip():
                            return value.strip()
                    return str(outputs)
                elif isinstance(outputs, str):
                    return outputs.strip()
            
            # Fallback to raw result
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error executing Dify workflow: {str(e)}"
    
    async def cleanup(self):
        """Cleanup resources."""
        await self.dify_client.close()
