#!/usr/bin/env python3
"""
Basic SDK Usage Example
Demonstrates core Nexus Delta SDK functionality
"""

from nexusdelta import NexusDeltaSDK

def main():
    # Initialize the SDK
    # Note: You'll need a valid Firebase auth token
    sdk = NexusDeltaSDK(api_key="your_firebase_token_here")

    print("🔍 Checking SDK connection...")
    try:
        # Test connection
        health = sdk.health_check()
        print(f"✅ Connected to Nexus Delta: {health}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    print("\n🤖 Registering a sample agent...")
    try:
        agent_card = {
            "name": "SampleDataAgent",
            "purpose": "Demonstrate basic data processing capabilities",
            "category": "data_processing",
            "model": "gpt-4",
            "tools": [
                {
                    "name": "process_numbers",
                    "description": "Process and analyze numerical data"
                },
                {
                    "name": "generate_summary",
                    "description": "Generate summary statistics"
                }
            ]
        }

        response = sdk.register_agent(agent_card)
        agent_id = response.get("agent_id")
        print(f"✅ Agent registered with ID: {agent_id}")

    except Exception as e:
        print(f"❌ Agent registration failed: {e}")
        return

    print("\n🔍 Searching for agents...")
    try:
        agents = sdk.search_agents("data")
        print(f"✅ Found {len(agents)} agents in marketplace")

        if agents:
            print("Sample agents:")
            for agent in agents[:3]:  # Show first 3
                print(f"  - {agent.get('name', 'Unknown')} ({agent.get('category', 'uncategorized')})")

    except Exception as e:
        print(f"❌ Agent search failed: {e}")

    print("\n🛠️  Testing tool execution...")
    try:
        # This would execute a tool if one was available
        # result = sdk.execute_tool(agent_id, "process_numbers", {"data": [1,2,3,4,5]})
        # print(f"✅ Tool execution result: {result}")
        print("ℹ️  Tool execution requires running agent containers")

    except Exception as e:
        print(f"❌ Tool execution failed: {e}")

    print("\n🎉 SDK demo completed!")

if __name__ == "__main__":
    main()