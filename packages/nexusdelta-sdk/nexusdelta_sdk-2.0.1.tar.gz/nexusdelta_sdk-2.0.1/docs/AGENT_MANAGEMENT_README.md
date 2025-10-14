# Nexus Delta Agent Management System

## Overview

Nexus Delta supports **unlimited agents** through a flexible containerization system. Each agent runs in its own isolated Docker container, making it easy to scale from 1 to 100+ agents.

## Current Architecture

### How Agents Are Housed

1. **Registry Storage**: Agent metadata stored in Firebase Firestore
2. **Container Isolation**: Each agent runs in separate Docker container
3. **API Endpoints**: Agents expose REST APIs for tool execution
4. **Service Discovery**: Registry service manages agent discovery

### Scaling Strategy

```
50 Agents Example:
├── Agent Registry (Firebase) - Stores all agent metadata
├── Docker Host - Runs containers
│   ├── agent-001 (port 8081) - Data Processor
│   ├── agent-002 (port 8082) - Text Analyzer
│   ├── agent-003 (port 8083) - Image Processor
│   ├── ... (ports 8084-8130)
│   └── agent-050 (port 8130) - Custom Agent
└── Load Balancer - Routes requests to appropriate agents
```

## Quick Start - Create Your First Agent

### 1. Create Agent from Template
```bash
python agent_manager.py create --name "MyAgent" --port 8081 --capabilities data_processing analytics
```

### 2. Customize Agent Code
Edit `agents/myagent/myagent_agent.py` to implement your logic.

### 3. Build and Start
```bash
# Build base image
docker build -f Dockerfile.agent -t nexus-delta-agent:latest .

# Start your agent
python agent_manager.py start --name "MyAgent"
```

### 4. Test Agent
```bash
curl http://localhost:8081/health
curl -X POST http://localhost:8081/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "process_data", "parameters": {"data": [1,2,3,4,5]}}'
```

## Managing Multiple Agents

### Create Multiple Agents
```bash
# Create 5 agents at once
python agent_manager.py create --name "DataAgent" --port 8081 --capabilities data analytics
python agent_manager.py create --name "TextAgent" --port 8082 --capabilities nlp text
python agent_manager.py create --name "ImageAgent" --port 8083 --capabilities vision ocr
python agent_manager.py create --name "CodeAgent" --port 8084 --capabilities programming
python agent_manager.py create --name "MathAgent" --port 8085 --capabilities math calculus
```

### Start All Agents
```bash
python agent_manager.py start-all
```

### List Running Agents
```bash
python agent_manager.py list
```

### Stop Agents
```bash
# Stop specific agent
python agent_manager.py stop --name "DataAgent"

# Stop all agents
python agent_manager.py stop-all
```

## Docker Compose for Production

For production deployments with 50+ agents, use Docker Compose:

```yaml
# docker-compose-agents.yml
version: '3.8'
services:
  agent-001:
    build: ./Dockerfile.agent
    ports: ["8081:8081"]
    environment:
      - AGENT_NAME=DataProcessor
      - PORT=8081
  agent-002:
    # ... more agents
```

```bash
# Start all agents
docker-compose -f docker-compose-agents.yml up -d

# Scale specific agent
docker-compose -f docker-compose-agents.yml up -d --scale agent-001=3
```

## Agent Development Template

Each agent follows this structure:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="MyAgent")

class ToolRequest(BaseModel):
    tool_name: str
    parameters: dict

@app.post("/execute")
async def execute_tool(request: ToolRequest):
    if request.tool_name == "my_tool":
        # Your logic here
        return {"result": "processed"}
    else:
        return {"error": "tool not found"}
```

## Performance Considerations

### For 50+ Agents:

1. **Resource Allocation**: Each container needs ~200-500MB RAM
2. **Port Management**: Use port ranges (8081-8180 for 100 agents)
3. **Load Balancing**: Use nginx or traefik for request routing
4. **Monitoring**: Implement health checks and metrics
5. **Auto-scaling**: Scale agents based on demand

### Resource Requirements:
- **50 agents**: ~10-25GB RAM, 50-100 CPU cores
- **100 agents**: ~20-50GB RAM, 100-200 CPU cores

## Registration with Marketplace

Once agents are running, register them with the marketplace:

```python
from nexusdelta_sdk import NexusDeltaSDK

sdk = NexusDeltaSDK(api_key="your_token")

# Register each agent
for agent in agents:
    agent_card = {
        "name": agent["name"],
        "purpose": agent["description"],
        "category": "utility",
        "model": "gpt-4",
        "tools": agent["tools"],
        "api_endpoint": f"http://your-host:{agent['port']}"
    }
    sdk.register_agent(agent_card)
```

## Demo

Run the complete demo:

```bash
python demo_multiple_agents.py
```

This creates 5 agents, builds Docker images, starts containers, and tests health checks.

## Troubleshooting

### Common Issues:

1. **Port conflicts**: Check `netstat -an | find "808"` on Windows
2. **Docker issues**: Run `docker system prune` to clean up
3. **Memory limits**: Increase Docker memory allocation
4. **Health check failures**: Check agent logs with `docker logs <container>`

### Monitoring Commands:
```bash
# List all agent containers
docker ps | grep nexus-agent

# Check agent logs
docker logs nexus-agent-data-processor

# Monitor resource usage
docker stats
```

## Next Steps

1. **Implement load balancing** for high-traffic agents
2. **Add auto-scaling** based on request volume
3. **Implement agent versioning** and updates
4. **Add monitoring dashboard** for all agents
5. **Create agent marketplace UI** for easy management

This system scales naturally - adding the 51st agent is just as easy as adding the 1st!