# test_firebase_registration.py (Corrected)
import os
from nexusdelta_sdk import NexusDeltaSDK

# --- Configuration ---
# The manifest URL needs to be a valid web URL.
# For this test, we'll use a placeholder URL. The server doesn't fetch it
# during registration, it just stores the URL. We'll use the real one later.
MANIFEST_URL = "https://gist.githubusercontent.com/oogalieboogalie/2597c9548f3aaeea650c9f5155433f44/raw/8f270e3fc0557fb12e85afb357f4be269f73629f/quantflow.manifest.json"

print(f"Attempting to register agent with manifest URL: {MANIFEST_URL}")

try:
    # 1. Initialize the SDK. The API key is not used by our current server,
    #    but the class requires it. The base_url will be found automatically.
    sdk = NexusDeltaSDK(api_key="test-key")

    # 2. Use the SDK instance to register the agent
    agent_id = sdk.register_manifest(MANIFEST_URL)
    
    print("\n✅ Registration successful!")
    print(f"   Marketplace assigned Agent ID: {agent_id}")
    print("\n➡️ Now, check the 'agents' collection in your Firebase Firestore console to see the new entry!")

except Exception as e:
    print(f"\nRegistration failed.")
    print(f"   Error: {e}")
    print("\n   Troubleshooting:")
    print("   1. Is the main.py server running? (python -m uvicorn main:app --reload)")
    print("   2. Is the API endpoint in `base_url` correct?")
    print("   3. Is the Firebase connection configured correctly in main.py?")