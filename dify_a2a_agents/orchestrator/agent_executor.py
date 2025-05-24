"""Orchestrator Agent Executor using Dify workflows and A2A protocol."""

import json
import asyncio
from typing import Dict, List, Any, Optional
from typing_extensions import override

import aiohttp
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message

from ..shared.dify_client import DifyA2AExecutor, DifyWorkflowClient
from ..config.agents import get_agent_config, get_all_agent_urls


class OrchestratorAgent(DifyA2AExecutor):
    """Orchestrator agent that routes queries and synthesizes responses."""
    
    def __init__(self, dify_client: DifyWorkflowClient):
        """Initialize orchestrator with Dify client and agent URLs."""
        super().__init__(dify_client)
        self.agent_urls = get_all_agent_urls()
        self.config = get_agent_config("orchestrator")
        
    async def route_query(self, user_input: str) -> Dict[str, Any]:
        """Determine which specialist agents to involve based on the query.
        
        Args:
            user_input: User's query
            
        Returns:
            Dictionary with routing decisions and context
        """
        # Use Dify workflow to analyze query and determine routing
        routing_context = {
            "available_agents": list(self.agent_urls.keys()),
            "agent_capabilities": {
                "research": "information gathering, web search, fact checking",
                "analysis": "data analysis, summarization, insights",
                "code": "code generation, programming, technical tasks"
            }
        }
        
        routing_result = await self.process_with_dify(
            self.config.dify_workflow_id,
            user_input,
            routing_context
        )
        
        # Parse the routing decision from Dify response
        try:
            # Expect Dify to return JSON with agent selections
            if routing_result.startswith("{"):
                routing_data = json.loads(routing_result)
            else:
                # Fallback: parse simple text response
                routing_data = {
                    "selected_agents": self._parse_agent_selection(routing_result),
                    "reasoning": routing_result
                }
        except json.JSONDecodeError:
            # Default routing based on keywords
            routing_data = self._default_routing(user_input)
        
        return routing_data
    
    def _parse_agent_selection(self, text: str) -> List[str]:
        """Parse agent selection from text response."""
        agents = []
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in ["research", "search", "find", "information"]):
            agents.append("research")
        if any(keyword in text_lower for keyword in ["analyze", "data", "summary", "insight"]):
            agents.append("analysis")
        if any(keyword in text_lower for keyword in ["code", "program", "script", "function"]):
            agents.append("code")
            
        return agents if agents else ["research"]  # Default to research if unclear
    
    def _default_routing(self, user_input: str) -> Dict[str, Any]:
        """Default routing logic based on keywords."""
        input_lower = user_input.lower()
        selected_agents = []
        
        # Keyword-based routing
        if any(keyword in input_lower for keyword in ["find", "search", "research", "information", "what is", "who is"]):
            selected_agents.append("research")
        if any(keyword in input_lower for keyword in ["analyze", "data", "summarize", "insights", "trends"]):
            selected_agents.append("analysis")
        if any(keyword in input_lower for keyword in ["code", "program", "script", "function", "algorithm"]):
            selected_agents.append("code")
        
        if not selected_agents:
            selected_agents = ["research"]  # Default to research
        
        return {
            "selected_agents": selected_agents,
            "reasoning": f"Routing based on keywords in: {user_input}"
        }
    
    async def query_agent(self, agent_name: str, query: str) -> str:
        """Send query to a specialist agent via A2A protocol.
        
        Args:
            agent_name: Name of the target agent
            query: Query to send
            
        Returns:
            Agent's response
        """
        if agent_name not in self.agent_urls:
            return f"Error: Agent '{agent_name}' not available"
        
        agent_url = self.agent_urls[agent_name]
        
        try:
            # A2A protocol communication
            async with aiohttp.ClientSession() as session:
                # Create task on the agent
                create_task_payload = {
                    "jsonrpc": "2.0",
                    "method": "CreateTask",
                    "params": {
                        "inputs": [{"text": query}],
                        "outputMode": "text"
                    },
                    "id": f"orchestrator-{agent_name}-{asyncio.get_event_loop().time()}"
                }
                
                async with session.post(
                    f"{agent_url.rstrip('/')}/",
                    json=create_task_payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status != 200:
                        return f"Error communicating with {agent_name}: HTTP {response.status}"
                    
                    result = await response.json()
                    
                    if "error" in result:
                        return f"Error from {agent_name}: {result['error']['message']}"
                    
                    # Extract task ID and get result
                    task_id = result.get("result", {}).get("taskId")
                    if not task_id:
                        return f"No task ID received from {agent_name}"
                    
                    # Get task result
                    get_result_payload = {
                        "jsonrpc": "2.0",
                        "method": "GetTaskResult",
                        "params": {"taskId": task_id},
                        "id": f"get-result-{task_id}"
                    }
                    
                    async with session.post(
                        f"{agent_url.rstrip('/')}/",
                        json=get_result_payload,
                        headers={"Content-Type": "application/json"}
                    ) as result_response:
                        if result_response.status != 200:
                            return f"Error getting result from {agent_name}: HTTP {result_response.status}"
                        
                        result_data = await result_response.json()
                        
                        if "error" in result_data:
                            return f"Error getting result from {agent_name}: {result_data['error']['message']}"
                        
                        # Extract the response text
                        events = result_data.get("result", {}).get("events", [])
                        response_text = ""
                        
                        for event in events:
                            if event.get("type") == "AgentMessage" and event.get("data", {}).get("text"):
                                response_text += event["data"]["text"]
                        
                        return response_text or f"No response from {agent_name}"
        
        except Exception as e:
            return f"Error communicating with {agent_name}: {str(e)}"
    
    async def synthesize_responses(self, user_input: str, agent_responses: Dict[str, str]) -> str:
        """Synthesize responses from multiple agents into a coherent answer.
        
        Args:
            user_input: Original user query
            agent_responses: Dictionary of agent responses
            
        Returns:
            Synthesized final response
        """
        synthesis_context = {
            "original_query": user_input,
            "agent_responses": agent_responses,
            "agents_involved": list(agent_responses.keys())
        }
        
        # Use Dify workflow for synthesis
        final_response = await self.process_with_dify(
            self.config.dify_workflow_id,
            f"Synthesize the following responses to '{user_input}': {json.dumps(agent_responses)}",
            synthesis_context
        )
        
        return final_response


class OrchestratorAgentExecutor(AgentExecutor):
    """A2A Agent Executor for the Orchestrator."""
    
    def __init__(self, dify_client: DifyWorkflowClient):
        """Initialize with Dify client."""
        self.orchestrator = OrchestratorAgent(dify_client)
    
    @override
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Execute orchestrator logic for incoming requests."""
        # Extract user input from context
        user_input = ""
        for input_item in context.inputs:
            if hasattr(input_item, 'text') and input_item.text:
                user_input = input_item.text
                break
        
        if not user_input:
            event_queue.enqueue_event(
                new_agent_text_message("Error: No text input provided")
            )
            return
        
        try:
            # Step 1: Route the query
            event_queue.enqueue_event(
                new_agent_text_message("🤔 Analyzing your request and determining the best approach...")
            )
            
            routing_data = await self.orchestrator.route_query(user_input)
            selected_agents = routing_data.get("selected_agents", [])
            
            event_queue.enqueue_event(
                new_agent_text_message(f"📋 Routing to: {', '.join(selected_agents)}")
            )
            
            # Step 2: Query selected agents
            agent_responses = {}
            
            for agent_name in selected_agents:
                if agent_name == "orchestrator":
                    continue  # Skip self
                
                event_queue.enqueue_event(
                    new_agent_text_message(f"🔍 Consulting {agent_name} agent...")
                )
                
                response = await self.orchestrator.query_agent(agent_name, user_input)
                agent_responses[agent_name] = response
                
                # Stream partial response
                event_queue.enqueue_event(
                    new_agent_text_message(f"✅ {agent_name.title()} Agent Response:\n{response}\n")
                )
            
            # Step 3: Synthesize responses
            if len(agent_responses) > 1:
                event_queue.enqueue_event(
                    new_agent_text_message("🔄 Synthesizing responses...")
                )
                
                final_response = await self.orchestrator.synthesize_responses(
                    user_input, agent_responses
                )
                
                event_queue.enqueue_event(
                    new_agent_text_message(f"📝 Final Synthesized Response:\n{final_response}")
                )
            elif len(agent_responses) == 1:
                # Single agent response, just clean it up
                agent_name, response = next(iter(agent_responses.items()))
                event_queue.enqueue_event(
                    new_agent_text_message(f"✨ Complete response from {agent_name} agent.")
                )
            else:
                event_queue.enqueue_event(
                    new_agent_text_message("❌ No agents were able to process the request.")
                )
        
        except Exception as e:
            event_queue.enqueue_event(
                new_agent_text_message(f"Error processing request: {str(e)}")
            )
    
    @override
    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        """Cancel the orchestrator execution."""
        await self.orchestrator.cleanup()
        event_queue.enqueue_event(
            new_agent_text_message("Orchestrator execution cancelled.")
        )
