# Nexus Delta SDK - Enhanced with Multi-Model AI Orchestration
# Version: 2.1.0
# Compatible with: Microservices Architecture (API Gateway)
# Includes: Grok, Gemini, and Jules integration

import requests
import json
from typing import List, Dict, Any, Optional
import os
import logging
import secrets

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base URL is now dynamically determined
def get_base_url():
    """
    Automatically discovers the Nexus Delta API Gateway.
    Priority:
    1. Environment variable NEXUS_DELTA_URL
    2. .port or nexusdelta.port file
    3. Auto-discovery on common ports
    4. Production URL (Firebase Hosting)
    """
    # Check environment variable first
    if os.getenv("NEXUS_DELTA_URL"):
        return os.getenv("NEXUS_DELTA_URL")

    # Check port files
    port_files = [".port", "nexusdelta.port"]
    for port_file in port_files:
        if os.path.exists(port_file):
            with open(port_file, "r") as f:
                port = f.read().strip()
                return f"http://127.0.0.1:{port}"

    # Try common development ports (API Gateway is on 8080)
    # Check 8080 first (default API Gateway port)
    for port in [8080, 8000, 8001, 3000]:
        try:
            response = requests.get(f"http://127.0.0.1:{port}/health", timeout=0.5)
            if response.status_code == 200:
                logger.info(f"✅ Discovered API Gateway at http://127.0.0.1:{port}")
                return f"http://127.0.0.1:{port}"
        except:
            continue

    # Production fallback
    logger.warning("⚠️ Local API Gateway not found, using production URL")
    return "https://nexus-delta.web.app"

class NexusDeltaSDK:
    """
    Official Python SDK for Nexus Delta AI Agent Marketplace

    Features:
    - Agent registration and discovery
    - Tool execution via isolated Cloud Run instances
    - Firebase Authentication integration
    - Automatic rate limiting handling
    - Production and development environment support

    Example:
        sdk = NexusDeltaSDK(api_key="your_firebase_token")
        agents = sdk.search_agents("data processing")
        result = sdk.execute_tool(agent_id, tool_name, payload)
    """

    def __init__(self, api_key: str, base_url: Optional[str] = None, user_id: Optional[str] = None):
        """
        Initialize the SDK connection.

        Args:
            api_key: Firebase ID token (get from Firebase Auth)
            base_url: Override auto-discovered API Gateway URL
            user_id: User ID for agent registration (optional, defaults to 'test-user')
        """
        self.base_url = base_url or get_base_url()
        self.api_version = "v1"
        self.user_id = user_id or "test-user"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "NexusDeltaSDK/2.1.0",
            "X-User-ID": self.user_id
        }
        logger.info(f"🚀 NexusDeltaSDK initialized - API Gateway: {self.base_url}")

    def _get_url(self, path: str) -> str:
        """Constructs the full API URL with proper versioning."""
        # Remove leading slash if present
        path = path.lstrip("/")
        return f"{self.base_url}/api/{self.api_version}/{path}"

    def register_agent(self, agent_card: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register an agent with the marketplace.

        Args:
            agent_card: Complete agent card with name, purpose, tools, etc.

        Returns:
            dict: Registration response with agent_id and status

        Example:
            agent_card = {
                "name": "DataProcessor",
                "purpose": "Process and analyze data",
                "category": "utility",
                "model": "gpt-4",
                "tools": [{"id": "process", "name": "Process Data"}]
            }
            response = sdk.register_agent(agent_card)
            agent_id = response["agent_id"]
        """
        url = self._get_url("agents/register")
        logger.info(f"📝 Registering agent '{agent_card.get('name', 'Unknown')}'")
        logger.debug(f"POST {url}")

        # Generate hash_id if not provided
        if 'hash_id' not in agent_card:
            agent_card['hash_id'] = f"agent_{secrets.token_hex(8)}"

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=agent_card,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"✅ Agent registered successfully - ID: {data.get('agent_id', 'Unknown')}")
            return data
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ Registration failed: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"❌ Registration error: {e}")
            raise

    def search_agents(self, query: str, category: Optional[str] = None, vetted_only: bool = True) -> List[Dict[str, Any]]:
        """
        Search for agents in the marketplace using natural language.

        Args:
            query: Natural language search query (e.g., "data processing", "all")
            category: Filter by category (utility, creative, analysis, etc.)
            vetted_only: Only return vetted agents (default: True)

        Returns:
            list: List of matching agents with their details

        Example:
            agents = sdk.search_agents("data processing", category="utility")
            for agent in agents:
                print(f"{agent['name']}: {agent['purpose']}")
        """
        url = self._get_url("registry/search")
        logger.info(f"🔍 Searching for agents: '{query}'")
        logger.debug(f"GET {url}")

        params = {"query": query}
        if category:
            params["category"] = category
        if vetted_only:
            params["vetted_only"] = "true"

        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            agents = data.get('agents', data.get('matching_tools', []))
            logger.info(f"✅ Found {len(agents)} agents")
            return agents
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ Search failed: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"❌ Search error: {e}")
            raise

    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific agent.

        Args:
            agent_id: The unique agent hash ID

        Returns:
            dict: Complete agent details including tools, status, metadata
        """
        url = self._get_url(f"agents/{agent_id}")
        logger.info(f"📋 Fetching agent details: {agent_id}")

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ Failed to get agent: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"❌ Error fetching agent: {e}")
            raise

    def execute_tool(self, agent_id: str, tool_name: str, payload: Dict[str, Any]) -> Any:
        """
        Execute a tool on a specific agent.

        Args:
            agent_id: The agent's hash ID that provides the tool
            tool_name: Name of the tool to execute
            payload: Input data for the tool

        Returns:
            Tool execution result

        Example:
            result = sdk.execute_tool(
                agent_id="agent_abc123",
                tool_name="process_data",
                payload={"data": [1, 2, 3, 4, 5]}
            )
        """
        url = self._get_url("execute")
        logger.info(f"⚡ Executing tool '{tool_name}' on agent '{agent_id}'")
        logger.debug(f"POST {url}")

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json={
                    "agent_id": agent_id,
                    "tool_name": tool_name,
                    "payload": payload
                },
                timeout=60  # Tools can take time to execute
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"✅ Tool execution successful")
            return data.get('result', data)
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ Execution failed: {e.response.status_code} - {e.response.text}")
            raise
        except requests.exceptions.Timeout:
            logger.error(f"❌ Execution timeout (>60s)")
            raise
        except Exception as e:
            logger.error(f"❌ Execution error: {e}")
            raise

    def list_tools(self, agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available tools in the marketplace.

        Args:
            agent_id: Optional - filter tools by specific agent

        Returns:
            list: Available tools with metadata
        """
        url = self._get_url("tools")
        logger.info(f"📦 Listing tools" + (f" for agent {agent_id}" if agent_id else ""))

        params = {"agent_id": agent_id} if agent_id else {}

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            tools = data.get('tools', [])
            logger.info(f"✅ Found {len(tools)} tools")
            return tools
        except Exception as e:
            logger.error(f"❌ Error listing tools: {e}")
            raise

    def health_check(self) -> Dict[str, Any]:
        """
        Check the health status of the Nexus Delta API Gateway.

        Returns:
            dict: Health status of gateway and all backend services

        Example:
            health = sdk.health_check()
            if health['gateway'] == 'healthy':
                print("All systems operational")
        """
        url = f"{self.base_url}/health"
        logger.info(f"🏥 Checking API Gateway health")

        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()

            # Log service statuses
            if 'services' in data:
                for service, status in data['services'].items():
                    if status.get('status') == 'healthy':
                        logger.debug(f"  ✅ {service}: healthy")
                    else:
                        logger.warning(f"  ⚠️ {service}: {status.get('status', 'unknown')}")

            return data
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            raise

    def get_all_agents(self) -> List[Dict[str, Any]]:
        """
        Get all registered agents from the marketplace.
        Convenience method that searches for "all" agents.

        Returns:
            list: All registered agents
        """
        return self.search_agents("all", vetted_only=False)

    # ===== MULTI-MODEL AI EXTENSIONS =====

    def create_multi_model_agent(self, name: str, purpose: str, models: List[str] = None) -> Dict[str, Any]:
        """
        Create an agent that can use multiple AI models (Grok, Gemini, Jules).

        Args:
            name: Agent name
            purpose: Agent purpose description
            models: List of models to support (default: ["grok", "gemini"])

        Returns:
            dict: Agent registration response

        Example:
            agent = sdk.create_multi_model_agent(
                "CodeAssistant",
                "AI coding assistant with multiple models",
                ["grok", "gemini", "jules"]
            )
        """
        if models is None:
            models = ["grok", "gemini"]

        agent_card = {
            "name": name,
            "purpose": purpose,
            "category": "multi_model",
            "model": "multi_model_orchestrator",
            "version": "1.0.0",
            "description": f"Multi-model agent supporting: {', '.join(models)}",
            "capabilities": ["multi_model_ai", "intelligent_routing"],
            "tools": [
                {
                    "id": "orchestrate_query",
                    "name": "Orchestrate Query",
                    "description": "Automatically route queries to the best AI model"
                }
            ],
            "metadata": {
                "supported_models": models,
                "routing_intelligence": True,
                "orchestration_capable": True
            }
        }

        return self.register_agent(agent_card)

    def orchestrate_ai_query(self, prompt: str, context: str = "", model: str = "auto",
                           max_tokens: int = 1000, temperature: float = 0.7) -> Dict[str, Any]:
        """
        Execute an AI query using intelligent model routing.

        Args:
            prompt: The query to process
            context: Additional context for routing decisions
            model: Specific model to use ("auto", "grok", "gemini", "jules")
            max_tokens: Maximum response tokens
            temperature: Creativity level (0.0-1.0)

        Returns:
            dict: Query result with model used and response

        Example:
            result = sdk.orchestrate_ai_query(
                "Write a Python function to calculate fibonacci",
                context="code generation task"
            )
            print(f"Model: {result['model']}, Response: {result['response']}")
        """
        # Initialize orchestrator if needed
        if not hasattr(self, '_orchestrator'):
            self._orchestrator = MultiModelOrchestrator()

        try:
            if model == "auto":
                return self._orchestrator.orchestrate_query(
                    prompt, context, max_tokens=max_tokens, temperature=temperature
                )
            elif model == "grok":
                return self._orchestrator.query_grok(
                    prompt, max_tokens=max_tokens, temperature=temperature
                )
            elif model == "gemini":
                return self._orchestrator.query_gemini(
                    prompt, max_tokens=max_tokens, temperature=temperature
                )
            elif model == "jules":
                return self._orchestrator.query_jules(prompt, context)
            else:
                raise ValueError(f"Unknown model: {model}")
        except Exception as e:
            return {
                "error": f"Failed to query {model}: {str(e)}",
                "model": model,
                "timestamp": json.dumps({"error": "import datetime failed"}, default=str)
            }

    def get_model_capabilities(self) -> Dict[str, List[str]]:
        """
        Get capabilities of available AI models.

        Returns:
            dict: Model capabilities mapping
        """
        return {
            "grok": ["reasoning", "analysis", "general_ai"],
            "gemini": ["code_generation", "text_analysis", "creative_writing"],
            "jules": ["content_generation", "github_context", "project_planning"]
        }

    # Backwards compatibility aliases
    def find_service(self, query: str) -> List[Dict[str, Any]]:
        """Legacy alias for search_agents"""
        logger.warning("⚠️ find_service() is deprecated, use search_agents() instead")
        return self.search_agents(query)

    def get_registered_agents(self) -> List[Dict[str, Any]]:
        """Legacy alias for get_all_agents"""
        logger.warning("⚠️ get_registered_agents() is deprecated, use get_all_agents() instead")
        return self.get_all_agents()


# ===== MULTI-MODEL ORCHESTRATOR CLASS =====

class MultiModelOrchestrator:
    """Multi-model AI orchestrator supporting Grok, Gemini, and Jules"""

    def __init__(self, grok_key: Optional[str] = None, gemini_key: Optional[str] = None,
                 jules_key: Optional[str] = None):
        self.grok_key = grok_key or os.getenv("XAI_API_KEY")
        self.gemini_key = gemini_key or os.getenv("GEMINI_API_KEY")
        self.jules_key = jules_key or os.getenv("JULES_API_KEY")

        # Model capabilities mapping
        self.model_capabilities = {
            "grok": ["reasoning", "analysis", "general_ai"],
            "gemini": ["code_generation", "text_analysis", "creative_writing"],
            "jules": ["content_generation", "github_context", "project_planning"]
        }

    def route_task_to_model(self, task: str, context: str = "") -> str:
        """Intelligently route tasks to the best AI model"""
        task_lower = task.lower()
        context_lower = context.lower()

        # Code generation -> Gemini
        if any(keyword in task_lower for keyword in ["code", "function", "script", "program"]):
            return "gemini"

        # Reasoning/analysis -> Grok
        if any(keyword in task_lower for keyword in ["reason", "analyze", "explain", "why"]):
            return "grok"

        # Content generation with GitHub context -> Jules
        if any(keyword in context_lower for keyword in ["github", "repository", "repo", "commit"]):
            return "jules"

        # Creative writing -> Gemini
        if any(keyword in task_lower for keyword in ["write", "story", "creative", "article"]):
            return "gemini"

        # Default to Grok for general tasks
        return "grok"

    def query_grok(self, prompt: str, **params) -> Dict[str, Any]:
        """Query xAI Grok model"""
        if not self.grok_key:
            raise ValueError("XAI_API_KEY not configured")

        url = "https://api.x.ai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.grok_key}", "Content-Type": "application/json"}

        payload = {
            "model": "grok-1",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": params.get("max_tokens", 1000),
            "temperature": params.get("temperature", 0.7)
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        result = response.json()
        return {
            "model": "grok",
            "response": result["choices"][0]["message"]["content"],
            "timestamp": json.dumps({"timestamp": "now"}, default=str)
        }

    def query_gemini(self, prompt: str, **params) -> Dict[str, Any]:
        """Query Google Gemini model"""
        if not self.gemini_key:
            raise ValueError("GEMINI_API_KEY not configured")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.gemini_key}"
        headers = {"Content-Type": "application/json"}

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": params.get("max_tokens", 1000),
                "temperature": params.get("temperature", 0.7)
            }
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        result = response.json()
        return {
            "model": "gemini",
            "response": result["candidates"][0]["content"]["parts"][0]["text"],
            "timestamp": json.dumps({"timestamp": "now"}, default=str)
        }

    def query_jules(self, prompt: str, repo_context: Optional[str] = None) -> Dict[str, Any]:
        """Query Jules for content generation with GitHub context"""
        if not self.jules_key:
            raise ValueError("JULES_API_KEY not configured")

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.jules_key
        }

        # Auto-select repository if not provided
        if not repo_context:
            # Try to find a suitable repo (this would need more sophisticated logic)
            repo_context = "sources/github/user/repo"  # Placeholder

        payload = {
            "prompt": prompt,
            "sourceContext": {
                "source": repo_context,
                "githubRepoContext": {"startingBranch": "main"}
            },
            "title": f"SDK Integration: {prompt[:30]}..."
        }

        url = "https://jules.googleapis.com/v1alpha/sessions"
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        result = response.json()
        return {
            "model": "jules",
            "session_url": result.get("url"),
            "session_id": result.get("id"),
            "timestamp": json.dumps({"timestamp": "now"}, default=str)
        }

    def orchestrate_query(self, prompt: str, context: str = "", **params) -> Dict[str, Any]:
        """Automatically route and execute query using best model"""
        model = self.route_task_to_model(prompt, context)

        try:
            if model == "grok":
                return self.query_grok(prompt, **params)
            elif model == "gemini":
                return self.query_gemini(prompt, **params)
            elif model == "jules":
                return self.query_jules(prompt, context)
            else:
                raise ValueError(f"Unknown model: {model}")
        except Exception as e:
            return {
                "error": f"Failed to query {model}: {str(e)}",
                "model": model,
                "timestamp": json.dumps({"error": "timestamp failed"}, default=str)
            }


if __name__ == "__main__":
    # Example usage
    print("Nexus Delta SDK v2.1.0 - Enhanced with Multi-Model AI")
    print("=" * 60)
    print("\nNew Features:")
    print("• Multi-model AI orchestration (Grok, Gemini, Jules)")
    print("• Intelligent task routing")
    print("• Hyper-scale content generation")
    print("• CLI tools for AI queries")
    print("\nExample Usage:")
    print("""
    from nexusdelta_sdk_enhanced import NexusDeltaSDK, MultiModelOrchestrator

    # Initialize enhanced SDK
    sdk = NexusDeltaSDK(api_key="your_firebase_token")

    # Create multi-model agent
    agent = sdk.create_multi_model_agent("AICodeAssistant", "Multi-model coding assistant")

    # Orchestrate AI queries
    result = sdk.orchestrate_ai_query("Write a Python fibonacci function")
    print(f"Model used: {result['model']}")
    print(f"Response: {result['response']}")

    # Direct model access
    grok_result = sdk.orchestrate_ai_query("Explain quantum computing", model="grok")
    gemini_result = sdk.orchestrate_ai_query("Generate API documentation", model="gemini")

    # Use standalone orchestrator
    orchestrator = MultiModelOrchestrator()
    capabilities = orchestrator.model_capabilities
    print(f"Available models: {list(capabilities.keys())}")
    """)