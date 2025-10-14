# Nexus Delta SDK - Official Python SDK for the Nexus Delta AI Agent Marketplace
# Version: 2.0.0
# Compatible with: Microservices Architecture (API Gateway)
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
            "User-Agent": "NexusDeltaSDK/2.0.0",
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

    # Backwards compatibility aliases
    def find_service(self, query: str) -> List[Dict[str, Any]]:
        """Legacy alias for search_agents"""
        logger.warning("⚠️ find_service() is deprecated, use search_agents() instead")
        return self.search_agents(query)
    
    def get_registered_agents(self) -> List[Dict[str, Any]]:
        """Legacy alias for get_all_agents"""
        logger.warning("⚠️ get_registered_agents() is deprecated, use get_all_agents() instead")
        return self.get_all_agents()


if __name__ == "__main__":
    # Example usage
    print("Nexus Delta SDK v2.0.0")
    print("=" * 50)
    print("\nExample Usage:")
    print("""
    from nexusdelta_sdk import NexusDeltaSDK
    
    # Initialize with Firebase token
    sdk = NexusDeltaSDK(api_key="your_firebase_id_token")
    
    # Check system health
    health = sdk.health_check()
    print(f"Gateway: {health['gateway']}")
    
    # Search for agents
    agents = sdk.search_agents("data processing")
    for agent in agents:
        print(f"- {agent['name']}: {agent['purpose']}")
    
    # Execute a tool
    result = sdk.execute_tool(
        agent_id="agent_abc123",
        tool_name="process",
        payload={"data": [1, 2, 3]}
    )
    
    # Register your own agent
    agent_card = {
        "name": "MyAgent",
        "purpose": "Does something cool",
        "category": "utility",
        "model": "gpt-4",
        "tools": [{"id": "my_tool", "name": "My Tool"}]
    }
    response = sdk.register_agent(agent_card)
    print(f"Registered: {response['agent_id']}")
    """)
