"""Research Agent Executor using Dify workflows for information gathering."""

from typing_extensions import override

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message

from ..shared.dify_client import DifyA2AExecutor, DifyWorkflowClient
from ..config.agents import get_agent_config


class ResearchAgent(DifyA2AExecutor):
    """Research agent specialized in information gathering and web research."""
    
    def __init__(self, dify_client: DifyWorkflowClient):
        """Initialize research agent with Dify client."""
        super().__init__(dify_client)
        self.config = get_agent_config("research")
    
    async def research_information(self, query: str) -> str:
        """Research information on a given topic.
        
        Args:
            query: Research query
            
        Returns:
            Research results
        """
        research_context = {
            "task_type": "research",
            "search_focus": "comprehensive information gathering",
            "output_format": "structured research report"
        }
        
        result = await self.process_with_dify(
            self.config.dify_workflow_id,
            query,
            research_context
        )
        
        return result
    
    async def fact_check(self, claim: str) -> str:
        """Verify factual claims and provide sources.
        
        Args:
            claim: Claim to verify
            
        Returns:
            Fact-check results with sources
        """
        fact_check_context = {
            "task_type": "fact_checking",
            "verification_focus": "accuracy and source reliability",
            "output_format": "verification report with sources"
        }
        
        result = await self.process_with_dify(
            self.config.dify_workflow_id,
            f"Fact-check: {claim}",
            fact_check_context
        )
        
        return result


class ResearchAgentExecutor(AgentExecutor):
    """A2A Agent Executor for the Research Agent."""
    
    def __init__(self, dify_client: DifyWorkflowClient):
        """Initialize with Dify client."""
        self.research_agent = ResearchAgent(dify_client)
    
    @override
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Execute research tasks for incoming requests."""
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
            # Indicate research is starting
            event_queue.enqueue_event(
                new_agent_text_message("🔍 Starting research on your topic...")
            )
            
            # Determine research type based on input
            input_lower = user_input.lower()
            
            if any(phrase in input_lower for phrase in ["fact-check", "verify", "is it true", "accurate"]):
                # Fact-checking task
                event_queue.enqueue_event(
                    new_agent_text_message("📋 Performing fact-checking...")
                )
                
                result = await self.research_agent.fact_check(user_input)
                
                event_queue.enqueue_event(
                    new_agent_text_message(f"✅ Fact-Check Results:\n{result}")
                )
            else:
                # General research task
                event_queue.enqueue_event(
                    new_agent_text_message("📚 Gathering comprehensive information...")
                )
                
                result = await self.research_agent.research_information(user_input)
                
                event_queue.enqueue_event(
                    new_agent_text_message(f"📖 Research Results:\n{result}")
                )
        
        except Exception as e:
            event_queue.enqueue_event(
                new_agent_text_message(f"❌ Error during research: {str(e)}")
            )
    
    @override
    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        """Cancel the research execution."""
        await self.research_agent.cleanup()
        event_queue.enqueue_event(
            new_agent_text_message("Research task cancelled.")
        )
