#!/usr/bin/env python3
"""
Nexus Delta SDK Test Script
Run this to verify your SDK installation and server connection.
"""

import sys
from nexusdelta_sdk import NexusDeltaSDK

def test_sdk():
    """Test basic SDK functionality."""
    print("🧪 Testing Nexus Delta SDK...")
    print("=" * 50)

    # Initialize SDK (will use demo key for testing)
    try:
        sdk = NexusDeltaSDK(api_key="demo-key")
        print("✅ SDK initialized successfully")
    except Exception as e:
        print(f"❌ SDK initialization failed: {e}")
        return False

    # Test health check
    try:
        health = sdk.health_check()
        print("✅ Health check passed")
        print(f"   Status: {health.get('status')}")
        print(f"   Agents registered: {health.get('agents_registered')}")
        print(f"   Agents running: {health.get('agents_running')}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

    # Test service discovery
    try:
        tools = sdk.find_service("all")
        print("✅ Service discovery working")
        print(f"   Found {len(tools)} tools")
        if tools:
            # Get total tools across all agents
            total_tools = sum(len(agent.get('tools', [])) for agent in tools)
            print(f"   Total tools available: {total_tools}")
            if total_tools > 0:
                # Show first tool from first agent
                first_agent_tools = tools[0].get('tools', [])
                if first_agent_tools:
                    print(f"   Sample tool: {first_agent_tools[0]['name']}")
    except Exception as e:
        print(f"❌ Service discovery failed: {e}")
        return False

    # Test tool listing (replaces generate_tool test)
    try:
        tools = sdk.list_tools()
        print("✅ Tool listing working")
        print(f"   Found {len(tools)} available tools")
        if tools:
            print(f"   Sample tool: {tools[0].get('name', 'Unknown')}")
    except Exception as e:
        print(f"❌ Tool listing failed: {e}")
        return False

    print("=" * 50)
    print("🎉 All SDK tests passed!")
    print("\nNext steps:")
    print("1. Get your API key from the Nexus Delta dashboard")
    print("2. Update your code to use the real API key")
    print("3. Start building agents and tools!")
    return True

if __name__ == "__main__":
    success = test_sdk()
    sys.exit(0 if success else 1)