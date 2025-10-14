# 🧪 Local Testing Guide for Cloud Run Architecture

## Overview

Before deploying to Google Cloud Run, we need to test the complete flow locally:
- **Frontend** (HTML/JS) → **Orchestrator** (main.py) → **Agent** (agent_runner.py)

This mimics the production Cloud Run setup where each agent runs in an isolated container.

---

## Quick Start (5 Minutes)

### Option 1: Automated Setup (Recommended)

Run the all-in-one test script:

```powershell
.\test-local-deployment.ps1
```

This will:
1. ✅ Start orchestrator on port 8000
2. ✅ Start test agent on port 8001
3. ✅ Start frontend on port 8080
4. ✅ Register test agent with orchestrator
5. ✅ Open browser to Agent Architect
6. ✅ Monitor all services

**Then test in the UI:**
1. Fill in agent name: "My Test Agent"
2. Select model: "GPT-5 Mini"
3. Select tools: Web, Code
4. Click "Submit for Vetting & Deployment"
5. Check if it registers successfully! ✅

### Option 2: Manual Setup (If script doesn't work)

**Terminal 1 - Orchestrator:**
```powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 - Test Agent:**
```powershell
$env:AGENT_HASH_ID = "agent_test1234567890"
$env:ORCHESTRATOR_URL = "http://127.0.0.1:8000"
$env:AGENT_NAME = "Test Agent"
$env:AGENT_MODEL = "gpt-5-mini"
python -m uvicorn agent_runner:app --host 127.0.0.1 --port 8001 --reload
```

**Terminal 3 - Frontend:**
```powershell
python -m http.server 8080 --bind 127.0.0.1
```

**Then register test agent:**
```powershell
$body = @{
    agent_card = @{
        version = "1.0.0"
        hash_id = "agent_test1234567890"
        name = "Test Agent"
        purpose = "Local testing"
        category = "testing"
        model = "gpt-5-mini"
        tools = @(
            @{ id = "web"; name = "Web Browser" }
        )
        deployment = @{
            type = "local"
            url = "http://127.0.0.1:8001"
            isolated = $true
            status = "active"
        }
    }
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://127.0.0.1:8000/v1/agents/register" -Method Post -Body $body -ContentType "application/json"
```

---

## Integration Tests

Run automated integration tests:

```powershell
python test_integration.py
```

This tests:
- ✅ Orchestrator health
- ✅ Agent health
- ✅ Agent info endpoint
- ✅ Agent registration
- ✅ Registry search
- ✅ Tool execution with auth
- ✅ Auth rejection (security test)

**Expected Output:**
```
═══════════════════════════════════════════════════
  Nexus Delta Integration Tests
═══════════════════════════════════════════════════

🧪 TEST: Orchestrator Health Check
✓ Orchestrator is running

🧪 TEST: Agent Health Check
✓ Agent is running

...

📊 Test Summary
═══════════════════════════════════════════════════
  ✓ PASS - Orchestrator Health
  ✓ PASS - Agent Health
  ✓ PASS - Agent Info
  ✓ PASS - Agent Registration
  ✓ PASS - Registry Search
  ✓ PASS - Agent Execution
  ✓ PASS - Auth Rejection

Result: 7/7 tests passed
🎉 All tests passed! Ready for Cloud Run deployment!
```

---

## Testing Checklist

### Frontend Testing
- [ ] Open http://127.0.0.1:8080/pages/agent-architect.html
- [ ] See API Key toggle (Alpha Keys / BYOK)
- [ ] See model dropdown with organized providers
- [ ] Fill in agent form (name, purpose, category)
- [ ] Select a model (try GPT-5 Mini)
- [ ] Select tools from catalog
- [ ] Preview updates in real-time
- [ ] JSON preview shows correct structure
- [ ] Click "Submit for Vetting & Deployment"
- [ ] See success message or error (check browser console F12)

### API Testing
```powershell
# Test orchestrator
Invoke-RestMethod http://127.0.0.1:8000/

# Search registry
Invoke-RestMethod "http://127.0.0.1:8000/v1/registry/search?query=all"

# Test agent health
Invoke-RestMethod http://127.0.0.1:8001/health

# Test agent info
Invoke-RestMethod http://127.0.0.1:8001/info

# Test agent execution (with auth)
$headers = @{ "X-Agent-Auth" = "agent_test1234567890" }
$body = @{ tool = "web"; payload = @{ action = "test" }; context = @{} } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8001/execute" -Method Post -Headers $headers -Body $body -ContentType "application/json"
```

### Security Testing
```powershell
# This should fail (wrong hash)
$headers = @{ "X-Agent-Auth" = "wrong_hash" }
$body = @{ tool = "web"; payload = @{ action = "test" }; context = @{} } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8001/execute" -Method Post -Headers $headers -Body $body -ContentType "application/json"
# Expected: 403 Forbidden
```

---

## Architecture Comparison

### Local (What you're testing now)
```
Browser (localhost:8080/pages)
    ↓
Orchestrator (localhost:8000) ← main.py
    ↓ (X-Agent-Auth header)
Agent (localhost:8001) ← agent_runner.py
```

### Cloud Run (Production)
```
Browser (your-domain.web.app via Firebase CDN)
    ↓ (HTTPS, global CDN)
Orchestrator (orchestrator-xyz.run.app in us-central1)
    ↓ (X-Agent-Auth header, private network)
Agent 1 (agent-abc123.run.app) - Isolated container
Agent 2 (agent-def456.run.app) - Isolated container
Agent 3 (agent-ghi789.run.app) - Isolated container
```

**Key differences:**
- Production uses HTTPS with Firebase Hosting CDN
- Each agent gets its own Cloud Run service URL
- Agents auto-scale (0 to N instances)
- Agent URLs are private (not publicly accessible)
- Orchestrator validates hashID before forwarding

---

## Common Issues & Fixes

### Issue: "Port already in use"
```powershell
# Kill processes on those ports
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
Get-Process -Id (Get-NetTCPConnection -LocalPort 8001).OwningProcess | Stop-Process -Force
Get-Process -Id (Get-NetTCPConnection -LocalPort 8080).OwningProcess | Stop-Process -Force
```

### Issue: "Module not found"
```powershell
# Install dependencies
pip install -r requirements.txt
```

### Issue: Frontend can't reach orchestrator
**Check `agent-architect.js`** - Registration URL should be:
```javascript
fetch('/v1/agents/register', {  // This works because it's relative
    method: 'POST',
    // ...
})
```

**OR** if frontend is on different port:
```javascript
fetch('http://127.0.0.1:8000/v1/agents/register', {
    method: 'POST',
    // ...
})
```

### Issue: Firebase not working
The app falls back to in-memory storage automatically. Check logs:
```
[SERVER] Firebase save failed: XYZ. Using JSON fallback.
```

This is OK for local testing. Firebase is only needed for production persistence.

### Issue: Agent returns 401/403
Make sure `X-Agent-Auth` header matches `AGENT_HASH_ID`:
```powershell
# Agent started with:
$env:AGENT_HASH_ID = "agent_test1234567890"

# Request must include:
$headers = @{ "X-Agent-Auth" = "agent_test1234567890" }
```

---

## What You're Actually Testing

### 1. **Frontend → Orchestrator Communication**
When you click "Submit" in Agent Architect:
```
POST http://127.0.0.1:8000/v1/agents/register
Content-Type: application/json

{
  "agent_card": {
    "hash_id": "agent_xyz123...",
    "name": "My Agent",
    "model": "gpt-5-mini",
    // ...
  }
}
```

### 2. **Orchestrator → Agent Communication**
When agent needs to execute a tool:
```
POST http://127.0.0.1:8001/execute
X-Agent-Auth: agent_test1234567890
Content-Type: application/json

{
  "tool": "web",
  "payload": { "action": "search", "query": "test" },
  "context": {}
}
```

### 3. **Agent → Tool Execution**
Inside `agent_runner.py`:
```python
async def execute_web_tool(payload: Dict[str, Any]):
    # This is where actual web scraping/browsing happens
    # Currently mocked for testing
    return {"status": "success", "data": "mock result"}
```

---

## Next Steps After Local Testing

Once all tests pass locally:

### 1. Create Google Cloud Project
```powershell
gcloud projects create nexus-delta --name="Nexus Delta"
gcloud config set project nexus-delta
```

### 2. Enable Required APIs
```powershell
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable firestore.googleapis.com
```

### 3. Deploy Orchestrator
```powershell
.\deploy-cloud-run.ps1 -ProjectId "nexus-delta"
```

### 4. Deploy Frontend to Firebase
```powershell
firebase init hosting
firebase deploy --only hosting
```

### 5. Update Frontend Config
In `agent-architect.js`, change API URL:
```javascript
const API_BASE = 'https://orchestrator-xyz.run.app';  // Your Cloud Run URL
```

---

## Monitoring & Debugging

### Check Logs
```powershell
# Orchestrator logs
Get-Content transaction.log -Tail 50 -Wait

# Watch all terminals for errors
```

### Browser DevTools (F12)
- **Console**: JavaScript errors
- **Network**: API requests/responses
- **Application**: LocalStorage, cookies

### API Documentation
- Orchestrator: http://127.0.0.1:8000/docs
- Agent: http://127.0.0.1:8001/docs

---

## Summary

✅ **Run this to test everything:**
```powershell
.\test-local-deployment.ps1
```

✅ **Then run integration tests:**
```powershell
python test_integration.py
```

✅ **Test in browser:**
http://127.0.0.1:8080/pages/agent-architect.html

If all tests pass, you're ready for Cloud Run deployment! 🚀

**Questions?**
- Check logs in terminal windows
- Check browser console (F12)
- Review CLOUD_RUN_ARCHITECTURE.md
- Review API_KEY_STRATEGY.md
