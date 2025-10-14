#!/usr/bin/env python3
"""
NEXUS DELTA SDK - PUBLIC DEMO WITH NGROK
This demonstrates the SDK working over the public internet!
"""

from nexusdelta_sdk import NexusDeltaSDK

def main():
    print("🌐 NEXUS DELTA PUBLIC DEMO - Via Ngrok")
    print("=" * 50)
    print("🚀 SDK connecting to public URL (not localhost!)")

    # Use the ngrok URL instead of localhost
    ngrok_url = "https://b14f4829578a.ngrok.app"

    print(f"📡 Public API Gateway: {ngrok_url}")

    # Initialize SDK with ngrok URL
    sdk = NexusDeltaSDK(
        api_key="test_token_for_development",
        base_url=ngrok_url
    )

    print("\n✅ SDK initialized with public endpoint!")

    # Test health check
    print("\n🏥 Testing public health check...")
    try:
        health = sdk.health_check()
        print("✅ Public API is responding!")
        print(f"   Services: {len(health.get('services', {}))} running")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return

    # Register an agent
    print("\n🤖 Registering agent via public API...")
    agent_data = {
        "hash_id": f"public-demo-agent",
        "name": "Public Demo Agent",
        "purpose": "Demonstrate public API functionality",
        "category": "demo",
        "expertise": "Public API testing",
        "model": "gpt-4",
        "tools": [
            {"name": "demo_tool", "description": "Demo tool for public testing"}
        ]
    }

    try:
        result = sdk.register_agent(agent_data)
        agent_id = result.get('agent_id')
        print("✅ Agent registered via public API!")
        print(f"   Agent ID: {agent_id}")
    except Exception as e:
        print(f"❌ Registration failed: {e}")
        return

    # Get agent details
    print("\n📋 Fetching agent details via public API...")
    try:
        agent_details = sdk.get_agent(agent_id)
        print("✅ Agent details retrieved via public API!")
        print(f"   Name: {agent_details.get('name')}")
        print(f"   Status: {agent_details.get('status')}")
    except Exception as e:
        print(f"❌ Failed to get agent: {e}")

    # Execute tool
    print("\n⚡ Executing tool via public API...")
    try:
        result = sdk.execute_tool(agent_id, "demo_tool", {"message": "Hello from public API!"})
        print("✅ Tool executed via public API!")
        print(f"   Status: {result.get('status')}")
    except Exception as e:
        print(f"❌ Tool execution failed: {e}")

    print("\n🎉 SUCCESS!")
    print("   • SDK works over public internet")
    print("   • Alpha testers can access your API")
    print("   • No Cloud Run deployment needed!")
    print(f"   • Public URL: {ngrok_url}")

    print("\n🔗 SHARE THIS WITH ALPHA TESTERS:")
    print(f"   API Gateway: {ngrok_url}")
    print("   SDK: pip install nexusdelta-sdk")
    print("   Example code in: sdk_example.py")

if __name__ == "__main__":
    main()