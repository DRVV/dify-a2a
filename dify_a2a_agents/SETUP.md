# Dify A2A Multi-Agent System Setup Guide

This guide walks you through setting up and running the Dify A2A Multi-Agent System.

## Prerequisites

1. **Dify Installation**: Ensure Dify is running locally
   ```bash
   cd dify/docker
   docker compose up -d
   ```
   Access Dify at: http://localhost/

2. **Python Environment**: Python 3.8+
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

## Installation Steps

### 1. Install Dependencies
```bash
cd dify_a2a_agents
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

**Required Configuration:**
- `DIFY_API_KEY`: Your Dify API key
- `DIFY_BASE_URL`: Dify API URL (default: http://localhost/v1)
- Workflow IDs for each agent (see Dify Workflow Setup below)

### 3. Set Up Dify Workflows

For each agent, create a Dify workflow:

#### Orchestrator Workflow
**Purpose**: Route queries and synthesize responses
**Input Variables:**
- `user_input` (text): User's query
- `available_agents` (array): List of available agents
- `agent_capabilities` (object): Agent capabilities mapping

**Workflow Logic:**
1. **LLM Node**: Analyze user input and determine which agents to involve
2. **Code Node**: Parse routing decisions
3. **Output**: JSON with selected agents and reasoning

#### Research Agent Workflow
**Purpose**: Information gathering and research
**Input Variables:**
- `user_input` (text): Research query
- `task_type` (text): Type of research task
- `search_focus` (text): Focus of the search

**Workflow Logic:**
1. **Web Search Node**: Search for relevant information
2. **LLM Node**: Process and structure the findings
3. **Output**: Structured research report

#### Analysis Agent Workflow
**Purpose**: Data analysis and summarization
**Input Variables:**
- `user_input` (text): Data to analyze
- `task_type` (text): Analysis type
- `analysis_focus` (text): Focus of analysis

**Workflow Logic:**
1. **LLM Node**: Analyze the input data
2. **Code Node**: Extract key insights
3. **Output**: Analysis with insights and patterns

#### Code Agent Workflow
**Purpose**: Code generation and review
**Input Variables:**
- `user_input` (text): Code request or code to review
- `task_type` (text): Generation or review
- `code_focus` (text): Focus of the task

**Workflow Logic:**
1. **LLM Node**: Generate or review code
2. **Code Node**: Format and validate output
3. **Output**: Code with explanations

### 4. Update Configuration

After creating workflows in Dify, update your `.env` file:
```bash
# Get workflow IDs from Dify dashboard URLs
ORCHESTRATOR_WORKFLOW_ID=wf-xxxxxxxxx
RESEARCH_WORKFLOW_ID=wf-yyyyyyyyy
ANALYSIS_WORKFLOW_ID=wf-zzzzzzzzz
CODE_WORKFLOW_ID=wf-aaaaaaaaa

# Get API keys from Dify app settings
DIFY_API_KEY=app-your-api-key-here
```

## Running the System

### 1. Start All Agents
```bash
python start_agents.py
```

This will start:
- Research Agent on port 9002
- Analysis Agent on port 9003
- Code Agent on port 9004
- Orchestrator Agent on port 9001

### 2. Test the System

**Automated Tests:**
```bash
python test_client.py
```

**Interactive Mode:**
```bash
python test_client.py --interactive
```

**Manual A2A Testing:**
```bash
# Test individual agent
curl -X POST http://localhost:9002/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "CreateTask",
    "params": {
      "inputs": [{"text": "Research AI trends"}],
      "outputMode": "text"
    },
    "id": "test-1"
  }'
```

## Agent URLs and Capabilities

| Agent | URL | Primary Skills |
|-------|-----|----------------|
| Orchestrator | http://localhost:9001/ | Query routing, response synthesis |
| Research | http://localhost:9002/ | Web research, fact checking |
| Analysis | http://localhost:9003/ | Data analysis, summarization |
| Code | http://localhost:9004/ | Code generation, code review |

## Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Ensure you're in the correct directory and virtual environment
cd dify_a2a_agents
source venv/bin/activate
pip install -r requirements.txt
```

**2. Dify Connection Issues**
- Verify Dify is running: http://localhost/
- Check API key is correct
- Ensure workflow IDs match your Dify workflows

**3. Agent Communication Errors**
- Confirm all agents are running on correct ports
- Check firewall settings
- Verify A2A protocol communication

**4. Missing Workflow IDs**
- Create workflows in Dify first
- Copy workflow IDs from browser URL
- Update .env file with correct IDs

### Debug Mode
Set environment variables for more detailed logging:
```bash
export PYTHONPATH=$PWD
export A2A_LOG_LEVEL=debug
python start_agents.py
```

### Individual Agent Testing
Start agents individually for debugging:
```bash
# Start research agent only
cd research_agent
python server.py

# In another terminal, test it
python ../test_client.py
```

## Extending the System

### Adding New Agents
1. Create new agent directory following the pattern
2. Implement `AgentExecutor` class
3. Create A2A server
4. Add configuration to `config/agents.py`
5. Update `start_agents.py`

### Customizing Agent Behavior
- Modify agent executors in each agent's `agent_executor.py`
- Update Dify workflows for different processing logic
- Adjust routing logic in orchestrator

### Scaling Considerations
- Use process managers like PM2 or systemd for production
- Implement load balancing for multiple agent instances
- Add monitoring and health checks
- Consider container deployment with Docker

## Next Steps

1. **Create Dify Workflows**: Set up the four required workflows in Dify
2. **Configure API Keys**: Get your Dify API keys and workflow IDs
3. **Test Individual Agents**: Verify each agent works independently
4. **Test Multi-Agent Coordination**: Run full system tests
5. **Customize and Extend**: Modify agents for your specific use cases

For more details, see the main README.md file.
