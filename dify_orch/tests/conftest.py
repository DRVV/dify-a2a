"""
Pytest configuration and shared fixtures for Dify Orchestrator tests.
"""
import os
import pytest
import warnings
from unittest.mock import Mock, patch
from orchestrator import DifyOrchestrator


@pytest.fixture(scope="session")
def test_env_vars():
    """Fixture providing test environment variables."""
    return {
        "DIFY_BASE_URL": "https://api.dify.ai/v1",
        "DIFY_CHATFLOW_COUNT": "2",
        "DIFY_CHATFLOW_0_API_KEY": "test-api-key-1",
        "DIFY_CHATFLOW_0_NAME": "test-chatflow-1",
        "DIFY_CHATFLOW_0_DESCRIPTION": "Test chatflow 1 for unit testing",
        "DIFY_CHATFLOW_1_API_KEY": "test-api-key-2",
        "DIFY_CHATFLOW_1_NAME": "test-chatflow-2",
        "DIFY_CHATFLOW_1_DESCRIPTION": "Test chatflow 2 for unit testing",
        # Legacy support (these will override the above if present)
        "DIFY_CHATFLOW_1_API_KEY": "test-api-key-1",
        "DIFY_CHATFLOW_2_API_KEY": "test-api-key-2",
    }


@pytest.fixture(scope="session")
def mock_env(test_env_vars):
    """Mock environment variables for testing."""
    with patch.dict(os.environ, test_env_vars, clear=False):
        yield test_env_vars


@pytest.fixture
def mock_dify_client():
    """Mock ChatClient for unit testing."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "answer": "Test response from mocked chatflow",
        "conversation_id": "test-conversation-id",
        "message_id": "test-message-id",
        "created_at": 1234567890,
        "feedback": None
    }
    mock_client.create_chat_message.return_value = mock_response
    return mock_client


@pytest.fixture
def orchestrator_with_mock_client(mock_env, mock_dify_client):
    """Orchestrator instance with mocked ChatClient."""
    with patch('orchestrator.ChatClient', return_value=mock_dify_client):
        orchestrator = DifyOrchestrator()
        yield orchestrator


@pytest.fixture
def real_orchestrator(mock_env):
    """Real orchestrator instance for integration tests."""
    try:
        orchestrator = DifyOrchestrator()
        yield orchestrator
    except Exception as e:
        pytest.skip(f"Cannot create real orchestrator: {e}")


@pytest.fixture
def sample_test_queries():
    """Sample test queries for various test scenarios."""
    return {
        "simple": "Hello, this is a test message.",
        "complex": "Generate a detailed analysis of machine learning trends in 2024.",
        "creative": "Write a short story about a robot discovering emotions.",
        "technical": "Explain the differences between REST and GraphQL APIs.",
        "conversational": "What's your primary function and how can you help users?",
    }


@pytest.fixture
def expected_response_structure():
    """Expected structure of Dify API responses."""
    return {
        "required_fields": ["answer"],
        "optional_fields": ["conversation_id", "message_id", "created_at", "feedback"],
    }


@pytest.fixture(autouse=True)
def capture_warnings():
    """Automatically capture warnings for all tests."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        yield w


@pytest.fixture
def mock_failing_client():
    """Mock DifyClient that simulates failures."""
    mock_client = Mock()
    mock_client.chat_messages.create.side_effect = Exception("Simulated API failure")
    return mock_client


@pytest.fixture
def orchestrator_with_partial_failure(mock_env):
    """Orchestrator where some chatflows fail."""
    def mock_chat_client_factory(api_key, **kwargs):
        mock_client = Mock()
        if "test-api-key-1" in api_key:
            # First client succeeds
            mock_client.create_chat_message.return_value = Mock(
                json=lambda: {
                    "answer": f"Success response from {api_key}",
                    "conversation_id": "test-conversation-id",
                    "message_id": "test-message-id",
                }
            )
        else:
            # Second client fails
            mock_client.create_chat_message.side_effect = Exception("Simulated failure")
        return mock_client
    
    with patch('orchestrator.ChatClient', side_effect=mock_chat_client_factory):
        orchestrator = DifyOrchestrator()
        yield orchestrator


@pytest.fixture(scope="session")
def performance_test_data():
    """Data for performance testing."""
    return {
        "small_query": "Test",
        "medium_query": "This is a medium-length test query " * 10,
        "large_query": "This is a large test query " * 100,
        "batch_queries": [f"Batch test query {i}" for i in range(10)],
    }


class MockResponseGenerator:
    """Helper class for generating mock responses."""
    
    @staticmethod
    def success_response(content="Test response", chatflow_name="test-chatflow"):
        return {
            "answer": f"{content} from {chatflow_name}",
            "conversation_id": f"conv-{chatflow_name}",
            "message_id": f"msg-{chatflow_name}",
            "created_at": 1234567890,
            "feedback": None
        }
    
    @staticmethod
    def error_response(error_msg="Test error"):
        raise Exception(error_msg)


@pytest.fixture
def mock_response_generator():
    """Fixture providing MockResponseGenerator."""
    return MockResponseGenerator()


# Pytest marks for organizing tests
pytestmark = [
    pytest.mark.filterwarnings("ignore::DeprecationWarning"),
]


def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line(
        "markers",
        "unit: Unit tests that don't require external dependencies"
    )
    config.addinivalue_line(
        "markers", 
        "integration: Integration tests that require real API calls"
    )
    config.addinivalue_line(
        "markers",
        "slow: Slow tests that may take longer to run"
    )
    config.addinivalue_line(
        "markers",
        "requires_env: Tests that require specific environment setup"
    )
    config.addinivalue_line(
        "markers",
        "backward_compatibility: Tests for backward compatibility"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file names."""
    for item in items:
        # Add markers based on test file names
        if "unit" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        elif "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
            item.add_marker(pytest.mark.requires_env)
        elif "backward_compatibility" in item.nodeid:
            item.add_marker(pytest.mark.backward_compatibility)
        
        # Mark slow tests
        if "performance" in item.name or "scalability" in item.name:
            item.add_marker(pytest.mark.slow)
