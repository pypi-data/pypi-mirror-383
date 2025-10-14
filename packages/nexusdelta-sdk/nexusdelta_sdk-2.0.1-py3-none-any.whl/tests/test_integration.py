"""
Integration Test for Nexus Delta
Tests orchestrator ↔ agent communication locally before Cloud Run deployment
"""
import requests
import time
import json
from typing import Dict, Any

# Configuration
ORCHESTRATOR_URL = "http://127.0.0.1:8000"
AGENT_URL = "http://127.0.0.1:8001"
TEST_AGENT_HASH = "agent_test1234567890"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_test(name: str):
    print(f"\n{Colors.CYAN}🧪 TEST: {name}{Colors.END}")

def print_success(msg: str):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg: str):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

def test_orchestrator_health():
    """Test if orchestrator is responding"""
    print_test("Orchestrator Health Check")
    try:
        response = requests.get(f"{ORCHESTRATOR_URL}/", timeout=5)
        if response.status_code == 200:
            print_success(f"Orchestrator is running")
            print_info(f"Response: {response.json()}")
            return True
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed to connect: {e}")
        return False

def test_agent_health():
    """Test if agent is responding"""
    print_test("Agent Health Check")
    try:
        response = requests.get(f"{AGENT_URL}/health", timeout=5)
        if response.status_code == 200:
            print_success(f"Agent is running")
            print_info(f"Response: {response.json()}")
            return True
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed to connect: {e}")
        return False

def test_agent_info():
    """Test agent info endpoint"""
    print_test("Agent Info")
    try:
        response = requests.get(f"{AGENT_URL}/info", timeout=5)
        if response.status_code == 200:
            info = response.json()
            print_success(f"Agent info retrieved")
            print_info(f"Agent: {info.get('agent_name')} ({info.get('agent_id')})")
            print_info(f"Model: {info.get('model')}")
            print_info(f"Orchestrator: {info.get('orchestrator_url')}")
            return True
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed: {e}")
        return False

def test_agent_registration():
    """Test registering an agent with orchestrator"""
    print_test("Agent Registration")
    
    agent_card = {
        "agent_card": {
            "version": "1.0.0",
            "hash_id": TEST_AGENT_HASH,
            "name": "Integration Test Agent",
            "purpose": "Testing orchestrator-agent communication",
            "category": "testing",
            "model": "gpt-5-mini",
            "tools": [
                {"id": "web", "name": "Web Browser"},
                {"id": "code", "name": "Code Execution"}
            ],
            "deployment": {
                "type": "local",
                "url": AGENT_URL,
                "isolated": True,
                "status": "active"
            },
            "metadata": {
                "created_at": "2025-10-11T00:00:00Z",
                "created_with": "Integration Test"
            }
        }
    }
    
    try:
        response = requests.post(
            f"{ORCHESTRATOR_URL}/v1/agents/register",
            json=agent_card,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success("Agent registered successfully")
            print_info(f"Agent ID: {result.get('agent_id')}")
            print_info(f"Status: {result.get('status')}")
            return True
        elif response.status_code == 409:
            print_success("Agent already registered (this is OK)")
            return True
        else:
            print_error(f"Registration failed: {response.status_code}")
            print_info(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Failed: {e}")
        return False

def test_registry_search():
    """Test searching the agent registry"""
    print_test("Registry Search")
    try:
        response = requests.get(
            f"{ORCHESTRATOR_URL}/v1/registry/search",
            params={"query": "all"},
            timeout=5
        )
        
        if response.status_code == 200:
            results = response.json()
            print_success(f"Registry search successful")
            print_info(f"Found {len(results.get('agents', []))} agents")
            
            for agent in results.get('agents', []):
                print_info(f"  - {agent.get('name')} ({agent.get('hash_id')})")
            
            return True
        else:
            print_error(f"Search failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed: {e}")
        return False

def test_agent_execution():
    """Test executing a tool via the agent"""
    print_test("Agent Tool Execution (with auth)")
    
    execution_request = {
        "tool": "web",
        "payload": {
            "action": "search",
            "query": "test"
        },
        "context": {}
    }
    
    try:
        # This should fail without proper auth
        response = requests.post(
            f"{AGENT_URL}/execute",
            json=execution_request,
            headers={"X-Agent-Auth": TEST_AGENT_HASH},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success("Tool execution successful")
            print_info(f"Status: {result.get('status')}")
            print_info(f"Result: {json.dumps(result.get('result'), indent=2)}")
            return True
        else:
            print_error(f"Execution failed: {response.status_code}")
            print_info(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Failed: {e}")
        return False

def test_agent_auth_failure():
    """Test that invalid auth is rejected"""
    print_test("Agent Authentication (should fail)")
    
    execution_request = {
        "tool": "web",
        "payload": {"action": "test"},
        "context": {}
    }
    
    try:
        response = requests.post(
            f"{AGENT_URL}/execute",
            json=execution_request,
            headers={"X-Agent-Auth": "wrong_hash_12345678"},
            timeout=5
        )
        
        if response.status_code == 403:
            print_success("Authentication correctly rejected invalid hash")
            return True
        else:
            print_error(f"Unexpected status: {response.status_code} (expected 403)")
            return False
    except Exception as e:
        print_error(f"Failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}═══════════════════════════════════════════════════{Colors.END}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}  Nexus Delta Integration Tests{Colors.END}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}═══════════════════════════════════════════════════{Colors.END}")
    
    print(f"\n{Colors.YELLOW}📋 Configuration:{Colors.END}")
    print(f"  Orchestrator: {ORCHESTRATOR_URL}")
    print(f"  Agent:        {AGENT_URL}")
    print(f"  Test Hash:    {TEST_AGENT_HASH}")
    
    tests = [
        ("Orchestrator Health", test_orchestrator_health),
        ("Agent Health", test_agent_health),
        ("Agent Info", test_agent_info),
        ("Agent Registration", test_agent_registration),
        ("Registry Search", test_registry_search),
        ("Agent Execution", test_agent_execution),
        ("Auth Rejection", test_agent_auth_failure),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            results.append((name, test_func()))
        except Exception as e:
            print_error(f"Test crashed: {e}")
            results.append((name, False))
        time.sleep(0.5)  # Small delay between tests
    
    # Summary
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}═══════════════════════════════════════════════════{Colors.END}")
    print(f"{Colors.BOLD}📊 Test Summary{Colors.END}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}═══════════════════════════════════════════════════{Colors.END}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{Colors.GREEN}✓ PASS{Colors.END}" if result else f"{Colors.RED}✗ FAIL{Colors.END}"
        print(f"  {status} - {name}")
    
    print(f"\n{Colors.BOLD}Result: {passed}/{total} tests passed{Colors.END}")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 All tests passed! Ready for Cloud Run deployment!{Colors.END}\n")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}⚠️  Some tests failed. Review the logs above.{Colors.END}\n")
        return 1

if __name__ == "__main__":
    exit(main())
