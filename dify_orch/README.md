# Dify Orchestrator

A basic Dify client orchestrator that sends POST messages to multiple Dify chatflows.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   # or if using uv:
   uv pip install .
   ```

2. **Configure API keys:**
   Edit the `.env` file and add your Dify API keys:
   ```env
   DIFY_BASE_URL=http://localhost/v1
   DIFY_CHATFLOW_1_API_KEY=app-your-chatflow-1-api-key-here
   DIFY_CHATFLOW_2_API_KEY=app-your-chatflow-2-api-key-here
   ```

## Usage

### Basic Example
```python
from orchestrator import DifyOrchestrator

# Initialize the orchestrator
orch = DifyOrchestrator()

# Send message to chatflow 1
response1 = orch.send_to_chatflow_1("Hello, how are you?")

# Send message to chatflow 2
response2 = orch.send_to_chatflow_2("What's the weather like?")

# Send to both chatflows simultaneously
dual_response = orch.orchestrate_dual_response("Compare AI capabilities")

# Sequential workflow (output of chatflow 1 → input to chatflow 2)
sequential_result = orch.sequential_workflow("Generate a story")
```

### Run Tests
```bash
python test_orchestrator.py
```

## Features

- **Individual Chatflow Communication**: Send messages to specific chatflows
- **Dual Response Mode**: Send the same query to both chatflows and compare responses
- **Sequential Workflow**: Chain chatflows where the output of one becomes input to another
- **Environment Configuration**: Load API keys and settings from `.env` file
- **Error Handling**: Comprehensive logging and error management
- **Type Hints**: Full type annotation support

## API Reference

### DifyOrchestrator Class

#### Methods

- `send_to_chatflow_1(query, user, conversation_id, inputs)`: Send message to first chatflow
- `send_to_chatflow_2(query, user, conversation_id, inputs)`: Send message to second chatflow  
- `orchestrate_dual_response(query)`: Send query to both chatflows
- `sequential_workflow(initial_query)`: Chain chatflow responses

#### Parameters

- `query` (str): The message to send
- `user` (str): User identifier (default: "default_user")
- `conversation_id` (str, optional): Conversation ID for context
- `inputs` (dict, optional): Additional workflow inputs

## Requirements

- Python >= 3.8
- dify-client >= 0.1.0
- python-dotenv >= 1.0.0
- requests >= 2.25.0