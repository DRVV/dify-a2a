"""Research Agent A2A Server."""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

from agent_executor import ResearchAgentExecutor
from ..shared.dify_client import DifyWorkflowClient
from ..config.agents import get_agent_config


def create_research_server():
    """Create and configure the research A2A server."""
    
    # Get configuration
    config = get_agent_config("research")
    
    # Create Dify client
    dify_client = DifyWorkflowClient(
        base_url=config.dify_base_url,
        api_key=config.dify_api_key
    )
    
    # Create skills from configuration
    skills = []
    for skill_config in config.skills:
        skill = AgentSkill(
            id=skill_config["id"],
            name=skill_config["name"],
            description=skill_config["description"],
            tags=skill_config.get("tags", []),
            examples=skill_config.get("examples", [])
        )
        skills.append(skill)
    
    # Create agent card
    agent_card = AgentCard(
        name=config.name,
        description=config.description,
        url=f"http://{config.host}:{config.port}/",
        version="1.0.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=skills
    )
    
    # Create request handler
    request_handler = DefaultRequestHandler(
        agent_executor=ResearchAgentExecutor(dify_client),
        task_store=InMemoryTaskStore()
    )
    
    # Create A2A server
    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler
    )
    
    return server, config


if __name__ == "__main__":
    import uvicorn
    
    server, config = create_research_server()
    
    print(f"🔍 Starting Research Agent at http://{config.host}:{config.port}")
    print(f"📋 Agent Card: {config.name}")
    print(f"🔧 Skills: {[skill['name'] for skill in config.skills]}")
    
    uvicorn.run(
        server.build(),
        host=config.host,
        port=config.port,
        log_level="info"
    )
