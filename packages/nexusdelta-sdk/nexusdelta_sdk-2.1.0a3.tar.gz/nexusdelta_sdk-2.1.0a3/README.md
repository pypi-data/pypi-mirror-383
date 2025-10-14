#  CensaiOS SDK - The AI Agent Operating System

[![PyPI version](https://badge.fury.io/py/nexusdelta-sdk.svg)](https://badge.fury.io/py/nexusdelta-sdk)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**The AI Agent Operating System SDK** - Build, deploy, and orchestrate AI agents with multi-model support.

##  Features

- **Multi-Model AI Orchestration**: Seamlessly integrate Grok, Gemini, and Jules models
- **Agent Marketplace**: Register and discover AI agents in a decentralized ecosystem
- **Cloud-Native Execution**: Isolated tool execution via Cloud Run instances
- **Firebase Authentication**: Secure user management and agent ownership
- **Auto-Discovery**: Automatically finds API Gateway in development and production
- **Type Safety**: Full Python type hints and Pydantic validation

##  Installation

`ash
pip install nexusdelta-sdk
`

### Optional Dependencies

`ash
# For AI model integrations
pip install nexusdelta-sdk[ai]

# For blockchain/crypto features
pip install nexusdelta-sdk[crypto]

# For full development stack
pip install nexusdelta-sdk[full]

# For development and testing
pip install nexusdelta-sdk[dev]
`

##  Quick Start

`python
from nexusdelta_sdk import NexusDeltaSDK

# Initialize with your Firebase token
sdk = NexusDeltaSDK(api_key="your_firebase_token_here")

# Check connection
health = sdk.health_check()
print(f"Connected to CensaiOS: {health}")

# Register an agent
agent_card = {
    "name": "DataAnalyzer",
    "purpose": "Analyze datasets and generate insights",
    "category": "data_science",
    "model": "gpt-4",
    "tools": ["data_analysis", "visualization"]
}

result = sdk.register_agent(agent_card)
print(f"Agent registered: {result['agent_id']}")

# Search for agents
agents = sdk.search_agents("data processing")
for agent in agents:
    print(f"Found agent: {agent['name']}")

# Execute a tool
payload = {"data": [1, 2, 3, 4, 5], "operation": "mean"}
result = sdk.execute_tool(agent_id, "calculate", payload)
print(f"Result: {result}")
`

##  Architecture

CensaiOS uses a microservices architecture with:

- **API Gateway**: Routes requests to appropriate services
- **Agent Registry**: Manages agent metadata and discovery
- **Execution Engine**: Runs tools in isolated Cloud Run instances
- **Authentication Service**: Firebase-based user management

##  Documentation

- [API Reference](docs/api.md)
- [Agent Development Guide](docs/agents.md)
- [Deployment Guide](docs/deployment.md)
- [Security Best Practices](docs/security.md)

##  Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Support

- **Email**: censai.systems@gmail.com
- **Issues**: [GitHub Issues](https://github.com/oogalieboogalie/Nexus-Delta-SDK/issues)
- **Documentation**: [GitHub Wiki](https://github.com/oogalieboogalie/Nexus-Delta-SDK/wiki)

##  Security

CensaiOS takes security seriously. All communications are encrypted, and agents run in isolated environments. See our [Security Guide](docs/security.md) for details.

---

**Built with  by the CensaiOS Team**
