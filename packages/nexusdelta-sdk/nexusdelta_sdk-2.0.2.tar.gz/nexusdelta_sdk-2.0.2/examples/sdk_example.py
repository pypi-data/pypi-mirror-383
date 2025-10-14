#!/usr/bin/env python3
"""
NEXUS DELTA SDK - SIMPLE USAGE EXAMPLE
This shows what developers can do with your SDK
"""

from nexusdelta_sdk import NexusDeltaSDK

def main():
    print("🚀 Nexus Delta SDK - What Developers Can Do")
    print("=" * 50)

    # Initialize SDK
    sdk = NexusDeltaSDK(api_key="test_token_for_development")

    print("\n1️⃣ REGISTER AN AI AGENT")
    print("   Developers can create and register AI agents:")
    agent_data = {
        "name": "ContentWriter",
        "purpose": "Write creative content",
        "category": "content_creation",
        "model": "gpt-4",
        "tools": [
            {"name": "write_blog", "description": "Write blog posts"},
            {"name": "write_poetry", "description": "Write poems"}
        ]
    }

    print(f"   Agent: {agent_data['name']}")
    print(f"   Purpose: {agent_data['purpose']}")
    print(f"   Tools: {len(agent_data['tools'])} available")

    print("\n2️⃣ DISCOVER AGENTS")
    print("   Find agents in the marketplace:")
    print("   agents = sdk.search_agents('content creation')")
    print("   → Returns list of matching AI agents")

    print("\n3️⃣ EXECUTE AI TOOLS")
    print("   Use agent tools programmatically:")
    print("   result = sdk.execute_tool(")
    print("       agent_id='agent_abc123',")
    print("       tool_name='write_blog',")
    print("       payload={'topic': 'AI Future', 'length': 500}")
    print("   )")
    print("   → AI generates a 500-word blog post!")

    print("\n4️⃣ BUILD APPLICATIONS")
    print("   Developers can now build:")
    print("   • AI-powered writing assistants")
    print("   • Automated content workflows")
    print("   • Custom AI agent marketplaces")
    print("   • Integrated AI services")

    print("\n🎯 THE VALUE:")
    print("   • Zero AI infrastructure needed")
    print("   • Access to diverse AI agents")
    print("   • Pay-per-use model")
    print("   • Easy integration (pip install nexusdelta-sdk)")

    print("\n🔥 THIS PROVES:")
    print("   • AI collaboration can build real products")
    print("   • Non-technical founders can create platforms")
    print("   • The agent marketplace model works")
    print("   • SDK enables developer adoption")

if __name__ == "__main__":
    main()