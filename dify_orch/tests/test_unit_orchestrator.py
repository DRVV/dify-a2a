"""
Unit tests for Dify Orchestrator.
These tests use mocked dependencies and don't require external API calls.
"""
import pytest
from unittest.mock import Mock, patch
from orchestrator import DifyOrchestrator


class TestOrchestratorInitialization:
    """Test orchestrator initialization and configuration."""

    def test_orchestrator_initialization_success(self, orchestrator_with_mock_client):
        """Test successful orchestrator initialization."""
        orchestrator = orchestrator_with_mock_client
        
        # Test that orchestrator is properly initialized
        assert orchestrator is not None
        assert hasattr(orchestrator, 'chatflows')
        assert len(orchestrator.chatflows) > 0

    def test_get_chatflow_names(self, orchestrator_with_mock_client):
        """Test getting chatflow names."""
        orchestrator = orchestrator_with_mock_client
        names = orchestrator.get_chatflow_names()
        
        assert isinstance(names, list)
        assert len(names) == 2  # Based on test env
        assert "test-chatflow-1" in names
        assert "test-chatflow-2" in names

    def test_get_chatflow_config(self, orchestrator_with_mock_client):
        """Test getting chatflow configuration."""
        orchestrator = orchestrator_with_mock_client
        names = orchestrator.get_chatflow_names()
        
        for name in names:
            config = orchestrator.get_chatflow_config(name)
            assert hasattr(config, 'name')
            assert hasattr(config, 'description')
            assert config.name == name

    def test_invalid_chatflow_config(self, orchestrator_with_mock_client):
        """Test getting configuration for non-existent chatflow."""
        orchestrator = orchestrator_with_mock_client
        
        with pytest.raises(ValueError, match="Chatflow 'invalid-name' not found"):
            orchestrator.get_chatflow_config("invalid-name")


class TestIndividualChatflowAccess:
    """Test sending messages to individual chatflows."""

    def test_send_to_chatflow_success(self, orchestrator_with_mock_client, sample_test_queries):
        """Test successful message sending to individual chatflow."""
        orchestrator = orchestrator_with_mock_client
        chatflow_names = orchestrator.get_chatflow_names()
        
        for chatflow_name in chatflow_names:
            response = orchestrator.send_to_chatflow(
                chatflow_name=chatflow_name,
                query=sample_test_queries["simple"]
            )
            
            assert isinstance(response, dict)
            assert "answer" in response
            assert response["answer"] == "Test response from mocked chatflow"

    def test_send_to_chatflow_invalid_name(self, orchestrator_with_mock_client, sample_test_queries):
        """Test sending message to non-existent chatflow."""
        orchestrator = orchestrator_with_mock_client
        
        with pytest.raises(ValueError, match="Chatflow 'invalid-chatflow' not found"):
            orchestrator.send_to_chatflow(
                chatflow_name="invalid-chatflow",
                query=sample_test_queries["simple"]
            )

    def test_send_to_chatflow_with_different_query_types(self, orchestrator_with_mock_client, sample_test_queries):
        """Test sending different types of queries."""
        orchestrator = orchestrator_with_mock_client
        chatflow_name = orchestrator.get_chatflow_names()[0]
        
        for query_type, query in sample_test_queries.items():
            response = orchestrator.send_to_chatflow(
                chatflow_name=chatflow_name,
                query=query
            )
            assert "answer" in response

    def test_response_structure(self, orchestrator_with_mock_client, sample_test_queries, expected_response_structure):
        """Test that response has expected structure."""
        orchestrator = orchestrator_with_mock_client
        chatflow_name = orchestrator.get_chatflow_names()[0]
        
        response = orchestrator.send_to_chatflow(
            chatflow_name=chatflow_name,
            query=sample_test_queries["simple"]
        )
        
        # Check required fields
        for field in expected_response_structure["required_fields"]:
            assert field in response, f"Required field '{field}' missing from response"
        
        # Check that response is properly formed
        assert isinstance(response["answer"], str)


class TestMultipleChatflowAccess:
    """Test sending messages to multiple chatflows."""

    def test_send_to_multiple_chatflows_success(self, orchestrator_with_mock_client, sample_test_queries):
        """Test successful sending to multiple chatflows."""
        orchestrator = orchestrator_with_mock_client
        chatflow_names = orchestrator.get_chatflow_names()
        
        response = orchestrator.send_to_multiple_chatflows(
            chatflow_names=chatflow_names,
            query=sample_test_queries["simple"]
        )
        
        assert response["status"] == "success"
        assert response["success_count"] == len(chatflow_names)
        assert response["total_count"] == len(chatflow_names)
        assert "responses" in response
        assert len(response["responses"]) == len(chatflow_names)

    def test_send_to_all_chatflows(self, orchestrator_with_mock_client, sample_test_queries):
        """Test sending to all chatflows."""
        orchestrator = orchestrator_with_mock_client
        
        response = orchestrator.send_to_all_chatflows(sample_test_queries["simple"])
        
        assert response["status"] == "success"
        assert response["success_count"] > 0
        assert "responses" in response

    def test_send_to_multiple_chatflows_partial_invalid(self, orchestrator_with_mock_client, sample_test_queries):
        """Test sending to multiple chatflows with some invalid names."""
        orchestrator = orchestrator_with_mock_client
        valid_name = orchestrator.get_chatflow_names()[0]
        invalid_names = [valid_name, "invalid-chatflow"]
        
        response = orchestrator.send_to_multiple_chatflows(
            chatflow_names=invalid_names,
            query=sample_test_queries["simple"]
        )
        
        assert response["status"] == "partial_success"
        assert response["success_count"] == 1
        assert response["total_count"] == 2
        assert len(response["responses"]) == 1  # Only successful response
        assert len(response["errors"]) == 1  # One error


class TestSequentialOrchestration:
    """Test sequential orchestration functionality."""

    def test_orchestrate_sequential_success(self, orchestrator_with_mock_client):
        """Test successful sequential orchestration."""
        orchestrator = orchestrator_with_mock_client
        chatflow_names = orchestrator.get_chatflow_names()
        
        result = orchestrator.orchestrate_sequential(
            chatflow_sequence=chatflow_names,
            initial_query="Test sequential query"
        )
        
        assert result["status"] == "success"
        assert "final_answer" in result
        assert "step_results" in result
        assert len(result["step_results"]) == len(chatflow_names)

    def test_orchestrate_sequential_empty_sequence(self, orchestrator_with_mock_client):
        """Test sequential orchestration with empty sequence."""
        orchestrator = orchestrator_with_mock_client
        
        result = orchestrator.orchestrate_sequential(
            chatflow_sequence=[],
            initial_query="Test query"
        )
        
        assert result["status"] == "error"
        assert "error" in result

    def test_orchestrate_sequential_invalid_chatflow(self, orchestrator_with_mock_client):
        """Test sequential orchestration with invalid chatflow in sequence."""
        orchestrator = orchestrator_with_mock_client
        invalid_sequence = ["invalid-chatflow"]
        
        result = orchestrator.orchestrate_sequential(
            chatflow_sequence=invalid_sequence,
            initial_query="Test query"
        )
        
        assert result["status"] == "error"
        assert "error" in result


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_api_client_initialization_failure(self, mock_env):
        """Test handling of API client initialization failure."""
        with patch('orchestrator.ChatClient') as mock_client_class:
            mock_client_class.side_effect = Exception("API client initialization failed")
            
            with pytest.raises(Exception, match="API client initialization failed"):
                DifyOrchestrator()

    def test_chatflow_api_call_failure(self, mock_env):
        """Test handling of API call failures."""
        mock_failing_client = Mock()
        mock_failing_client.create_chat_message.side_effect = Exception("Simulated API failure")
        
        with patch('orchestrator.ChatClient', return_value=mock_failing_client):
            orchestrator = DifyOrchestrator()
            chatflow_name = orchestrator.get_chatflow_names()[0]
            
            with pytest.raises(Exception, match="Simulated API failure"):
                orchestrator.send_to_chatflow(chatflow_name, "test query")

    def test_partial_failure_handling(self, orchestrator_with_partial_failure, sample_test_queries):
        """Test handling of partial failures in multiple chatflow calls."""
        orchestrator = orchestrator_with_partial_failure
        chatflow_names = orchestrator.get_chatflow_names()
        
        response = orchestrator.send_to_multiple_chatflows(
            chatflow_names=chatflow_names,
            query=sample_test_queries["simple"]
        )
        
        assert response["status"] == "partial_success"
        assert response["success_count"] == 1
        assert response["total_count"] == 2
        assert len(response["errors"]) == 1


class TestConfigurationValidation:
    """Test configuration validation."""

    def test_missing_environment_variables(self):
        """Test behavior with missing environment variables."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(Exception):  # Should fail due to missing config
                DifyOrchestrator()

    def test_invalid_chatflow_count(self):
        """Test behavior with invalid chatflow count."""
        invalid_env = {"DIFY_CHATFLOW_COUNT": "invalid"}
        
        with patch.dict('os.environ', invalid_env, clear=True):
            with pytest.raises(ValueError):
                DifyOrchestrator()

    def test_missing_chatflow_configuration(self):
        """Test behavior with missing chatflow configuration."""
        incomplete_env = {
            "DIFY_CHATFLOW_COUNT": "1",
            "DIFY_CHATFLOW_1_NAME": "test-chatflow"
            # Missing API_KEY
        }
        
        with patch.dict('os.environ', incomplete_env, clear=True):
            with pytest.raises(Exception):
                DifyOrchestrator()


class TestUtilityMethods:
    """Test utility and helper methods."""

    def test_chatflow_existence_check(self, orchestrator_with_mock_client):
        """Test checking if chatflow exists."""
        orchestrator = orchestrator_with_mock_client
        
        # Test existing chatflow
        valid_name = orchestrator.get_chatflow_names()[0]
        assert orchestrator._validate_chatflow_name(valid_name) is True
        
        # Test non-existing chatflow
        with pytest.raises(ValueError):
            orchestrator._validate_chatflow_name("non-existent")

    def test_query_validation(self, orchestrator_with_mock_client):
        """Test query validation."""
        orchestrator = orchestrator_with_mock_client
        chatflow_name = orchestrator.get_chatflow_names()[0]
        
        # Test empty query
        with pytest.raises(ValueError, match="Query cannot be empty"):
            orchestrator.send_to_chatflow(chatflow_name, "")
        
        # Test None query
        with pytest.raises(ValueError, match="Query cannot be empty"):
            orchestrator.send_to_chatflow(chatflow_name, None)

    def test_response_formatting(self, orchestrator_with_mock_client, sample_test_queries):
        """Test response formatting consistency."""
        orchestrator = orchestrator_with_mock_client
        chatflow_name = orchestrator.get_chatflow_names()[0]
        
        response = orchestrator.send_to_chatflow(chatflow_name, sample_test_queries["simple"])
        
        # Check response type and basic structure
        assert isinstance(response, dict)
        assert "answer" in response
        assert isinstance(response["answer"], str)
        assert len(response["answer"]) > 0
