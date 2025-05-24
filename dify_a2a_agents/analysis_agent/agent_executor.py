"""Analysis Agent Executor using Dify workflows for data analysis."""

from typing_extensions import override

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message

from ..shared.dify_client import DifyA2AExecutor, DifyWorkflowClient
from ..config.agents import get_agent_config


class AnalysisAgent(DifyA2AExecutor):
    """Analysis agent specialized in data analysis and summarization."""
    
    def __init__(self, dify_client: DifyWorkflowClient):
        """Initialize analysis agent with Dify client."""
        super().__init__(dify_client)
        self.config = get_agent_config("analysis")
    
    async def analyze_data(self, data_input: str) -> str:
        """Analyze data and provide insights.
        
        Args:
            data_input: Data to analyze or description of analysis task
            
        Returns:
            Analysis results with insights
        """
        analysis_context = {
            "task_type": "data_analysis",
            "analysis_focus": "patterns, trends, and insights",
            "output_format": "structured analysis with key findings"
        }
        
        result = await self.process_with_dify(
            self.config.dify_workflow_id,
            data_input,
            analysis_context
        )
        
        return result
    
    async def summarize_content(self, content: str) -> str:
        """Summarize long content and extract key points.
        
        Args:
            content: Content to summarize
            
        Returns:
            Summary with key points
        """
        summary_context = {
            "task_type": "summarization",
            "summary_focus": "key points and main insights",
            "output_format": "executive summary with bullet points"
        }
        
        result = await self.process_with_dify(
            self.config.dify_workflow_id,
            f"Summarize: {content}",
            summary_context
        )
        
        return result


class AnalysisAgentExecutor(AgentExecutor):
    """A2A Agent Executor for the Analysis Agent."""
    
    def __init__(self, dify_client: DifyWorkflowClient):
        """Initialize with Dify client."""
        self.analysis_agent = AnalysisAgent(dify_client)
    
    @override
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Execute analysis tasks for incoming requests."""
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
            # Indicate analysis is starting
            event_queue.enqueue_event(
                new_agent_text_message("📊 Starting analysis of your request...")
            )
            
            # Determine analysis type based on input
            input_lower = user_input.lower()
            
            if any(phrase in input_lower for phrase in ["summarize", "summary", "key points", "tldr"]):
                # Summarization task
                event_queue.enqueue_event(
                    new_agent_text_message("📝 Creating summary and extracting key points...")
                )
                
                result = await self.analysis_agent.summarize_content(user_input)
                
                event_queue.enqueue_event(
                    new_agent_text_message(f"📋 Summary Results:\n{result}")
                )
            else:
                # General data analysis task
                event_queue.enqueue_event(
                    new_agent_text_message("🔍 Performing detailed analysis...")
                )
                
                result = await self.analysis_agent.analyze_data(user_input)
                
                event_queue.enqueue_event(
                    new_agent_text_message(f"📈 Analysis Results:\n{result}")
                )
        
        except Exception as e:
            event_queue.enqueue_event(
                new_agent_text_message(f"❌ Error during analysis: {str(e)}")
            )
    
    @override
    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        """Cancel the analysis execution."""
        await self.analysis_agent.cleanup()
        event_queue.enqueue_event(
            new_agent_text_message("Analysis task cancelled.")
        )
