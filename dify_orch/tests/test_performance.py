"""
Performance tests for Dify Orchestrator.
These tests measure performance characteristics and identify bottlenecks.
"""
import pytest
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from orchestrator import DifyOrchestrator


@pytest.mark.slow
@pytest.mark.performance
class TestResponseTime:
    """Test response time performance."""

    def test_single_chatflow_response_time(self, orchestrator_with_mock_client, sample_test_queries):
        """Test response time for single chatflow calls."""
        orchestrator = orchestrator_with_mock_client
        chatflow_name = orchestrator.get_chatflow_names()[0]
        
        response_times = []
        
        # Measure response time over multiple calls
        for _ in range(10):
            start_time = time.time()
            response = orchestrator.send_to_chatflow(
                chatflow_name=chatflow_name,
                query=sample_test_queries["simple"]
            )
            end_time = time.time()
            
            assert "answer" in response
            response_times.append(end_time - start_time)
        
        # Performance assertions
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        
        # Mock should be very fast
        assert avg_response_time < 0.1, f"Average response time too slow: {avg_response_time:.3f}s"
        assert max_response_time < 0.2, f"Max response time too slow: {max_response_time:.3f}s"

    def test_multiple_chatflow_response_time(self, orchestrator_with_mock_client, sample_test_queries):
        """Test response time for multiple chatflow calls."""
        orchestrator = orchestrator_with_mock_client
        chatflow_names = orchestrator.get_chatflow_names()
        
        if len(chatflow_names) < 2:
            pytest.skip("Need at least 2 chatflows for multiple chatflow performance test")
        
        start_time = time.time()
        response = orchestrator.send_to_multiple_chatflows(
            chatflow_names=chatflow_names,
            query=sample_test_queries["simple"]
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response["status"] == "success"
        # Multiple chatflow calls should still be reasonably fast with mocks
        assert response_time < 0.5, f"Multiple chatflow response time too slow: {response_time:.3f}s"

    def test_sequential_orchestration_performance(self, orchestrator_with_mock_client):
        """Test performance of sequential orchestration."""
        orchestrator = orchestrator_with_mock_client
        chatflow_names = orchestrator.get_chatflow_names()
        
        if len(chatflow_names) < 2:
            pytest.skip("Need at least 2 chatflows for sequential performance test")
        
        start_time = time.time()
        result = orchestrator.orchestrate_sequential(
            chatflow_sequence=chatflow_names,
            initial_query="Performance test query"
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert result["status"] == "success"
        # Sequential calls should complete reasonably quickly with mocks
        expected_max_time = len(chatflow_names) * 0.1 + 0.2  # Allow 0.1s per chatflow + overhead
        assert response_time < expected_max_time, f"Sequential response time too slow: {response_time:.3f}s"


@pytest.mark.slow
@pytest.mark.performance
class TestThroughput:
    """Test throughput and concurrent performance."""

    def test_concurrent_single_chatflow_calls(self, orchestrator_with_mock_client, performance_test_data):
        """Test concurrent calls to single chatflow."""
        orchestrator = orchestrator_with_mock_client
        chatflow_name = orchestrator.get_chatflow_names()[0]
        
        def make_call(query_index):
            try:
                response = orchestrator.send_to_chatflow(
                    chatflow_name=chatflow_name,
                    query=f"Concurrent test query {query_index}"
                )
                return response is not None and "answer" in response
            except Exception:
                return False
        
        start_time = time.time()
        
        # Make 10 concurrent calls
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_call, i) for i in range(10)]
            results = [future.result() for future in as_completed(futures)]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        success_count = sum(results)
        
        # All calls should succeed
        assert success_count == 10, f"Only {success_count}/10 concurrent calls succeeded"
        
        # Total time should be reasonable (concurrent calls shouldn't take 10x longer)
        assert total_time < 2.0, f"Concurrent calls took too long: {total_time:.3f}s"

    def test_batch_processing_performance(self, orchestrator_with_mock_client, performance_test_data):
        """Test batch processing performance."""
        orchestrator = orchestrator_with_mock_client
        chatflow_names = orchestrator.get_chatflow_names()
        
        queries = performance_test_data["batch_queries"]
        
        start_time = time.time()
        
        # Process batch of queries
        results = []
        for query in queries:
            try:
                response = orchestrator.send_to_chatflow(
                    chatflow_name=chatflow_names[0],
                    query=query
                )
                results.append(response)
            except Exception:
                results.append(None)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        successful_results = [r for r in results if r is not None and "answer" in r]
        
        # Calculate throughput
        throughput = len(successful_results) / total_time
        
        assert len(successful_results) == len(queries), "Not all batch queries succeeded"
        # With mocks, should achieve high throughput
        assert throughput > 50, f"Throughput too low: {throughput:.1f} queries/second"


@pytest.mark.slow
@pytest.mark.performance
class TestMemoryUsage:
    """Test memory usage patterns."""

    def test_memory_usage_stability(self, orchestrator_with_mock_client):
        """Test that memory usage remains stable over multiple calls."""
        import psutil
        import os
        
        orchestrator = orchestrator_with_mock_client
        chatflow_name = orchestrator.get_chatflow_names()[0]
        
        process = psutil.Process(os.getpid())
        
        # Baseline memory usage
        initial_memory = process.memory_info().rss
        
        # Make many calls
        for i in range(100):
            response = orchestrator.send_to_chatflow(
                chatflow_name=chatflow_name,
                query=f"Memory test query {i}"
            )
            assert "answer" in response
        
        # Check memory after calls
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 10MB for 100 calls)
        memory_increase_mb = memory_increase / (1024 * 1024)
        assert memory_increase_mb < 10, f"Memory increased by {memory_increase_mb:.1f}MB"

    def test_large_response_handling(self, orchestrator_with_mock_client):
        """Test handling of large responses."""
        orchestrator = orchestrator_with_mock_client
        chatflow_name = orchestrator.get_chatflow_names()[0]
        
        # Mock a large response
        original_create = orchestrator.chatflows[chatflow_name].client.chat_messages.create
        
        def mock_large_response(*args, **kwargs):
            return {
                "answer": "Large response content " * 1000,  # Simulate large response
                "conversation_id": "test-conv-id",
                "message_id": "test-msg-id",
                "created_at": 1234567890
            }
        
        orchestrator.chatflows[chatflow_name].client.chat_messages.create = mock_large_response
        
        try:
            response = orchestrator.send_to_chatflow(
                chatflow_name=chatflow_name,
                query="Request for large response"
            )
            
            assert "answer" in response
            assert len(response["answer"]) > 10000  # Should be large
            
        finally:
            # Restore original method
            orchestrator.chatflows[chatflow_name].client.chat_messages.create = original_create


@pytest.mark.slow
@pytest.mark.performance
class TestScalability:
    """Test scalability with different configurations."""

    def test_scaling_with_chatflow_count(self, mock_env):
        """Test performance scaling with different numbers of chatflows."""
        # Test with different chatflow counts
        chatflow_counts = [1, 2, 5]
        performance_results = {}
        
        for count in chatflow_counts:
            # Create environment with specified chatflow count
            test_env = mock_env.copy()
            test_env["DIFY_CHATFLOW_COUNT"] = str(count)
            
            # Add required chatflow configurations
            for i in range(1, count + 1):
                test_env[f"DIFY_CHATFLOW_{i}_API_KEY"] = f"test-key-{i}"
                test_env[f"DIFY_CHATFLOW_{i}_NAME"] = f"test-chatflow-{i}"
                test_env[f"DIFY_CHATFLOW_{i}_DESCRIPTION"] = f"Test chatflow {i}"
            
            try:
                from unittest.mock import patch, Mock
                
                with patch.dict('os.environ', test_env):
                    with patch('orchestrator.DifyClient') as mock_client_class:
                        mock_client = Mock()
                        mock_client.chat_messages.create.return_value = {
                            "answer": "Test response",
                            "conversation_id": "test-conv",
                            "message_id": "test-msg",
                        }
                        mock_client_class.return_value = mock_client
                        
                        orchestrator = DifyOrchestrator()
                        
                        # Measure initialization time
                        start_time = time.time()
                        chatflow_names = orchestrator.get_chatflow_names()
                        init_time = time.time() - start_time
                        
                        # Measure send_to_all_chatflows time
                        start_time = time.time()
                        response = orchestrator.send_to_all_chatflows("Test query")
                        all_chatflows_time = time.time() - start_time
                        
                        performance_results[count] = {
                            "init_time": init_time,
                            "all_chatflows_time": all_chatflows_time,
                            "chatflow_count": len(chatflow_names)
                        }
                        
                        assert len(chatflow_names) == count
                        assert response["status"] == "success"
                        
            except Exception as e:
                pytest.fail(f"Failed with {count} chatflows: {e}")
        
        # Verify scaling characteristics
        if len(performance_results) > 1:
            # Initialization time should scale reasonably
            max_init_time = max(result["init_time"] for result in performance_results.values())
            assert max_init_time < 1.0, f"Initialization too slow with multiple chatflows: {max_init_time:.3f}s"
            
            # All chatflows time should scale roughly linearly
            for count, result in performance_results.items():
                expected_max_time = count * 0.1 + 0.5  # Linear scaling + overhead
                actual_time = result["all_chatflows_time"]
                assert actual_time < expected_max_time, f"send_to_all_chatflows too slow with {count} chatflows: {actual_time:.3f}s"

    def test_error_handling_performance(self, orchestrator_with_partial_failure):
        """Test that error handling doesn't significantly impact performance."""
        orchestrator = orchestrator_with_partial_failure
        chatflow_names = orchestrator.get_chatflow_names()
        
        # Mix of valid and invalid chatflow names
        mixed_names = chatflow_names + ["invalid-1", "invalid-2"]
        
        start_time = time.time()
        response = orchestrator.send_to_multiple_chatflows(
            chatflow_names=mixed_names,
            query="Error handling performance test"
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response["status"] == "partial_success"
        # Error handling shouldn't significantly slow down the response
        assert response_time < 1.0, f"Error handling too slow: {response_time:.3f}s"


@pytest.mark.slow
@pytest.mark.performance
class TestRealWorldScenarios:
    """Test performance in realistic usage scenarios."""

    def test_typical_usage_pattern(self, orchestrator_with_mock_client, sample_test_queries):
        """Test performance of typical usage patterns."""
        orchestrator = orchestrator_with_mock_client
        chatflow_names = orchestrator.get_chatflow_names()
        
        # Simulate typical usage: mix of individual and multiple calls
        start_time = time.time()
        
        # 5 individual calls
        for i in range(5):
            response = orchestrator.send_to_chatflow(
                chatflow_name=chatflow_names[0],
                query=sample_test_queries["simple"]
            )
            assert "answer" in response
        
        # 2 multiple chatflow calls
        if len(chatflow_names) > 1:
            for i in range(2):
                response = orchestrator.send_to_multiple_chatflows(
                    chatflow_names=chatflow_names,
                    query=sample_test_queries["complex"]
                )
                assert response["status"] == "success"
        
        # 1 sequential call
        if len(chatflow_names) > 1:
            result = orchestrator.orchestrate_sequential(
                chatflow_sequence=chatflow_names,
                initial_query=sample_test_queries["creative"]
            )
            assert result["status"] == "success"
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Typical usage should complete quickly with mocks
        assert total_time < 2.0, f"Typical usage pattern too slow: {total_time:.3f}s"

    def test_burst_load_handling(self, orchestrator_with_mock_client):
        """Test handling of burst loads."""
        orchestrator = orchestrator_with_mock_client
        chatflow_name = orchestrator.get_chatflow_names()[0]
        
        def burst_calls():
            success_count = 0
            for i in range(20):  # 20 rapid calls
                try:
                    response = orchestrator.send_to_chatflow(
                        chatflow_name=chatflow_name,
                        query=f"Burst test {i}"
                    )
                    if "answer" in response:
                        success_count += 1
                except Exception:
                    pass
            return success_count
        
        start_time = time.time()
        success_count = burst_calls()
        end_time = time.time()
        
        burst_time = end_time - start_time
        
        # Should handle burst load successfully
        assert success_count >= 18, f"Only {success_count}/20 burst calls succeeded"
        assert burst_time < 5.0, f"Burst load handling too slow: {burst_time:.3f}s"
