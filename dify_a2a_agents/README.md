# Dify A2A Multi-Agent System

A complete implementation of a multi-agent system using Dify workflows integrated with Google's Agent2Agent (A2A) protocol.

## 🎯 Project Overview

This system implements **Phase 1-4** of the specification, providing a fully functional multi-agent architecture where:

- **Orchestrator Agent** routes queries and synthesizes responses
- **Research Agent** handles information gathering and web research  
- **Analysis Agent** processes data and performs analytical tasks
- **Code Agent** handles code generation and technical tasks

All agents communicate via the A2A protocol while leveraging Dify workflows for their core intelligence.

## 🏗️ Architecture

```
┌─────────────────┐    A2A Protocol    ┌─────────────────┐
│  Orchestrator   │◄──────────────────►│  Research Agent │
│   (Port 9001)   │                    │   (Port 9002)   │
│   Dify Flow     │                    │   Dify Flow     │
└─────────────────┘                    └─────────────────┘
         │                                       
         │ A2A Protocol                         
         ▼                                       
┌─────────────────┐    A2A Protocol    ┌─────────────────┐
│  Analysis Agent │◄──────────────────►│   Code Agent    │
│   (Port 9003)   │                    │   (Port 9004)   │
│   Dify Flow     │                    │   Dify Flow     │
└─────────────────┘                    └─────────────────┘
```

### Agent Capabilities

| Agent | Skills | Port | Purpose |
|-------|--------|------|---------|
| **Orchestrator** | Query routing, Response synthesis | 9001 | Main entry point and coordinator |
| **Research** | Web search, Fact checking | 9002 | Information gathering and verification |
| **Analysis** | Data analysis, Summarization | 9003 | Data processing and insights |
| **Code** | Code generation, Code review | 9004 | Programming and technical tasks |

## 🚀 Quick Start

### 1. Prerequisites
- **Dify** running locally (http://localhost/)
- **Python 3.8+** 
- **A2A SDK** installed

### 2. Installation
```bash
cd dify_a2a_agents
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Dify configuration
```

### 3. Run the System
```bash
# Start all agents
python start_agents.py

# Test the system (in another terminal)
python test_client.py

# Or run interactively
python test_client.py --interactive
```

## 📁 Project Structure

```
dify_a2a_agents/
├── README.md              # This file
├── SETUP.md               # Detailed setup guide
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── start_agents.py       # Agent launcher
├── test_client.py        # Test client
│
├── config/               # Configuration
│   ├── __init__.py
│   └── agents.py         # Agent definitions
│
├── shared/               # Common utilities
│   ├── __init__.py
│   └── dify_client.py    # Dify API integration
│
├── orchestrator/         # Main routing agent
│   ├── __init__.py
│   ├── agent_executor.py # Core logic
│   └── server.py         # A2A server
│
├── research_agent/       # Information gathering
│   ├── __init__.py
│   ├── agent_executor.py
│   └── server.py
│
├── analysis_agent/       # Data analysis
│   ├── __init__.py
│   ├── agent_executor.py
│   └── server.py
│
└── code_agent/          # Code generation
    ├── __init__.py
    ├── agent_executor.py
    └── server.py
```

## 🔧 Key Features

### A2A Protocol Integration
- ✅ **Standardized Communication**: JSON-RPC 2.0 over HTTP
- ✅ **Agent Discovery**: Agent Cards with capabilities and skills
- ✅ **Streaming Support**: Real-time response streaming
- ✅ **Error Handling**: Comprehensive error management

### Dify Workflow Integration
- ✅ **Workflow Execution**: Direct API calls to Dify workflows
- ✅ **Context Passing**: Rich context and parameters
- ✅ **Response Processing**: Structured output handling
- ✅ **Async Operations**: Non-blocking workflow execution

### Multi-Agent Coordination
- ✅ **Intelligent Routing**: LLM-powered query analysis
- ✅ **Parallel Processing**: Concurrent agent consultation
- ✅ **Response Synthesis**: Coherent multi-source responses
- ✅ **State Management**: Task lifecycle tracking

## 🧪 Testing

The system includes comprehensive testing capabilities:

### Automated Test Suite
```bash
python test_client.py
```
Runs predefined test scenarios covering:
- Research queries
- Analysis requests  
- Code generation
- Multi-agent collaboration
- Summarization tasks

### Interactive Testing
```bash
python test_client.py --interactive
```
Provides a conversational interface for manual testing.

### Individual Agent Testing
```bash
# Test specific agents
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

## 📋 Setup Requirements

### Dify Configuration
You'll need to create 4 workflows in Dify:

1. **Orchestrator Workflow**: Query routing and synthesis
2. **Research Workflow**: Information gathering  
3. **Analysis Workflow**: Data analysis and summarization
4. **Code Workflow**: Code generation and review

See [SETUP.md](SETUP.md) for detailed workflow configuration.

### Environment Variables
```bash
# Core Dify settings
DIFY_BASE_URL=http://localhost/v1
DIFY_API_KEY=your_api_key

# Workflow IDs (from Dify dashboard)
ORCHESTRATOR_WORKFLOW_ID=wf-xxxxxxxxx
RESEARCH_WORKFLOW_ID=wf-yyyyyyyyy  
ANALYSIS_WORKFLOW_ID=wf-zzzzzzzzz
CODE_WORKFLOW_ID=wf-aaaaaaaaa
```

## 🔄 How It Works

### Request Flow
1. **User Query** → Orchestrator Agent (port 9001)
2. **Query Analysis** → Determine required specialist agents
3. **Agent Consultation** → Parallel A2A calls to specialists
4. **Response Synthesis** → Combine results into coherent answer
5. **Final Response** → Delivered to user

### Example Interaction
```
User: "Research AI trends, analyze the data, and write code to visualize it"

🤔 Orchestrator: Analyzing request...
📋 Routing to: research, analysis, code

🔍 Research Agent: Gathering AI trend information...
📊 Analysis Agent: Processing trend data...  
💻 Code Agent: Generating visualization code...

📝 Final Response: [Synthesized comprehensive answer]
```

## 🛠️ Customization

### Adding New Agents
1. Create new agent directory
2. Implement `AgentExecutor` class
3. Create A2A server
4. Add to `config/agents.py`
5. Update launcher script

### Modifying Agent Behavior
- **Agent Logic**: Edit `agent_executor.py` files
- **Dify Workflows**: Update workflow logic in Dify
- **Routing Logic**: Modify orchestrator routing rules

### Scaling Considerations
- Use process managers (PM2, systemd) for production
- Implement load balancing for multiple instances
- Add monitoring and health checks
- Consider containerization with Docker

## 🐛 Troubleshooting

### Common Issues
- **Import Errors**: Ensure virtual environment is activated
- **Dify Connection**: Verify Dify is running and API keys are correct
- **Agent Communication**: Check all agents are running on expected ports
- **Workflow Issues**: Confirm workflow IDs match your Dify setup

### Debug Mode
```bash
export A2A_LOG_LEVEL=debug
python start_agents.py
```

## 📚 Documentation

- **[SETUP.md](SETUP.md)**: Complete setup guide
- **[A2A Documentation](https://google.github.io/A2A/)**: Official A2A protocol docs
- **[Dify Documentation](https://docs.dify.ai)**: Dify platform documentation

## 🎉 Implementation Status

✅ **Phase 1**: Foundation Setup - Complete  
✅ **Phase 2**: Agent Development - Complete  
✅ **Phase 3**: A2A Integration - Complete  
✅ **Phase 4**: System Integration - Complete

The system is now fully functional and ready for testing and customization!

## 📝 Next Steps

1. **Setup Dify Workflows** following the SETUP.md guide
2. **Configure Environment** with your API keys and workflow IDs  
3. **Test the System** using the provided test scripts
4. **Customize Agents** for your specific use cases
5. **Scale and Deploy** for production environments

Happy multi-agent building! 🤖✨
