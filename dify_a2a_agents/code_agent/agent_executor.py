"""Code Agent Executor using Dify workflows for code generation and review."""

from typing_extensions import override

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message

from ..shared.dify_client import DifyA2AExecutor, DifyWorkflowClient
from ..config.agents import get_agent_config


class CodeAgent(DifyA2AExecutor):
    """Code agent specialized in code generation and technical tasks."""
    
    def __init__(self, dify_client: DifyWorkflowClient):
        """Initialize code agent with Dify client."""
        super().__init__(dify_client)
        self.config = get_agent_config("code")
    
    async def generate_code(self, code_request: str) -> str:
        """Generate code based on requirements.
        
        Args:
            code_request: Description of code to generate
            
        Returns:
            Generated code with explanations
        """
        code_context = {
            "task_type": "code_generation",
            "code_focus": "clean, efficient, and well-documented code",
            "output_format": "code with explanations and usage examples"
        }
        
        result = await self.process_with_dify(
            self.config.dify_workflow_id,
            code_request,
            code_context
        )
        
        return result
    
    async def review_code(self, code_input: str) -> str:
        """Review code for best practices and improvements.
        
        Args:
            code_input: Code to review
            
        Returns:
            Code review with suggestions
        """
        review_context = {
            "task_type": "code_review",
            "review_focus": "best practices, bugs, optimization opportunities",
            "output_format": "detailed review with improvement suggestions"
        }
        
        result = await self.process_with_dify(
            self.config.dify_workflow_id,
            f"Review this code: {code_input}",
            review_context
        )
        
        return result


class CodeAgentExecutor(AgentExecutor):
    """A2A Agent Executor for the Code Agent."""
    
    def __init__(self, dify_client: DifyWorkflowClient):
        """Initialize with Dify client."""
        self.code_agent = CodeAgent(dify_client)
    
    @override
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """Execute code tasks for incoming requests."""
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
            # Indicate coding task is starting
            event_queue.enqueue_event(
                new_agent_text_message("💻 Starting code-related task...")
            )
            
            # Determine task type based on input
            input_lower = user_input.lower()
            
            if any(phrase in input_lower for phrase in ["review", "check", "improve", "optimize", "debug"]):
                # Code review task
                event_queue.enqueue_event(
                    new_agent_text_message("🔍 Reviewing code for improvements...")
                )
                
                result = await self.code_agent.review_code(user_input)
                
                event_queue.enqueue_event(
                    new_agent_text_message(f"📝 Code Review Results:\n{result}")
                )
            else:
                # Code generation task
                event_queue.enqueue_event(
                    new_agent_text_message("⚡ Generating code based on your requirements...")
                )
                
                result = await self.code_agent.generate_code(user_input)
                
                event_queue.enqueue_event(
                    new_agent_text_message(f"🎯 Generated Code:\n{result}")
                )
        
        except Exception as e:
            event_queue.enqueue_event(
                new_agent_text_message(f"❌ Error during code task: {str(e)}")
            )
    
    @override
    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        """Cancel the code execution."""
        await self.code_agent.cleanup()
        event_queue.enqueue_event(
            new_agent_text_message("Code task cancelled.")
        )
