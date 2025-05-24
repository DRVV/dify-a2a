"""Agent configuration for the Dify A2A Multi-Agent System."""

from dataclasses import dataclass
from typing import Dict, List
import os


@dataclass
class AgentConfig:
    """Configuration for a single agent."""
    name: str
    description: str
    port: int
    dify_workflow_id: str
    dify_api_key: str
    skills: List[Dict[str, str]]
    host: str = "0.0.0.0"
    dify_base_url: str = "http://localhost/v1"


# Agent configurations
AGENTS_CONFIG = {
    "orchestrator": AgentConfig(
        name="Orchestrator Agent",
        description="Main orchestrator that routes queries to specialized agents and synthesizes responses",
        port=9001,
        dify_workflow_id=os.getenv("ORCHESTRATOR_WORKFLOW_ID", ""),
        dify_api_key=os.getenv("ORCHESTRATOR_API_KEY", ""),
        skills=[
            {
                "id": "route_query",
                "name": "Route Query",
                "description": "Analyzes user queries and routes them to appropriate specialist agents",
                "tags": ["routing", "orchestration", "delegation"],
                "examples": ["Find information about AI trends", "Analyze this dataset", "Generate Python code for data processing"]
            },
            {
                "id": "synthesize_response",
                "name": "Synthesize Response",
                "description": "Combines responses from multiple agents into a coherent final answer",
                "tags": ["synthesis", "aggregation", "final_response"],
                "examples": ["Combine research and analysis results", "Merge code and documentation"]
            }
        ]
    ),
    
    "research": AgentConfig(
        name="Research Agent",
        description="Specialized agent for information gathering and web research",
        port=9002,
        dify_workflow_id=os.getenv("RESEARCH_WORKFLOW_ID", ""),
        dify_api_key=os.getenv("RESEARCH_API_KEY", ""),
        skills=[
            {
                "id": "web_research",
                "name": "Web Research",
                "description": "Searches the web for relevant information on any topic",
                "tags": ["research", "web_search", "information_gathering"],
                "examples": ["Research latest AI developments", "Find market trends", "Look up technical documentation"]
            },
            {
                "id": "fact_checking",
                "name": "Fact Checking",
                "description": "Verifies information accuracy and provides source citations",
                "tags": ["fact_check", "verification", "sources"],
                "examples": ["Verify this claim", "Check accuracy of statistics", "Find reliable sources"]
            }
        ]
    ),
    
    "analysis": AgentConfig(
        name="Analysis Agent",
        description="Specialized agent for data analysis and processing",
        port=9003,
        dify_workflow_id=os.getenv("ANALYSIS_WORKFLOW_ID", ""),
        dify_api_key=os.getenv("ANALYSIS_API_KEY", ""),
        skills=[
            {
                "id": "data_analysis",
                "name": "Data Analysis",
                "description": "Analyzes datasets and provides insights and patterns",
                "tags": ["analysis", "data_processing", "insights"],
                "examples": ["Analyze sales data", "Find patterns in user behavior", "Statistical analysis"]
            },
            {
                "id": "summarization",
                "name": "Text Summarization",
                "description": "Summarizes long documents and extracts key points",
                "tags": ["summarization", "text_processing", "key_points"],
                "examples": ["Summarize research paper", "Extract key insights", "Create executive summary"]
            }
        ]
    ),
    
    "code": AgentConfig(
        name="Code Agent",
        description="Specialized agent for code generation and technical tasks",
        port=9004,
        dify_workflow_id=os.getenv("CODE_WORKFLOW_ID", ""),
        dify_api_key=os.getenv("CODE_API_KEY", ""),
        skills=[
            {
                "id": "code_generation",
                "name": "Code Generation",
                "description": "Generates code in various programming languages",
                "tags": ["coding", "programming", "development"],
                "examples": ["Write Python function", "Create API endpoint", "Generate SQL queries"]
            },
            {
                "id": "code_review",
                "name": "Code Review",
                "description": "Reviews code for best practices, bugs, and improvements",
                "tags": ["code_review", "debugging", "optimization"],
                "examples": ["Review this Python code", "Find bugs in JavaScript", "Optimize algorithm"]
            }
        ]
    )
}


def get_agent_config(agent_name: str) -> AgentConfig:
    """Get configuration for a specific agent.
    
    Args:
        agent_name: Name of the agent
        
    Returns:
        Agent configuration
        
    Raises:
        KeyError: If agent name is not found
    """
    if agent_name not in AGENTS_CONFIG:
        raise KeyError(f"Agent '{agent_name}' not found in configuration")
    
    return AGENTS_CONFIG[agent_name]


def get_all_agent_urls() -> Dict[str, str]:
    """Get URLs for all agents.
    
    Returns:
        Dictionary mapping agent names to their URLs
    """
    return {
        name: f"http://localhost:{config.port}/"
        for name, config in AGENTS_CONFIG.items()
    }


# Environment variables for Dify connection
DIFY_BASE_URL = os.getenv("DIFY_BASE_URL", "http://localhost/v1")
DEFAULT_DIFY_API_KEY = os.getenv("DIFY_API_KEY", "")
