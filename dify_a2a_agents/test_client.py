"""Test client for the Dify A2A Multi-Agent System."""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any


class A2ATestClient:
    """Test client for communicating with A2A agents."""
    
    def __init__(self, orchestrator_url: str = "http://localhost:9001"):
        """Initialize the test client.
        
        Args:
            orchestrator_url: URL of the orchestrator agent
        """
        self.orchestrator_url = orchestrator_url.rstrip('/')
    
    async def send_request(self, message: str) -> Dict[str, Any]:
        """Send a request to the orchestrator agent.
        
        Args:
            message: Message to send
            
        Returns:
            Response from the agent
        """
        async with aiohttp.ClientSession() as session:
            # Create task
            create_payload = {
                "jsonrpc": "2.0",
                "method": "CreateTask",
                "params": {
                    "inputs": [{"text": message}],
                    "outputMode": "text"
                },
                "id": f"test-{int(time.time())}"
            }
            
            print(f"📤 Sending request: {message}")
            
            async with session.post(
                f"{self.orchestrator_url}/",
                json=create_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    return {"error": f"HTTP {response.status}: {await response.text()}"}
                
                result = await response.json()
                
                if "error" in result:
                    return {"error": result["error"]["message"]}
                
                task_id = result.get("result", {}).get("taskId")
                if not task_id:
                    return {"error": "No task ID received"}
                
                # Get task result
                return await self._get_task_result(session, task_id)
    
    async def _get_task_result(self, session: aiohttp.ClientSession, task_id: str) -> Dict[str, Any]:
        """Get the result of a task.
        
        Args:
            session: HTTP session
            task_id: Task ID to query
            
        Returns:
            Task result
        """
        get_result_payload = {
            "jsonrpc": "2.0",
            "method": "GetTaskResult",
            "params": {"taskId": task_id},
            "id": f"get-result-{task_id}"
        }
        
        print(f"🔄 Getting result for task: {task_id}")
        
        # Poll for result (A2A tasks might take time)
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts:
            async with session.post(
                f"{self.orchestrator_url}/",
                json=get_result_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    return {"error": f"HTTP {response.status}: {await response.text()}"}
                
                result = await response.json()
                
                if "error" in result:
                    return {"error": result["error"]["message"]}
                
                task_result = result.get("result", {})
                events = task_result.get("events", [])
                
                if events:
                    # Extract and format the response
                    full_response = ""
                    for event in events:
                        if event.get("type") == "AgentMessage":
                            text = event.get("data", {}).get("text", "")
                            if text:
                                full_response += text + "\n"
                    
                    return {
                        "success": True,
                        "response": full_response.strip(),
                        "task_id": task_id,
                        "events": events
                    }
                
                attempt += 1
                await asyncio.sleep(1)  # Wait 1 second before retrying
        
        return {"error": "Timeout waiting for task result"}
    
    async def test_scenarios(self):
        """Run various test scenarios."""
        test_cases = [
            {
                "name": "Research Query",
                "message": "Find information about the latest developments in artificial intelligence",
                "description": "Tests research agent routing and information gathering"
            },
            {
                "name": "Analysis Request",
                "message": "Analyze the trends in AI adoption across different industries",
                "description": "Tests analysis agent for data processing and insights"
            },
            {
                "name": "Code Generation",
                "message": "Write a Python function to calculate the Fibonacci sequence",
                "description": "Tests code agent for programming tasks"
            },
            {
                "name": "Multi-Agent Collaboration",
                "message": "Research current AI trends, analyze the data, and write code to visualize the findings",
                "description": "Tests orchestrator coordination across multiple agents"
            },
            {
                "name": "Summarization Task",
                "message": "Summarize the key points of machine learning advancements in 2024",
                "description": "Tests analysis agent's summarization capabilities"
            }
        ]
        
        print("🧪 Starting A2A Multi-Agent System Tests")
        print("=" * 60)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 Test {i}: {test_case['name']}")
            print(f"📝 Description: {test_case['description']}")
            print(f"❓ Query: {test_case['message']}")
            print("-" * 40)
            
            start_time = time.time()
            result = await self.send_request(test_case['message'])
            end_time = time.time()
            
            if result.get("success"):
                print(f"✅ Success (took {end_time - start_time:.1f}s)")
                print(f"📄 Response:\n{result['response']}")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
            print("-" * 40)
            
            # Wait between tests
            await asyncio.sleep(2)
        
        print("\n🎯 Test suite completed!")
    
    async def interactive_mode(self):
        """Run in interactive mode for manual testing."""
        print("🤖 Interactive A2A Multi-Agent System")
        print("Type your queries below. Type 'quit' to exit.")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                print("🤔 Processing...")
                result = await self.send_request(user_input)
                
                if result.get("success"):
                    print(f"🤖 Agent System:\n{result['response']}")
                else:
                    print(f"❌ Error: {result.get('error', 'Unknown error')}")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


async def main():
    """Main test function."""
    import sys
    
    client = A2ATestClient()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        await client.interactive_mode()
    else:
        await client.test_scenarios()


if __name__ == "__main__":
    asyncio.run(main())
