# C:\homebase-db\Nexus-Delta\nexusdelta_sdk.py (Updated for Live API)
import requests
import json
from typing import List, Dict, Any, Optional

import os

# Base URL is now dynamically determined
def get_base_url():
    """Reads the port from .port file or defaults."""
    port_files = [".port", "nexusdelta.port"]
    for port_file in port_files:
        if os.path.exists(port_file):
            with open(port_file, "r") as f:
                port = f.read().strip()
                url = f"http://127.0.0.1:{port}"
                if _test_url(url):
                    return url
    
    # Try common development ports
    for port in [8000, 8001, 3000]:
        url = f"http://127.0.0.1:{port}"
        if _test_url(url):
            return url
    
    return "http://127.0.0.1:8000"  # Final fallback

def _test_url(url: str) -> bool:
    """Test if a URL is reachable."""
    try:
        response = requests.get(f"{url}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

class NexusDeltaSDK:
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """Initializes the SDK connection."""
        self.base_url = base_url or get_base_url()
        self.api_version = "v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "NexusDeltaSDK/1.1"
        }

    def _get_url(self, path: str) -> str:
        """Constructs the full API URL."""
        return f"{self.base_url}/{self.api_version}/{path}"

    def register_agent(self, agent_card: Dict[str, Any]) -> str:
        """
        Registers an agent directly with an agent card.
        Returns the Agent ID assigned by the marketplace.
        """
        url = self._get_url("agents/register")
        print("-" * 30)
        print(f"[SDK] Registering agent '{agent_card.get('name', 'Unknown')}' via POST to: {url}")
        
        response = requests.post(
            url,
            headers=self.headers,
            json={"agent_card": agent_card}
        )
        response.raise_for_status()
        data = response.json()
        print(f"[SDK] Agent registration successful. Assigned ID: {data['agent_id']}")
        return data['agent_id']

    def register_manifest(self, manifest_url: str) -> str:
        """
        Registers an agent's manifest URL with the Nexus Delta Registry.
        Returns the LIVE Agent ID assigned by the marketplace.
        """
        url = self._get_url("agents/register")
        print("-" * 30)
        print(f"[SDK] Attempting to register agent via POST to: {url}")
        
        response = requests.post(
            url,
            headers=self.headers,
            json={"manifest_url": manifest_url}
        )
        response.raise_for_status()
        data = response.json()
        print(f"[SDK] Live registration successful. Assigned ID: {data['agent_id']}")
        return data['agent_id']

    def find_service(self, natural_language_query: str) -> List[Dict[str, Any]]:
        """
        Queries the LIVE registry using natural language to find matching agent tools.
        """
        url = self._get_url("registry/search")
        print("-" * 30)
        print(f"[SDK] Searching for services matching: '{natural_language_query}' at {url}")
        
        response = requests.get(
            url,
            headers=self.headers,
            params={"query": natural_language_query}
        )
        response.raise_for_status()
        
        return response.json().get('matching_tools', [])

    def execute_tool(self, agent_id: str, tool_name: str, provider_id: str, payload: Dict[str, Any]) -> Any:
        """
        Sends a request to execute a specific tool on a specific provider's agent.
        Requires the ID of the agent making the request for authentication.
        """
        url = self._get_url("transaction/execute")
        print("-" * 30)
        print(f"[SDK] Sending execution request for tool '{tool_name}' on provider '{provider_id}'...")
        print(f"[SDK] Authenticating as Agent ID: {agent_id}")

        # Add the agent ID to the headers for this specific request
        auth_headers = self.headers.copy()
        auth_headers["X-Agent-ID"] = agent_id
        
        response = requests.post(
            url,
            headers=auth_headers,
            json={
                "tool_name": tool_name,
                "provider_id": provider_id,
                "payload": payload
            }
        )
        response.raise_for_status()
        
        return response.json().get('result')

    def generate_tool(self, name: str, description: str, input_type: str = "text", 
                     output_format: str = "text", capabilities: List[str] = None) -> Dict[str, Any]:
        """
        Generates a complete AI tool using the Tool Factory.
        Returns a dictionary with 'ui', 'code', 'docker', and 'api' keys.
        """
        if capabilities is None:
            capabilities = ["gpt4"]
            
        url = self._get_url("../api/generate-tool")  # Note: this is not versioned
        print("-" * 30)
        print(f"[SDK] Generating tool '{name}' via POST to: {url}")
        
        tool_data = {
            "name": name,
            "description": description,
            "inputType": input_type,
            "outputFormat": output_format,
            "capabilities": capabilities,
            "instructions": f"Create a robust {name} tool that {description.lower()}"
        }
        
        response = requests.post(
            url,
            headers=self.headers,
            json=tool_data
        )
        response.raise_for_status()
        
        result = response.json()
        print(f"[SDK] Tool generation successful. Generated {len(result.get('code', ''))} lines of code.")
        return result

    def health_check(self) -> Dict[str, Any]:
        """
        Checks the health status of the Nexus Delta server.
        """
        url = f"{self.base_url}/health"
        print(f"[SDK] Checking server health at: {url}")
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        return response.json()

    def get_registered_agents(self) -> List[Dict[str, Any]]:
        """
        Gets all registered agents from the marketplace.
        """
        tools = self.find_service("all")
        # Group by agent
        agents = {}
        for tool in tools:
            agent_id = tool['agent_id']
            if agent_id not in agents:
                agents[agent_id] = {
                    'agent_id': agent_id,
                    'agent_name': tool['agent_name'],
                    'tools': []
                }
            agents[agent_id]['tools'].append(tool['tool_data'])
        
        return list(agents.values())

# The `if __name__ == '__main__':` block is removed as it's no longer the driver, 
# and the `consumer_agent_orchestrator.py` is now the main entry point.
