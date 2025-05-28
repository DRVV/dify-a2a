"""
Integration tests for Dify Orchestrator.
These tests require real API connections and environment setup.
"""
import pytest
import time
from orchestrator import DifyOrchestrator


@pytest.mark.integration
@pytest.mark.requires_env
class TestRealAPIIntegration:
    """Test integration with real Dify API endpoints."""

    def test_real_orchestrator_initialization(self, real_orchestrator):
        """Test initialization with real environment."""
        orchestrator = real_orchestrator
        
        assert orchestrator is not None
        assert len(orchestrator.get_chatflow_names()) > 0

    def test_real_individual_chatflow_call(self, real_orchestrator, sample_test_queries):
        """Test real API call to individual chatflow."""
        orchestrator = real_orchestrator
        chatflow_names = orchestrator.get_chatflow_names()
        
        if not chatflow_names:
            pytest.skip("No chatflows configured for integration test")
        
        chatflow_name = chatflow_names[0]
        response = orchestrator.send_to_chatflow(
            chatflow_name=chatflow_name,
            query=sample_test_queries["simple"]
        )
        
        assert isinstance(response, dict)
        assert "answer" in response
        assert isinstance(response["answer"], str)
        assert len(response["answer"]) > 0

    def test_real_multiple_chatflow_calls(self, real_orchestrator, sample_test_queries):
        """Test real API calls to multiple chatflows."""
        orchestrator = real_orchestrator
        chatflow_names = orchestrator.get_chatflow_names()
        
        if len(chatflow_names) < 2:
            pytest.skip("Need at least 2 chatflows for multiple chatflow test")
        
        response = orchestrator.send_to_multiple_chatflows(
            chatflow_names=chatflow_names[:2],
            query=sample_test_queries["simple"]
        )
        
        assert response["status"] in ["success", "partial_success"]
        assert response["success_count"] > 0
        assert "responses" in response

    def test_real_sequential_orchestration(self, real_orchestrator):
        """Test real sequential orchestration."""
        orchestrator = real_orchestrator
        chatflow_names = orchestrator.get_chatflow_names()
        
        if len(chatflow_names) < 2:
            pytest.skip("Need at least 2 chatflows for sequential test")
        
        result = orchestrator.orchestrate_sequential(
            chatflow_sequence=chatflow_names[:2],
            initial_query="Generate a short greeting message"
        )
        
        assert result["status"] == "success"
        assert "final_answer" in result
        assert "step_results" in result

    @pytest.mark.slow
    def test_api_response_time(self, real_orchestrator, sample_test_queries):
        """Test API response time meets reasonable expectations."""
        orchestrator = real_orchestrator
        chatflow_names = orchestrator.get_chatflow_names()
        
        if not chatflow_names:
            pytest.skip("No chatflows configured for response time test")
        
        chatflow_name = chatflow_names[0]
        start_time = time.time()
        
        response = orchestrator.send_to_chatflow(
            chatflow_name=chatflow_name,
            query=sample_test_queries["simple"]
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Response should complete within 30 seconds
        assert response_time < 30.0, f"Response took {response_time:.2f} seconds"
        assert "answer" in response

    def test_concurrent_api_calls(self, real_orchestrator, sample_test_queries):
        """Test handling of concurrent API calls."""
        orchestrator = real_orchestrator
        chatflow_names = orchestrator.get_chatflow_names()
        
        if len(chatflow_names) < 2:
            pytest.skip("Need at least 2 chatflows for concurrent test")
        
        # Test sending to all chatflows concurrently
        response = orchestrator.send_to_all_chatflows(sample_test_queries["simple"])
        
        assert response["status"] in ["success", "partial_success"]
        assert response["success_count"] > 0


@pytest.mark.integration
class TestEnvironmentConfiguration:
    """Test environment configuration scenarios."""

    def test_environment_variable_loading(self, real_orchestrator):
        """Test that environment variables are loaded correctly."""
        orchestrator = real_orchestrator
        
        # Should have loaded configuration from environment
        chatflow_names = orchestrator.get_chatflow_names()
        assert len(chatflow_names) > 0
        
        # Each chatflow should have proper configuration
        for name in chatflow_names:
            config = orchestrator.get_chatflow_config(name)
            assert config.name == name
            assert hasattr(config, 'description')

    def test_dynamic_chatflow_count(self, real_orchestrator):
        """Test that dynamic chatflow count works correctly."""
        orchestrator = real_orchestrator
        
        # The number of chatflows should match the configured count
        import os
        expected_count = int(os.getenv("DIFY_CHATFLOW_COUNT", "0"))
        actual_count = len(orchestrator.get_chatflow_names())
        
        assert actual_count == expected_count


@pytest.mark.integration
@pytest.mark.slow
class TestStressAndReliability:
    """Test system under stress and reliability scenarios."""

    def test_rapid_sequential_calls(self, real_orchestrator):
        """Test rapid sequential API calls."""
        orchestrator = real_orchestrator
        chatflow_names = orchestrator.get_chatflow_names()
        
        if not chatflow_names:
            pytest.skip("No chatflows configured for stress test")
        
        chatflow_name = chatflow_names[0]
        success_count = 0
        
        # Make 5 rapid calls
        for i in range(5):
            try:
                response = orchestrator.send_to_chatflow(
                    chatflow_name=chatflow_name,
                    query=f"Test message {i+1}"
                )
                if "answer" in response:
                    success_count += 1
            except Exception as e:
                # Log the error but continue testing
                print(f"Call {i+1} failed: {e}")
        
        # At least 80% should succeed
        assert success_count >= 4, f"Only {success_count}/5 calls succeeded"

    def test_large_query_handling(self, real_orchestrator, performance_test_data):
        """Test handling of large queries."""
        orchestrator = real_orchestrator
        chatflow_names = orchestrator.get_chatflow_names()
        
        if not chatflow_names:
            pytest.skip("No chatflows configured for large query test")
        
        chatflow_name = chatflow_names[0]
        
        # Test with medium-sized query
        response = orchestrator.send_to_chatflow(
            chatflow_name=chatflow_name,
            query=performance_test_data["medium_query"]
        )
        
        assert "answer" in response
        assert isinstance(response["answer"], str)

    def test_error_recovery(self, real_orchestrator):
        """Test system recovery from errors."""
        orchestrator = real_orchestrator
        chatflow_names = orchestrator.get_chatflow_names()
        
        if len(chatflow_names) < 1:
            pytest.skip("Need at least 1 chatflow for error recovery test")
        
        # Mix valid and invalid chatflow names
        mixed_names = [chatflow_names[0], "definitely-invalid-chatflow-name"]
        
        response = orchestrator.send_to_multiple_chatflows(
            chatflow_names=mixed_names,
            query="Test error recovery"
        )
        
        # Should handle partial failure gracefully
        assert response["status"] == "partial_success"
        assert response["success_count"] == 1
        assert response["total_count"] == 2
        assert len(response["errors"]) == 1


@pytest.mark.integration
class TestEndToEndWorkflows:
    """Test complete end-to-end workflows."""

    def test_complete_analysis_workflow(self, real_orchestrator):
        """Test a complete analysis workflow using multiple chatflows."""
        orchestrator = real_orchestrator
        chatflow_names = orchestrator.get_chatflow_names()
        
        if len(chatflow_names) < 2:
            pytest.skip("Need at least 2 chatflows for analysis workflow")
        
        # Step 1: Initial analysis
        initial_query = "Analyze the current trends in artificial intelligence"
        initial_response = orchestrator.send_to_chatflow(
            chatflow_name=chatflow_names[0],
            query=initial_query
        )
        
        assert "answer" in initial_response
        
        # Step 2: Follow-up analysis based on first response
        follow_up_query = f"Based on this analysis: '{initial_response['answer'][:200]}', provide specific recommendations"
        
        if len(chatflow_names) > 1:
            follow_up_response = orchestrator.send_to_chatflow(
                chatflow_name=chatflow_names[1],
                query=follow_up_query
            )
            
            assert "answer" in follow_up_response
        
        # Step 3: Sequential workflow combining both
        sequential_result = orchestrator.orchestrate_sequential(
            chatflow_sequence=chatflow_names[:2],
            initial_query="Provide a comprehensive AI trend analysis with actionable insights"
        )
        
        assert sequential_result["status"] == "success"
        assert "final_answer" in sequential_result

    def test_comparison_workflow(self, real_orchestrator):
        """Test workflow that compares responses from multiple chatflows."""
        orchestrator = real_orchestrator
        chatflow_names = orchestrator.get_chatflow_names()
        
        if len(chatflow_names) < 2:
            pytest.skip("Need at least 2 chatflows for comparison workflow")
        
        query = "What are the key benefits of cloud computing?"
        
        # Get responses from all chatflows
        comparison_response = orchestrator.send_to_all_chatflows(query)
        
        assert comparison_response["status"] in ["success", "partial_success"]
        assert comparison_response["success_count"] >= 2
        
        # Verify we have distinct responses
        responses = comparison_response["responses"]
        assert len(responses) >= 2
        
        # Each response should have the expected structure
        for chatflow_name, response in responses.items():
            assert "answer" in response
            assert isinstance(response["answer"], str)
            assert len(response["answer"]) > 0
