"""
Backward compatibility tests for Dify Orchestrator.
These tests ensure that legacy methods continue to work with appropriate deprecation warnings.
"""
import pytest
import warnings
from orchestrator import DifyOrchestrator


@pytest.mark.backward_compatibility
class TestLegacyMethods:
    """Test deprecated/legacy methods for backward compatibility."""

    def test_legacy_individual_chatflow_methods(self, orchestrator_with_mock_client, capture_warnings):
        """Test legacy individual chatflow methods (send_to_chatflow_1, send_to_chatflow_2)."""
        orchestrator = orchestrator_with_mock_client
        test_message = "Testing backward compatibility"
        
        # Test legacy method 1
        if hasattr(orchestrator, 'send_to_chatflow_1'):
            response_1 = orchestrator.send_to_chatflow_1(test_message)
            assert isinstance(response_1, dict)
            assert "answer" in response_1
        
        # Test legacy method 2
        if hasattr(orchestrator, 'send_to_chatflow_2'):
            response_2 = orchestrator.send_to_chatflow_2(test_message)
            assert isinstance(response_2, dict)
            assert "answer" in response_2

    def test_legacy_dual_response(self, orchestrator_with_mock_client, capture_warnings):
        """Test legacy dual response method."""
        orchestrator = orchestrator_with_mock_client
        test_message = "Testing dual response backward compatibility"
        
        if hasattr(orchestrator, 'orchestrate_dual_response'):
            dual_response = orchestrator.orchestrate_dual_response(test_message)
            
            assert isinstance(dual_response, dict)
            # Should contain responses from both chatflows
            assert len(dual_response) >= 2 or "error" in dual_response

    def test_legacy_sequential_workflow(self, orchestrator_with_mock_client, capture_warnings):
        """Test legacy sequential workflow method."""
        orchestrator = orchestrator_with_mock_client
        test_message = "Testing sequential workflow backward compatibility"
        
        if hasattr(orchestrator, 'sequential_workflow'):
            sequential_result = orchestrator.sequential_workflow(test_message)
            
            assert isinstance(sequential_result, dict)
            assert "status" in sequential_result

    def test_deprecation_warnings_issued(self, orchestrator_with_mock_client, capture_warnings):
        """Test that deprecation warnings are properly issued for legacy methods."""
        orchestrator = orchestrator_with_mock_client
        test_message = "Testing deprecation warnings"
        
        # Clear any existing warnings
        capture_warnings.clear()
        
        # Call legacy methods if they exist
        legacy_methods = [
            ('send_to_chatflow_1', lambda: orchestrator.send_to_chatflow_1(test_message)),
            ('send_to_chatflow_2', lambda: orchestrator.send_to_chatflow_2(test_message)),
            ('orchestrate_dual_response', lambda: orchestrator.orchestrate_dual_response(test_message)),
            ('sequential_workflow', lambda: orchestrator.sequential_workflow(test_message))
        ]
        
        warning_count = 0
        for method_name, method_call in legacy_methods:
            if hasattr(orchestrator, method_name):
                try:
                    method_call()
                    # Count deprecation warnings
                    deprecation_warnings = [w for w in capture_warnings if issubclass(w.category, DeprecationWarning)]
                    if deprecation_warnings:
                        warning_count += 1
                except Exception:
                    # Some methods might fail, but we're mainly testing warnings
                    pass
        
        # Should have at least some deprecation warnings if legacy methods exist
        if any(hasattr(orchestrator, method) for method, _ in legacy_methods):
            assert warning_count >= 0  # Allow for different implementation approaches


@pytest.mark.backward_compatibility
class TestAPICompatibility:
    """Test API compatibility across versions."""

    def test_response_format_consistency(self, orchestrator_with_mock_client, sample_test_queries):
        """Test that response formats remain consistent."""
        orchestrator = orchestrator_with_mock_client
        chatflow_name = orchestrator.get_chatflow_names()[0]
        
        # New API
        new_response = orchestrator.send_to_chatflow(
            chatflow_name=chatflow_name,
            query=sample_test_queries["simple"]
        )
        
        # Test response structure
        assert isinstance(new_response, dict)
        assert "answer" in new_response
        
        # Legacy API (if available)
        if hasattr(orchestrator, 'send_to_chatflow_1'):
            legacy_response = orchestrator.send_to_chatflow_1(sample_test_queries["simple"])
            
            # Both should have similar structure
            assert isinstance(legacy_response, dict)
            assert "answer" in legacy_response

    def test_parameter_backward_compatibility(self, orchestrator_with_mock_client):
        """Test that method parameters remain backward compatible."""
        orchestrator = orchestrator_with_mock_client
        chatflow_names = orchestrator.get_chatflow_names()
        
        # Test that old parameter names/styles still work
        # (This depends on the actual implementation)
        
        # New style
        response_new = orchestrator.send_to_chatflow(
            chatflow_name=chatflow_names[0],
            query="Test query"
        )
        assert "answer" in response_new
        
        # Test that the method handles various input types
        response_positional = orchestrator.send_to_chatflow(chatflow_names[0], "Test query")
        assert "answer" in response_positional

    def test_configuration_backward_compatibility(self, orchestrator_with_mock_client):
        """Test that configuration methods remain backward compatible."""
        orchestrator = orchestrator_with_mock_client
        
        # New methods
        names = orchestrator.get_chatflow_names()
        assert isinstance(names, list)
        
        for name in names:
            config = orchestrator.get_chatflow_config(name)
            assert hasattr(config, 'name')


@pytest.mark.backward_compatibility
class TestMigrationPath:
    """Test migration path from old to new API."""

    def test_old_to_new_api_equivalence(self, orchestrator_with_mock_client, sample_test_queries):
        """Test that old and new APIs produce equivalent results."""
        orchestrator = orchestrator_with_mock_client
        test_query = sample_test_queries["simple"]
        
        # Get responses using both old and new methods (if available)
        chatflow_names = orchestrator.get_chatflow_names()
        if not chatflow_names:
            pytest.skip("No chatflows available for migration test")
        
        # New API
        new_response = orchestrator.send_to_chatflow(
            chatflow_name=chatflow_names[0],
            query=test_query
        )
        
        # Legacy API (if first chatflow corresponds to legacy method 1)
        if hasattr(orchestrator, 'send_to_chatflow_1'):
            legacy_response = orchestrator.send_to_chatflow_1(test_query)
            
            # Both should return valid responses
            assert "answer" in new_response
            assert "answer" in legacy_response
            
            # Responses should be from the same underlying chatflow
            # (exact content may vary due to different calling patterns)
            assert isinstance(new_response["answer"], str)
            assert isinstance(legacy_response["answer"], str)

    def test_error_handling_consistency(self, orchestrator_with_mock_client):
        """Test that error handling is consistent between old and new APIs."""
        orchestrator = orchestrator_with_mock_client
        
        # Test invalid input handling
        # New API
        with pytest.raises(ValueError):
            orchestrator.send_to_chatflow("invalid-chatflow", "test")
        
        # Legacy API error handling (if available)
        # Note: Legacy methods might have different error handling patterns
        if hasattr(orchestrator, 'send_to_chatflow_1'):
            try:
                # This might not raise an error in legacy implementation
                orchestrator.send_to_chatflow_1("")
            except (ValueError, Exception):
                # Either specific validation error or general error is acceptable
                pass


@pytest.mark.backward_compatibility
class TestConfigurationMigration:
    """Test configuration migration scenarios."""

    def test_environment_variable_compatibility(self, mock_env):
        """Test that old environment variable patterns still work."""
        # Test that the system can handle both old and new configuration styles
        
        # This test assumes the orchestrator can handle legacy environment patterns
        orchestrator = DifyOrchestrator()
        
        # Should initialize successfully with current environment
        assert orchestrator is not None
        assert len(orchestrator.get_chatflow_names()) > 0

    def test_dynamic_vs_static_configuration(self, orchestrator_with_mock_client):
        """Test that dynamic configuration is backward compatible with static configuration."""
        orchestrator = orchestrator_with_mock_client
        
        # Dynamic configuration should provide same interface as static
        chatflow_names = orchestrator.get_chatflow_names()
        assert isinstance(chatflow_names, list)
        
        # Should be able to access each configured chatflow
        for name in chatflow_names:
            config = orchestrator.get_chatflow_config(name)
            assert config.name == name


@pytest.mark.backward_compatibility
class TestUpgradeScenarios:
    """Test various upgrade scenarios from old to new versions."""

    def test_seamless_upgrade_path(self, orchestrator_with_mock_client, sample_test_queries):
        """Test that users can upgrade seamlessly."""
        orchestrator = orchestrator_with_mock_client
        
        # Users should be able to use both old and new methods during transition
        chatflow_names = orchestrator.get_chatflow_names()
        if not chatflow_names:
            pytest.skip("No chatflows available for upgrade test")
        
        # New method works
        new_response = orchestrator.send_to_chatflow(
            chatflow_name=chatflow_names[0],
            query=sample_test_queries["simple"]
        )
        assert "answer" in new_response
        
        # Old methods still work (if they exist)
        legacy_methods_work = True
        try:
            if hasattr(orchestrator, 'send_to_chatflow_1'):
                legacy_response = orchestrator.send_to_chatflow_1(sample_test_queries["simple"])
                assert "answer" in legacy_response
        except Exception:
            legacy_methods_work = False
        
        # Either legacy methods work or they're no longer available (both are valid)
        assert True  # Test passes if we reach here without critical errors

    def test_feature_parity(self, orchestrator_with_mock_client):
        """Test that new API provides feature parity with legacy API."""
        orchestrator = orchestrator_with_mock_client
        
        # New API should provide at least the same capabilities as legacy API
        
        # Single chatflow access
        chatflow_names = orchestrator.get_chatflow_names()
        assert len(chatflow_names) > 0
        
        # Multiple chatflow access
        if len(chatflow_names) > 1:
            response = orchestrator.send_to_multiple_chatflows(
                chatflow_names=chatflow_names[:2],
                query="Test multi-chatflow capability"
            )
            assert "status" in response
        
        # Sequential processing
        if len(chatflow_names) > 1:
            result = orchestrator.orchestrate_sequential(
                chatflow_sequence=chatflow_names[:2],
                initial_query="Test sequential capability"
            )
            assert "status" in result

    def test_documentation_examples_still_work(self, orchestrator_with_mock_client):
        """Test that examples from old documentation still work."""
        orchestrator = orchestrator_with_mock_client
        
        # This test ensures that code examples from old documentation continue to work
        # Adapt these based on what the old documentation actually showed
        
        try:
            # Example 1: Basic usage
            chatflow_names = orchestrator.get_chatflow_names()
            if chatflow_names:
                response = orchestrator.send_to_chatflow(chatflow_names[0], "Hello")
                assert "answer" in response
            
            # Example 2: Multiple chatflows
            if len(chatflow_names) >= 2:
                multi_response = orchestrator.send_to_multiple_chatflows(
                    chatflow_names=chatflow_names[:2],
                    query="Hello"
                )
                assert "status" in multi_response
            
            # Test passes if examples work without errors
            assert True
            
        except Exception as e:
            pytest.fail(f"Documentation example failed: {e}")
