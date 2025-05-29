import os
import logging
import warnings
from typing import Dict, Any, Optional, List, Union
from dotenv import load_dotenv
from dify_client import ChatClient

class ChatflowConfig:
    """Configuration for a single chatflow."""
    
    def __init__(self, api_key: str, name: str, description: str = "", role: str = "content"):
        self.api_key = api_key
        self.name = name
        self.description = description
        self.role = role

class DifyOrchestrator:
    """
    A scalable Dify orchestrator client that manages multiple chatflows
    and supports various orchestration patterns.
    """
    
    def __init__(self, env_path: str = ".env"):
        """
        Initialize the orchestrator with environment configuration.
        
        Args:
            env_path: Path to the .env file containing API keys
        """
        load_dotenv(env_path)
        
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Base URL configuration
        self.base_url = os.getenv("DIFY_BASE_URL")
        
        # Initialize chatflows dynamically
        self.chatflows: Dict[str, ChatClient] = {}
        self.chatflow_configs: Dict[str, ChatflowConfig] = {}
        
        # Load chatflows from environment
        self._load_chatflows_from_env()
        
        # Legacy clients for backward compatibility
        self._setup_legacy_clients()
        
        self.logger.info(f"Dify Orchestrator initialized with {len(self.chatflows)} chatflows")
    
    def _load_chatflows_from_env(self):
        """Load chatflow configurations from environment variables."""
        chatflow_count = int(os.getenv("DIFY_CHATFLOW_COUNT", "0"))
        
        if chatflow_count == 0:
            self.logger.warning("No chatflows configured. Set DIFY_CHATFLOW_COUNT and corresponding variables.")
            return
        
        for i in range(chatflow_count):
            api_key = os.getenv(f"DIFY_CHATFLOW_{i}_API_KEY")
            name = os.getenv(f"DIFY_CHATFLOW_{i}_NAME", f"chatflow_{i}")
            description = os.getenv(f"DIFY_CHATFLOW_{i}_DESCRIPTION", f"Chatflow {i}")
            role = os.getenv(f"DIFY_CHATFLOW_{i}_ROLE", "content")
            
            if not api_key:
                self.logger.warning(f"Missing API key for chatflow {i}, skipping...")
                continue
            
            # Create configuration
            config = ChatflowConfig(api_key, name, description, role)
            self.chatflow_configs[name] = config
            
            # Create client
            client = ChatClient(api_key=api_key)
            if self.base_url:
                client.base_url = self.base_url
            
            self.chatflows[name] = client
            self.logger.info(f"Initialized chatflow '{name}' (index {i})")
    
    def _setup_legacy_clients(self):
        """Setup legacy client attributes for backward compatibility."""
        # Legacy client_1
        chatflow_1_api_key = os.getenv("DIFY_CHATFLOW_1_API_KEY")
        if chatflow_1_api_key:
            self.chatflow_1_api_key = chatflow_1_api_key
            self.client_1 = ChatClient(api_key=chatflow_1_api_key)
            if self.base_url:
                self.client_1.base_url = self.base_url
        
        # Legacy client_2
        chatflow_2_api_key = os.getenv("DIFY_CHATFLOW_2_API_KEY")
        if chatflow_2_api_key:
            self.chatflow_2_api_key = chatflow_2_api_key
            self.client_2 = ChatClient(api_key=chatflow_2_api_key)
            if self.base_url:
                self.client_2.base_url = self.base_url
    
    def get_chatflow_names(self) -> List[str]:
        """Get list of all configured chatflow names."""
        return list(self.chatflows.keys())
    
    def get_chatflow_config(self, name: str) -> Optional[ChatflowConfig]:
        """Get configuration for a specific chatflow."""
        return self.chatflow_configs.get(name)
    
    def send_to_chatflow(self, 
                        chatflow_name: str,
                        query: str, 
                        user: str = "default_user",
                        conversation_id: Optional[str] = None,
                        inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send a message to a specific chatflow by name.
        
        Args:
            chatflow_name: Name of the chatflow to send to
            query: The message to send
            user: User identifier
            conversation_id: Optional conversation ID for context
            inputs: Optional additional inputs for the workflow
            
        Returns:
            Response from the chatflow as a dictionary
        """
        if chatflow_name not in self.chatflows:
            raise ValueError(f"Chatflow '{chatflow_name}' not found. Available: {list(self.chatflows.keys())}")
        
        try:
            self.logger.info(f"Sending message to chatflow '{chatflow_name}': {query[:50]}...")
            
            client = self.chatflows[chatflow_name]
            response = client.create_chat_message(
                query=query,
                user=user,
                conversation_id=conversation_id,
                inputs=inputs or {}
            )
            
            self.logger.info(f"Successfully received response from chatflow '{chatflow_name}'")
            
            # Convert Response object to dictionary
            if hasattr(response, 'json'):
                result = response.json()
            else:
                result = {"raw_response": str(response)}
            
            # Add metadata
            result["_chatflow_name"] = chatflow_name
            result["_query"] = query
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error sending to chatflow '{chatflow_name}': {str(e)}")
            raise
    
    def send_to_multiple_chatflows(self, 
                                  chatflow_names: List[str],
                                  query: str, 
                                  user: str = "default_user",
                                  conversation_id: Optional[str] = None,
                                  inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send the same query to multiple chatflows in parallel.
        
        Args:
            chatflow_names: List of chatflow names to send to
            query: The message to send to all chatflows
            user: User identifier
            conversation_id: Optional conversation ID for context
            inputs: Optional additional inputs for the workflow
            
        Returns:
            Dictionary containing responses from all chatflows
        """
        results = {
            "query": query,
            "responses": {},
            "errors": {},
            "status": "partial_success"
        }
        
        success_count = 0
        
        for chatflow_name in chatflow_names:
            try:
                response = self.send_to_chatflow(
                    chatflow_name=chatflow_name,
                    query=query,
                    user=user,
                    conversation_id=conversation_id,
                    inputs=inputs
                )
                results["responses"][chatflow_name] = response
                success_count += 1
            except Exception as e:
                self.logger.error(f"Failed to send to chatflow '{chatflow_name}': {str(e)}")
                results["errors"][chatflow_name] = str(e)
        
        # Update status based on results
        if success_count == len(chatflow_names):
            results["status"] = "success"
        elif success_count == 0:
            results["status"] = "failed"
        
        results["success_count"] = success_count
        results["total_count"] = len(chatflow_names)
        
        return results
    
    def send_to_all_chatflows(self, 
                             query: str, 
                             user: str = "default_user",
                             conversation_id: Optional[str] = None,
                             inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send the same query to all configured chatflows.
        
        Args:
            query: The message to send to all chatflows
            user: User identifier
            conversation_id: Optional conversation ID for context
            inputs: Optional additional inputs for the workflow
            
        Returns:
            Dictionary containing responses from all chatflows
        """
        return self.send_to_multiple_chatflows(
            chatflow_names=list(self.chatflows.keys()),
            query=query,
            user=user,
            conversation_id=conversation_id,
            inputs=inputs
        )
    
    def orchestrate_sequential(self, 
                              chatflow_sequence: List[str],
                              initial_query: str,
                              user: str = "default_user") -> Dict[str, Any]:
        """
        Execute chatflows in sequence, passing output from one to the next.
        
        Args:
            chatflow_sequence: List of chatflow names in execution order
            initial_query: The initial query for the first chatflow
            user: User identifier
            
        Returns:
            Dictionary containing the complete execution trace and final result
        """
        if not chatflow_sequence:
            raise ValueError("Chatflow sequence cannot be empty")
        
        results = {
            "initial_query": initial_query,
            "sequence": chatflow_sequence,
            "steps": [],
            "status": "success"
        }
        
        current_input = initial_query
        
        try:
            for i, chatflow_name in enumerate(chatflow_sequence):
                self.logger.info(f"Sequential step {i+1}: Executing chatflow '{chatflow_name}'")
                
                response = self.send_to_chatflow(
                    chatflow_name=chatflow_name,
                    query=current_input,
                    user=user
                )
                
                step_result = {
                    "step": i + 1,
                    "chatflow_name": chatflow_name,
                    "input": current_input,
                    "response": response,
                    "answer": response.get("answer", str(response))
                }
                
                results["steps"].append(step_result)
                
                # Use the answer as input for the next step
                current_input = step_result["answer"]
            
            # Set final result
            results["final_answer"] = current_input
            self.logger.info(f"Sequential workflow completed successfully with {len(chatflow_sequence)} steps")
            
        except Exception as e:
            self.logger.error(f"Error in sequential workflow: {str(e)}")
            results["status"] = "failed"
            results["error"] = str(e)
        
        return results
    
    def get_chatflows_by_role(self, role: str) -> List[str]:
        """Get list of chatflow names filtered by role.
        
        Args:
            role: The role to filter by (e.g., "content", "summarizer")
            
        Returns:
            List of chatflow names with the specified role
        """
        return [
            name for name, config in self.chatflow_configs.items() 
            if config.role == role
        ]
    
    def get_content_chatflows(self) -> List[str]:
        """Get list of content chatflow names (excludes summarizer).
        
        Returns:
            List of content chatflow names
        """
        return self.get_chatflows_by_role("content")
    
    def get_summarizer_chatflow(self) -> Optional[str]:
        """Get the summarizer chatflow name.
        
        Returns:
            Summarizer chatflow name or None if not configured
        """
        summarizers = self.get_chatflows_by_role("summarizer")
        if not summarizers:
            return None
        if len(summarizers) > 1:
            self.logger.warning(f"Multiple summarizers found: {summarizers}. Using first one.")
        return summarizers[0]
    
    def get_event_builder_chatflow(self) -> Optional[str]:
        """Get the event_builder chatflow name.
        
        Returns:
            Event builder chatflow name or None if not configured
        """
        event_builders = self.get_chatflows_by_role("event_builder")
        if not event_builders:
            return None
        if len(event_builders) > 1:
            self.logger.warning(f"Multiple event builders found: {event_builders}. Using first one.")
        return event_builders[0]
    
    def format_responses_for_summary(self, responses: Dict[str, Any]) -> str:
        """Format chatflow responses for summarizer input.
        
        Args:
            responses: Dictionary of chatflow responses
            
        Returns:
            Formatted string for summarizer input
        """
        if not responses:
            return "No responses received from content chatflows."
        
        formatted_parts = []
        formatted_parts.append("Please summarize the following responses from multiple AI agents:")
        formatted_parts.append("")
        
        for i, (chatflow_name, response) in enumerate(responses.items(), 1):
            # Extract the main answer content
            answer = response.get("answer", "")
            if not answer:
                # Fallback to other possible response fields
                answer = response.get("data", response.get("content", str(response)))
            
            formatted_parts.append(f"**Agent {i} ({chatflow_name}):**")
            formatted_parts.append(answer)
            formatted_parts.append("")  # Empty line for separation
        
        formatted_parts.append("Please provide a comprehensive summary that captures the key insights from all agents.")
        
        return "\n".join(formatted_parts)
    
    def format_data_for_event_builder(self, 
                                     original_query: str,
                                     content_responses: Dict[str, Any], 
                                     summary_response: Optional[Dict[str, Any]] = None) -> str:
        """Format all available data for event_builder input.
        
        Args:
            original_query: The original user query
            content_responses: Dictionary of content chatflow responses
            summary_response: Optional summary response
            
        Returns:
            Formatted string for event_builder input
        """
        formatted_parts = []
        formatted_parts.append("Based on the following analysis and summary, please create appropriate events, actions, or next steps:")
        formatted_parts.append("")
        
        # Add original query
        formatted_parts.append("**Original Query:**")
        formatted_parts.append(original_query)
        formatted_parts.append("")
        
        # Add content responses
        if content_responses:
            formatted_parts.append("**Content Agent Responses:**")
            for i, (chatflow_name, response) in enumerate(content_responses.items(), 1):
                answer = response.get("answer", "")
                if not answer:
                    answer = response.get("data", response.get("content", str(response)))
                
                formatted_parts.append(f"Agent {i} ({chatflow_name}): {answer}")
            formatted_parts.append("")
        
        # Add summary if available
        if summary_response:
            summary_content = summary_response.get("answer", "")
            if not summary_content:
                summary_content = summary_response.get("data", summary_response.get("content", str(summary_response)))
            
            formatted_parts.append("**Summary:**")
            formatted_parts.append(summary_content)
            formatted_parts.append("")
        
        formatted_parts.append("Please analyze the above information and provide actionable events, recommendations, or next steps that would be valuable to the user.")
        
        return "\n".join(formatted_parts)
    
    def orchestrate_with_summary(self, 
                                query: str, 
                                user: str = "default_user",
                                conversation_id: Optional[str] = None,
                                inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Orchestrate content chatflows in parallel, then summarize responses.
        
        Args:
            query: The message to send to content chatflows
            user: User identifier
            conversation_id: Optional conversation ID for context
            inputs: Optional additional inputs for the workflow
            
        Returns:
            Dictionary containing content responses, summary, and metadata
        """
        result = {
            "query": query,
            "content_responses": {},
            "content_errors": {},
            "summary_response": None,
            "summary_error": None,
            "status": "success"
        }
        
        # Step 1: Get content chatflows
        content_chatflows = self.get_content_chatflows()
        if not content_chatflows:
            result["status"] = "failed"
            result["error"] = "No content chatflows configured"
            return result
        
        # Step 2: Send to content chatflows in parallel
        self.logger.info(f"Sending query to {len(content_chatflows)} content chatflows...")
        content_result = self.send_to_multiple_chatflows(
            chatflow_names=content_chatflows,
            query=query,
            user=user,
            conversation_id=conversation_id,
            inputs=inputs
        )
        
        result["content_responses"] = content_result.get("responses", {})
        result["content_errors"] = content_result.get("errors", {})
        result["content_success_count"] = content_result.get("success_count", 0)
        result["content_total_count"] = content_result.get("total_count", 0)
        
        # Check if we have any successful content responses
        if not result["content_responses"]:
            result["status"] = "failed"
            result["error"] = "All content chatflows failed"
            return result
        
        # Step 3: Get summarizer chatflow
        summarizer_name = self.get_summarizer_chatflow()
        if not summarizer_name:
            self.logger.warning("No summarizer chatflow configured. Skipping summary step.")
            result["status"] = "partial_success" if result["content_errors"] else "success"
            result["summary_error"] = "No summarizer chatflow configured"
            return result
        
        # Step 4: Format responses for summarizer
        summary_input = self.format_responses_for_summary(result["content_responses"])
        
        # Step 5: Send to summarizer
        try:
            self.logger.info(f"Sending responses to summarizer '{summarizer_name}'...")
            summary_response = self.send_to_chatflow(
                chatflow_name=summarizer_name,
                query=summary_input,
                user=user,
                conversation_id=conversation_id,
                inputs=inputs
            )
            result["summary_response"] = summary_response
            self.logger.info("Successfully received summary response")
        except Exception as e:
            self.logger.error(f"Error getting summary: {str(e)}")
            result["summary_error"] = str(e)
        
        # Determine final status
        if result["summary_error"]:
            result["status"] = "partial_success"
        elif result["content_errors"]:
            result["status"] = "partial_success"
        else:
            result["status"] = "success"
        
        return result
    
    # Legacy methods for backward compatibility
    def send_to_chatflow_1(self, 
                          query: str, 
                          user: str = "default_user",
                          conversation_id: Optional[str] = None,
                          inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Legacy method: Send a message to chatflow 1.
        
        DEPRECATED: Use send_to_chatflow() with chatflow name instead.
        """
        warnings.warn(
            "send_to_chatflow_1() is deprecated. Use send_to_chatflow() with chatflow name instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        if not hasattr(self, 'client_1'):
            raise ValueError("DIFY_CHATFLOW_1_API_KEY not found in environment variables")
        
        try:
            self.logger.info(f"Sending message to chatflow 1: {query[:50]}...")
            
            response = self.client_1.create_chat_message(
                query=query,
                user=user,
                conversation_id=conversation_id,
                inputs=inputs or {}
            )
            
            self.logger.info("Successfully received response from chatflow 1")
            
            if hasattr(response, 'json'):
                return response.json()
            else:
                return {"raw_response": str(response)}
            
        except Exception as e:
            self.logger.error(f"Error sending to chatflow 1: {str(e)}")
            raise
    
    def send_to_chatflow_2(self, 
                          query: str, 
                          user: str = "default_user",
                          conversation_id: Optional[str] = None,
                          inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Legacy method: Send a message to chatflow 2.
        
        DEPRECATED: Use send_to_chatflow() with chatflow name instead.
        """
        warnings.warn(
            "send_to_chatflow_2() is deprecated. Use send_to_chatflow() with chatflow name instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        if not hasattr(self, 'client_2'):
            raise ValueError("DIFY_CHATFLOW_2_API_KEY not found in environment variables")
        
        try:
            self.logger.info(f"Sending message to chatflow 2: {query[:50]}...")
            
            response = self.client_2.create_chat_message(
                query=query,
                user=user,
                conversation_id=conversation_id,
                inputs=inputs or {}
            )
            
            self.logger.info("Successfully received response from chatflow 2")
            
            if hasattr(response, 'json'):
                return response.json()
            else:
                return {"raw_response": str(response)}
            
        except Exception as e:
            self.logger.error(f"Error sending to chatflow 2: {str(e)}")
            raise
    
    def orchestrate_dual_response(self, query: str) -> Dict[str, Any]:
        """
        Legacy method: Send the same query to both chatflows and return both responses.
        
        DEPRECATED: Use send_to_multiple_chatflows() instead.
        """
        warnings.warn(
            "orchestrate_dual_response() is deprecated. Use send_to_multiple_chatflows() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        try:
            self.logger.info(f"Orchestrating dual response for query: {query[:50]}...")
            
            response_1 = self.send_to_chatflow_1(query)
            response_2 = self.send_to_chatflow_2(query)
            
            result = {
                "query": query,
                "chatflow_1_response": response_1,
                "chatflow_2_response": response_2,
                "status": "success"
            }
            
            self.logger.info("Successfully orchestrated dual response")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in dual orchestration: {str(e)}")
            return {
                "query": query,
                "error": str(e),
                "status": "failed"
            }
    
    def sequential_workflow(self, initial_query: str) -> Dict[str, Any]:
        """
        Legacy method: Send query to chatflow 1, then use its response as input to chatflow 2.
        
        DEPRECATED: Use orchestrate_sequential() instead.
        """
        warnings.warn(
            "sequential_workflow() is deprecated. Use orchestrate_sequential() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        try:
            self.logger.info(f"Starting sequential workflow with query: {initial_query[:50]}...")
            
            response_1 = self.send_to_chatflow_1(initial_query)
            chatflow_1_answer = response_1.get("answer", str(response_1))
            response_2 = self.send_to_chatflow_2(chatflow_1_answer)
            
            result = {
                "initial_query": initial_query,
                "chatflow_1_response": response_1,
                "chatflow_2_input": chatflow_1_answer,
                "chatflow_2_response": response_2,
                "final_answer": response_2.get("answer", str(response_2)),
                "status": "success"
            }
            
            self.logger.info("Successfully completed sequential workflow")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in sequential workflow: {str(e)}")
            return {
                "initial_query": initial_query,
                "error": str(e),
                "status": "failed"
            }
