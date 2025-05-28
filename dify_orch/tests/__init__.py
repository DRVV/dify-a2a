"""
Dify Orchestrator Test Suite

This package contains comprehensive tests for the Dify Orchestrator including:
- Unit tests with mocked dependencies
- Integration tests with real API calls
- Backward compatibility tests
- Performance and stress tests

Test Categories:
- unit: Fast tests with mocked dependencies
- integration: Tests requiring real API connections
- slow: Performance and stress tests
- backward_compatibility: Legacy API compatibility tests
- requires_env: Tests requiring specific environment setup

Usage:
    # Run all tests
    pytest

    # Run only unit tests
    pytest -m unit

    # Run only integration tests (requires environment setup)
    pytest -m integration

    # Run tests with coverage
    pytest --cov=orchestrator

    # Run tests in parallel
    pytest -n auto

    # Generate HTML test report
    pytest --html=test_report.html
"""

__version__ = "1.0.0"
