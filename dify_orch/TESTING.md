# Testing Guide for Dify Orchestrator

This document provides comprehensive information about testing the Dify Orchestrator using the new pytest-based testing framework.

## Overview

The testing framework has been migrated from a single monolithic test script to a comprehensive pytest-based test suite that provides:

- **Enhanced test organization**: Tests are organized by category and functionality
- **Better test isolation**: Each test runs independently with proper setup/teardown
- **Comprehensive coverage**: Unit tests, integration tests, performance tests, and backward compatibility tests
- **Mock support**: Proper mocking for fast unit tests without external dependencies
- **Parallel execution**: Tests can run in parallel for faster feedback
- **Detailed reporting**: HTML reports, coverage reports, and detailed failure information

## Test Categories

### 🚀 Unit Tests (`-m unit`)
Fast tests that use mocked dependencies and don't require external API calls.

**Location**: `tests/test_unit_orchestrator.py`

**Features**:
- Mocked Dify API clients
- Fast execution (< 1 second per test)
- Test core functionality and edge cases
- Input validation and error handling

**Run**: 
```bash
python run_tests.py --unit
# or
pytest -m unit
```

### 🔗 Integration Tests (`-m integration`)
Tests that require real API connections and environment setup.

**Location**: `tests/test_integration_orchestrator.py`

**Features**:
- Real API calls to Dify services
- Environment configuration testing
- End-to-end workflow validation
- API response time validation

**Requirements**:
- Valid `.env` file with API credentials
- Active Dify service endpoints

**Run**:
```bash
python run_tests.py --integration
# or
pytest -m integration
```

### ⚡ Performance Tests (`-m performance`)
Tests that measure performance characteristics and identify bottlenecks.

**Location**: `tests/test_performance.py`

**Features**:
- Response time measurement
- Throughput testing
- Memory usage analysis
- Concurrent call handling
- Scalability testing

**Run**:
```bash
python run_tests.py --performance
# or
pytest -m performance
```

### 🔄 Backward Compatibility Tests (`-m backward_compatibility`)
Tests that ensure legacy API methods continue to work.

**Location**: `tests/test_backward_compatibility.py`

**Features**:
- Legacy method compatibility
- Deprecation warning validation
- Migration path testing
- API consistency checks

**Run**:
```bash
python run_tests.py --backwards
# or
pytest -m backward_compatibility
```

## Quick Start

### Installation

1. **Install test dependencies**:
   ```bash
   pip install -e .[test]
   # or
   python run_tests.py --install-deps
   ```

2. **Run quick unit tests**:
   ```bash
   python run_tests.py --quick
   ```

3. **Run all tests with coverage**:
   ```bash
   python run_tests.py --all --coverage --html
   ```

### Common Test Commands

```bash
# Quick feedback loop (unit tests only)
python run_tests.py --quick

# Comprehensive testing
python run_tests.py --all --coverage

# Integration testing (requires environment)
python run_tests.py --integration

# Performance benchmarking
python run_tests.py --performance

# Parallel execution for speed
python run_tests.py --parallel

# Generate HTML reports
python run_tests.py --html --coverage
```

## Test Structure

```
tests/
├── __init__.py                     # Test package initialization
├── conftest.py                     # Shared fixtures and configuration
├── test_unit_orchestrator.py       # Unit tests with mocks
├── test_integration_orchestrator.py # Integration tests with real APIs
├── test_backward_compatibility.py  # Legacy API compatibility tests
└── test_performance.py            # Performance and stress tests
```

## Fixtures and Utilities

### Key Fixtures (from `conftest.py`)

- **`orchestrator_with_mock_client`**: Orchestrator with mocked API clients
- **`real_orchestrator`**: Real orchestrator for integration tests
- **`sample_test_queries`**: Various test query types
- **`performance_test_data`**: Data for performance testing
- **`mock_env`**: Mocked environment variables

### Test Markers

- `@pytest.mark.unit`: Fast unit tests
- `@pytest.mark.integration`: Integration tests requiring environment
- `@pytest.mark.slow`: Tests that take longer to run
- `@pytest.mark.performance`: Performance and benchmarking tests
- `@pytest.mark.backward_compatibility`: Legacy compatibility tests
- `@pytest.mark.requires_env`: Tests requiring specific environment setup

## Environment Setup

### For Unit Tests
No special setup required - uses mocked dependencies.

### For Integration Tests
Create a `.env` file with:
```bash
DIFY_BASE_URL=https://api.dify.ai/v1
DIFY_CHATFLOW_COUNT=2
DIFY_CHATFLOW_1_API_KEY=your-api-key-1
DIFY_CHATFLOW_1_NAME=your-chatflow-1
DIFY_CHATFLOW_1_DESCRIPTION=Description for chatflow 1
DIFY_CHATFLOW_2_API_KEY=your-api-key-2
DIFY_CHATFLOW_2_NAME=your-chatflow-2
DIFY_CHATFLOW_2_DESCRIPTION=Description for chatflow 2
```

## Advanced Usage

### Running Specific Tests

```bash
# Run tests matching a pattern
pytest -k "test_initialization"

# Run tests from specific file
pytest tests/test_unit_orchestrator.py

# Run specific test class
pytest tests/test_unit_orchestrator.py::TestOrchestratorInitialization

# Run specific test method
pytest tests/test_unit_orchestrator.py::TestOrchestratorInitialization::test_orchestrator_initialization_success
```

### Custom Test Selection

```bash
# Run tests with multiple markers
pytest -m "unit or integration"

# Exclude slow tests
pytest -m "not slow"

# Run only tests that require environment
pytest -m "requires_env"
```

### Coverage Analysis

```bash
# Basic coverage
pytest --cov=orchestrator

# Coverage with missing lines
pytest --cov=orchestrator --cov-report=term-missing

# HTML coverage report
pytest --cov=orchestrator --cov-report=html

# Fail if coverage below threshold
pytest --cov=orchestrator --cov-fail-under=80
```

### Parallel Execution

```bash
# Auto-detect number of cores
pytest -n auto

# Specify number of workers
pytest -n 4

# Parallel with coverage (requires pytest-cov[toml])
pytest -n auto --cov=orchestrator
```

## Test Development

### Writing New Tests

1. **Choose the appropriate test file** based on test type
2. **Use proper markers** to categorize your test
3. **Use fixtures** for setup and common data
4. **Follow naming conventions**: `test_*` for functions, `Test*` for classes

Example unit test:
```python
@pytest.mark.unit
def test_new_feature(orchestrator_with_mock_client, sample_test_queries):
    """Test new feature functionality."""
    orchestrator = orchestrator_with_mock_client
    
    result = orchestrator.new_feature(sample_test_queries["simple"])
    
    assert result is not None
    assert "expected_field" in result
```

Example integration test:
```python
@pytest.mark.integration
@pytest.mark.requires_env
def test_real_api_feature(real_orchestrator):
    """Test feature with real API."""
    orchestrator = real_orchestrator
    
    result = orchestrator.new_feature("test query")
    
    assert result is not None
    # Additional assertions for real API response
```

### Adding New Fixtures

Add to `conftest.py`:
```python
@pytest.fixture
def my_custom_fixture():
    """Description of what this fixture provides."""
    # Setup code
    data = create_test_data()
    
    yield data
    
    # Teardown code (optional)
    cleanup_test_data(data)
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.8'
    
    - name: Install dependencies
      run: |
        pip install -e .[test]
    
    - name: Run unit tests
      run: |
        pytest -m unit --cov=orchestrator
    
    - name: Run integration tests
      run: |
        pytest -m integration
      env:
        DIFY_BASE_URL: ${{ secrets.DIFY_BASE_URL }}
        DIFY_CHATFLOW_COUNT: 2
        DIFY_CHATFLOW_1_API_KEY: ${{ secrets.DIFY_CHATFLOW_1_API_KEY }}
        # ... other environment variables
```

## Migration from Legacy Tests

The old `test_orchestrator.py` has been preserved for reference, but the new pytest-based tests provide:

### Advantages

1. **Better Organization**: Tests are grouped by functionality
2. **Faster Feedback**: Unit tests run in seconds
3. **Better Isolation**: Each test is independent
4. **More Comprehensive**: Covers edge cases and error conditions
5. **Better Reporting**: Detailed failure information and coverage reports
6. **Parallel Execution**: Tests can run concurrently
7. **Standard Framework**: Uses industry-standard pytest

### Key Differences

| Old Approach | New Approach |
|-------------|--------------|
| Single monolithic test file | Multiple organized test files |
| Manual test orchestration | Pytest automatic discovery |
| Print-based output | Structured test reporting |
| Limited error isolation | Per-test isolation |
| No mocking | Comprehensive mocking |
| Sequential execution only | Parallel execution support |
| Basic pass/fail reporting | Detailed coverage and HTML reports |

### Running Legacy Tests

The original test script is still available:
```bash
python test_orchestrator.py
```

However, we recommend using the new pytest-based tests for development and CI/CD.

## Troubleshooting

### Common Issues

1. **Import Errors**:
   ```bash
   # Make sure you're in the correct directory
   cd dify_orch
   
   # Install in development mode
   pip install -e .
   ```

2. **Missing Dependencies**:
   ```bash
   # Install test dependencies
   pip install -e .[test]
   ```

3. **Environment Issues for Integration Tests**:
   ```bash
   # Check .env file exists and has correct variables
   cat .env
   
   # Run only unit tests if environment setup is problematic
   pytest -m unit
   ```

4. **Slow Tests**:
   ```bash
   # Skip slow tests
   pytest -m "not slow"
   
   # Run in parallel
   pytest -n auto
   ```

### Getting Help

- Check test output for specific error messages
- Use `pytest --tb=long` for detailed tracebacks
- Run with `-v` flag for verbose output
- Check the logs with `--log-cli-level=DEBUG`

## Best Practices

1. **Start with unit tests** for fast feedback
2. **Use integration tests** to verify real API interactions
3. **Run performance tests** before major releases
4. **Maintain high test coverage** (aim for >80%)
5. **Keep tests independent** - each test should be able to run alone
6. **Use descriptive test names** that explain what is being tested
7. **Group related tests** in classes for better organization
8. **Mock external dependencies** in unit tests for reliability and speed
