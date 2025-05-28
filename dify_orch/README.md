# Dify Orchestrator

A scalable Python client for orchestrating multiple Dify chatflows with support for arbitrary numbers of chatflows and various orchestration patterns.

## Features

### 🚀 New Dynamic Features
- **Arbitrary Number of Chatflows**: Support for any number of chatflows (not limited to 2)
- **Dynamic Configuration**: Environment-based chatflow configuration
- **Parallel Orchestration**: Send queries to multiple chatflows simultaneously
- **Sequential Orchestration**: Chain chatflows with customizable execution order
- **Robust Error Handling**: Graceful handling of partial failures
- **Named Chatflows**: Use semantic names instead of numbers

### 🔄 Backward Compatibility
- **Legacy Method Support**: All existing methods continue to work
- **Deprecation Warnings**: Clear migration guidance
- **Seamless Transition**: Upgrade without breaking existing code

## 🌐 Web UI Interface

The orchestrator includes a **Chainlit-based web interface** for interactive debugging and testing:

### Quick Start Web UI
```bash
# Navigate to the dify_orch directory
cd dify_orch

# Install chainlit (if not already installed)
pip install chainlit

# Run the web interface
python run_chainlit.py
# OR
chainlit run chainlit_app.py --port 8000
```

### Web UI Features
- 💬 **Interactive chat interface** - Type messages and see responses from all chatflows
- 🔄 **Parallel execution** - Send messages to all configured chatflows simultaneously  
- 🤖 **Multi-assistant view** - Each chatflow appears as a separate chat assistant with unique avatars
- ⚡ **Real-time responses** - See results as they arrive, no waiting for all responses
- 🐛 **Debug information** - JSON response details and error messages for troubleshooting
- 📊 **Performance metrics** - Response times and success/failure rates
- ⚠️ **Error handling** - Clear display of failures and partial successes
- 🎯 **Status indicators** - Visual feedback for processing states

### Web UI Screenshots
The interface automatically detects your configured chatflows from the `.env` file and provides:
- Welcome screen showing active chatflows
- Chat bubbles for each chatflow response
- Error messages for failed chatflows
- Debug panels with JSON response data
- Processing indicators while waiting for responses

Perfect for:
- **Debugging orchestration logic**
- **Testing chatflow configurations**
- **Comparing responses across different chatflows**
- **Monitoring performance and reliability**

## Quick Start

### Installation

```bash
pip install dify-client python-dotenv
```

### Basic Configuration

Create a `.env` file:

```bash
# Base configuration
DIFY_BASE_URL=http://localhost/v1

# Dynamic configuration
DIFY_CHATFLOW_COUNT=3

# Chatflow definitions
DIFY_CHATFLOW_0_API_KEY=app-abc123
DIFY_CHATFLOW_0_NAME=research_agent
DIFY_CHATFLOW_0_DESCRIPTION=Research and information gathering

DIFY_CHATFLOW_1_API_KEY=app-def456
DIFY_CHATFLOW_1_NAME=analysis_agent
DIFY_CHATFLOW_1_DESCRIPTION=Data analysis and processing

DIFY_CHATFLOW_2_API_KEY=app-ghi789
DIFY_CHATFLOW_2_NAME=synthesis_agent
DIFY_CHATFLOW_2_DESCRIPTION=Content synthesis and summarization
```

### Basic Usage

```python
from orchestrator import DifyOrchestrator

# Initialize orchestrator
orchestrator = DifyOrchestrator()

# Get available chatflows
chatflow_names = orchestrator.get_chatflow_names()
print(f"Available chatflows: {chatflow_names}")

# Send to specific chatflow
response = orchestrator.send_to_chatflow(
    chatflow_name="research_agent",
    query="Research the latest AI developments"
)

# Send to multiple chatflows in parallel
parallel_response = orchestrator.send_to_all_chatflows(
    query="What are your capabilities?"
)

# Sequential processing
sequential_response = orchestrator.orchestrate_sequential(
    chatflow_sequence=["research_agent", "analysis_agent", "synthesis_agent"],
    initial_query="Analyze market trends for AI startups"
)
```

## API Reference

### Core Methods

#### `send_to_chatflow(chatflow_name, query, user="default_user", conversation_id=None, inputs=None)`
Send a message to a specific chatflow by name.

**Parameters:**
- `chatflow_name` (str): Name of the target chatflow
- `query` (str): Message to send
- `user` (str): User identifier
- `conversation_id` (str, optional): Conversation context
- `inputs` (dict, optional): Additional workflow inputs

**Returns:** Dictionary with response and metadata

#### `send_to_multiple_chatflows(chatflow_names, query, ...)`
Send the same query to multiple specified chatflows in parallel.

**Parameters:**
- `chatflow_names` (List[str]): List of chatflow names to target
- Other parameters same as `send_to_chatflow`

**Returns:** Dictionary with responses from all chatflows, errors, and status

#### `send_to_all_chatflows(query, ...)`
Send the same query to all configured chatflows.

**Returns:** Same as `send_to_multiple_chatflows`

#### `orchestrate_sequential(chatflow_sequence, initial_query, user="default_user")`
Execute chatflows in sequence, passing output from one to the next.

**Parameters:**
- `chatflow_sequence` (List[str]): Ordered list of chatflow names
- `initial_query` (str): Starting query for the first chatflow
- `user` (str): User identifier

**Returns:** Dictionary with complete execution trace and final result

### Utility Methods

#### `get_chatflow_names()`
Get list of all configured chatflow names.

#### `get_chatflow_config(name)`
Get configuration details for a specific chatflow.

### Legacy Methods (Deprecated)

These methods are still supported but will show deprecation warnings:

- `send_to_chatflow_1(query, ...)` → Use `send_to_chatflow("chatflow_1", query, ...)`
- `send_to_chatflow_2(query, ...)` → Use `send_to_chatflow("chatflow_2", query, ...)`
- `orchestrate_dual_response(query)` → Use `send_to_multiple_chatflows(["chatflow_1", "chatflow_2"], query)`
- `sequential_workflow(query)` → Use `orchestrate_sequential(["chatflow_1", "chatflow_2"], query)`

## Configuration

### Environment Variables

#### Required
- `DIFY_BASE_URL`: Base URL for Dify API
- `DIFY_CHATFLOW_COUNT`: Number of chatflows to configure

#### Per Chatflow (indexed from 0)
- `DIFY_CHATFLOW_N_API_KEY`: API key for chatflow N
- `DIFY_CHATFLOW_N_NAME`: Semantic name for chatflow N
- `DIFY_CHATFLOW_N_DESCRIPTION`: Description for chatflow N

#### Legacy (for backward compatibility)
- `DIFY_CHATFLOW_1_API_KEY`: Legacy chatflow 1 API key
- `DIFY_CHATFLOW_2_API_KEY`: Legacy chatflow 2 API key

### Example Configurations

#### Two Chatflows (Backward Compatible)
```bash
DIFY_BASE_URL=http://localhost/v1
DIFY_CHATFLOW_COUNT=2

DIFY_CHATFLOW_0_API_KEY=app-abc123
DIFY_CHATFLOW_0_NAME=chatflow_1
DIFY_CHATFLOW_0_DESCRIPTION=First chatflow

DIFY_CHATFLOW_1_API_KEY=app-def456
DIFY_CHATFLOW_1_NAME=chatflow_2
DIFY_CHATFLOW_1_DESCRIPTION=Second chatflow

# Legacy support
DIFY_CHATFLOW_1_API_KEY=app-abc123
DIFY_CHATFLOW_2_API_KEY=app-def456
```

#### Five Chatflows (Scaled Configuration)
```bash
DIFY_BASE_URL=http://localhost/v1
DIFY_CHATFLOW_COUNT=5

DIFY_CHATFLOW_0_API_KEY=app-research
DIFY_CHATFLOW_0_NAME=research_agent
DIFY_CHATFLOW_0_DESCRIPTION=Research and data gathering

DIFY_CHATFLOW_1_API_KEY=app-analysis
DIFY_CHATFLOW_1_NAME=analysis_agent
DIFY_CHATFLOW_1_DESCRIPTION=Data analysis and processing

DIFY_CHATFLOW_2_API_KEY=app-creative
DIFY_CHATFLOW_2_NAME=creative_agent
DIFY_CHATFLOW_2_DESCRIPTION=Creative content generation

DIFY_CHATFLOW_3_API_KEY=app-technical
DIFY_CHATFLOW_3_NAME=technical_agent
DIFY_CHATFLOW_3_DESCRIPTION=Technical documentation

DIFY_CHATFLOW_4_API_KEY=app-review
DIFY_CHATFLOW_4_NAME=review_agent
DIFY_CHATFLOW_4_DESCRIPTION=Quality review and validation
```

## Orchestration Patterns

### 1. Parallel Processing
Execute multiple chatflows simultaneously for different perspectives:

```python
# Get opinions from all agents
responses = orchestrator.send_to_all_chatflows(
    "What are the pros and cons of renewable energy?"
)

# Process specific subset
responses = orchestrator.send_to_multiple_chatflows(
    chatflow_names=["research_agent", "analysis_agent"],
    query="Market analysis for electric vehicles"
)
```

### 2. Sequential Processing
Chain chatflows for multi-step workflows:

```python
# Research → Analysis → Synthesis pipeline
result = orchestrator.orchestrate_sequential(
    chatflow_sequence=["research_agent", "analysis_agent", "synthesis_agent"],
    initial_query="Investigate AI impact on healthcare"
)

# Custom workflow
result = orchestrator.orchestrate_sequential(
    chatflow_sequence=["creative_agent", "technical_agent", "review_agent"],
    initial_query="Create a technical blog post about machine learning"
)
```

### 3. Conditional Routing
Route based on content or business logic:

```python
def route_query(orchestrator, query, query_type):
    if query_type == "research":
        return orchestrator.send_to_chatflow("research_agent", query)
    elif query_type == "creative":
        return orchestrator.send_to_chatflow("creative_agent", query)
    else:
        return orchestrator.send_to_all_chatflows(query)
```

### 4. Error-Resilient Processing
Handle partial failures gracefully:

```python
result = orchestrator.send_to_multiple_chatflows(
    chatflow_names=["agent_1", "agent_2", "agent_3"],
    query="Process this request"
)

if result["status"] == "partial_success":
    print(f"Succeeded: {result['success_count']}/{result['total_count']}")
    # Process successful responses
    for name, response in result["responses"].items():
        process_response(name, response)
    
    # Handle errors
    for name, error in result["errors"].items():
        handle_error(name, error)
```

## Testing

### 🚀 New Pytest-Based Testing Framework

The Dify Orchestrator now includes a comprehensive pytest-based testing framework for enhanced development experience:

#### Quick Start
```bash
# Install test dependencies
pip install -e .[test]

# Run quick unit tests
python run_tests.py --quick

# Run all tests with coverage
python run_tests.py --all --coverage --html

# Run specific test categories
python run_tests.py --unit          # Fast unit tests
python run_tests.py --integration   # Integration tests
python run_tests.py --performance   # Performance tests
python run_tests.py --backwards     # Backward compatibility tests
```

#### Test Categories

- **🚀 Unit Tests** (`-m unit`): Fast tests with mocked dependencies
- **🔗 Integration Tests** (`-m integration`): Real API tests requiring environment setup
- **⚡ Performance Tests** (`-m performance`): Performance and scalability benchmarks
- **🔄 Backward Compatibility Tests** (`-m backward_compatibility`): Legacy API compatibility

#### Features
- **Comprehensive Coverage**: 80%+ code coverage with detailed HTML reports
- **Parallel Execution**: Run tests concurrently for faster feedback
- **Mocked Dependencies**: Unit tests run without external API calls
- **Detailed Reporting**: HTML reports, coverage analysis, and failure details
- **CI/CD Ready**: Perfect for automated testing pipelines

#### Advanced Usage
```bash
# Run tests in parallel
python run_tests.py --parallel

# Generate HTML coverage report
python run_tests.py --coverage --html

# Run specific test patterns
pytest -k "test_initialization"

# Run tests from specific file
pytest tests/test_unit_orchestrator.py
```

See [TESTING.md](TESTING.md) for comprehensive testing documentation.

### Legacy Test Script

The original test script is still available for backward compatibility:

```bash
python test_orchestrator.py
```

The legacy test suite covers:
- Dynamic initialization
- Individual chatflow access
- Parallel orchestration
- Sequential orchestration
- Error handling
- Backward compatibility
- Scalability demonstration

## Migration Guide

### From Legacy (v1) to Dynamic (v2)

1. **Update Configuration**: Add `DIFY_CHATFLOW_COUNT` and indexed variables
2. **Update Method Calls**: Replace numbered methods with named methods
3. **Handle Warnings**: Address deprecation warnings in logs
4. **Test Thoroughly**: Run test suite to verify functionality

#### Before (Legacy)
```python
response1 = orchestrator.send_to_chatflow_1("Hello")
response2 = orchestrator.send_to_chatflow_2("Hello")
dual = orchestrator.orchestrate_dual_response("Hello")
```

#### After (Dynamic)
```python
response1 = orchestrator.send_to_chatflow("chatflow_1", "Hello")
response2 = orchestrator.send_to_chatflow("chatflow_2", "Hello")
parallel = orchestrator.send_to_multiple_chatflows(["chatflow_1", "chatflow_2"], "Hello")
```

## Best Practices

1. **Use Semantic Names**: Choose descriptive chatflow names (e.g., "research_agent" vs "chatflow_1")
2. **Error Handling**: Always check response status for parallel operations
3. **Resource Management**: Monitor API usage across multiple chatflows
4. **Configuration Management**: Use environment-specific .env files
5. **Logging**: Enable logging to monitor orchestration performance
6. **Testing**: Test with various chatflow combinations and failure scenarios

## Error Handling

The orchestrator provides robust error handling:

```python
try:
    response = orchestrator.send_to_chatflow("invalid_name", "test")
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Runtime error: {e}")

# For parallel operations
result = orchestrator.send_to_multiple_chatflows(
    chatflow_names=["valid_agent", "invalid_agent"],
    query="test"
)

if result["status"] == "partial_success":
    # Handle mixed success/failure scenario
    successful_responses = result["responses"]
    errors = result["errors"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure backward compatibility
5. Update documentation
6. Submit a pull request

## License

[Include your license information here]

## Changelog

### v2.0.0
- ✨ Added support for arbitrary numbers of chatflows
- ✨ Added dynamic configuration system
- ✨ Added parallel orchestration methods
- ✨ Added enhanced sequential orchestration
- ✨ Added robust error handling
- ✨ Added named chatflow support
- 🔄 Maintained backward compatibility
- 📚 Added comprehensive documentation
- 🧪 Added enhanced test suite

### v1.0.0
- Initial release with 2-chatflow support
