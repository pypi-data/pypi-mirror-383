# 🚀 Quick Start Guide - Cloud Run Deployment

## Prerequisites
- [x] Google Cloud Platform account
- [x] `gcloud` CLI installed
- [x] `firebase` CLI installed (for hosting)
- [x] Docker installed (for local testing)

## 📝 Step-by-Step Deployment

### 1. Setup GCP Project
```powershell
# Set your project ID
$PROJECT_ID = "your-project-id"

# Login to GCP
gcloud auth login

# Set project
gcloud config set project $PROJECT_ID

# Enable billing (required for Cloud Run)
# Go to: https://console.cloud.google.com/billing
```

### 2. Local Testing (Optional but Recommended)
```powershell
# Terminal 1: Start orchestrator locally
cd c:\homebase-db\Nexus-Delta
python -m uvicorn main:app --host 127.0.0.1 --port 8080

# Terminal 2: Start test agent locally
$env:AGENT_HASH_ID="agent_test123456789"
$env:ORCHESTRATOR_URL="http://localhost:8080"
$env:AGENT_NAME="Test Agent"
$env:AGENT_MODEL="gpt-4"
python -m uvicorn agent_runner:app --host 127.0.0.1 --port 8001

# Terminal 3: Run tests
python test_cloud_run.py
```

### 3. Deploy to Cloud Run
```powershell
# Run deployment script
.\deploy-cloud-run.ps1 -ProjectId "your-project-id"

# This will:
# ✅ Enable required APIs
# ✅ Deploy orchestrator to Cloud Run
# ✅ Build agent base image
# ✅ Deploy test agent
# ✅ Output all URLs
```

### 4. Deploy Frontend to Firebase Hosting
```powershell
# Install Firebase CLI (if not installed)
npm install -g firebase-tools

# Login to Firebase
firebase login

# Initialize Firebase (first time only)
firebase init hosting

# Select options:
# - What do you want to use as your public directory? pages
# - Configure as a single-page app (rewrite all urls to /index.html)? No
# - Set up automatic builds and deploys with GitHub? No

# Deploy
firebase deploy --only hosting

# Your website will be at: https://your-project-id.web.app
```

### 5. Update Frontend to Use Cloud Run API
After deployment, you'll get URLs like:
- Orchestrator: `https://nexus-delta-orchestrator-xxx.run.app`
- Test Agent: `https://nexus-agent-agent_test123456789-xxx.run.app`

Update your frontend to point to the orchestrator URL:

```javascript
// In pages/agent-architect.js
const API_BASE_URL = 'https://nexus-delta-orchestrator-xxx.run.app';

fetch(`${API_BASE_URL}/v1/agents/register`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ agent_card: agentCard })
})
```

### 6. Test Production Deployment
```powershell
# Test orchestrator health
curl https://nexus-delta-orchestrator-xxx.run.app/

# Test agent health
curl https://nexus-agent-agent_test123456789-xxx.run.app/health

# Test agent execution (with auth)
curl -X POST https://nexus-agent-agent_test123456789-xxx.run.app/execute `
  -H "Content-Type: application/json" `
  -H "X-Agent-Auth: agent_test123456789" `
  -d '{"tool":"web","payload":{"query":"test"},"context":{}}'
```

## 🎯 What You've Deployed

### Architecture
```
Firebase Hosting (Global CDN)
        ↓
Orchestrator (us-central1)
        ↓
Individual Agents (us-central1)
```

### Services
1. **Orchestrator** - Central hub
   - URL: `https://nexus-delta-orchestrator-xxx.run.app`
   - Always running (min instances: 1)
   - Handles registry, auth, routing

2. **Test Agent** - Example isolated agent
   - URL: `https://nexus-agent-{hash_id}-xxx.run.app`
   - Scales to zero when idle
   - Executes tools independently

3. **Frontend** - Static website
   - URL: `https://your-project-id.web.app`
   - Global CDN (fast everywhere)
   - Calls orchestrator API

## 💰 Expected Costs

### Free Tier (First Month)
- Cloud Run: 2M requests free
- Firebase Hosting: 10 GB free
- Firestore: 50K reads, 20K writes free

### After Free Tier (Moderate Usage)
- ~$235/month for:
  - Orchestrator always-on
  - 100 agents (1hr/day average)
  - 50GB hosting bandwidth
  - Firestore operations

## 🔧 Common Issues

### Issue: "Permission denied" during deployment
```powershell
# Grant yourself admin roles
gcloud projects add-iam-policy-binding $PROJECT_ID `
  --member=user:your-email@gmail.com `
  --role=roles/run.admin

gcloud projects add-iam-policy-binding $PROJECT_ID `
  --member=user:your-email@gmail.com `
  --role=roles/iam.serviceAccountUser
```

### Issue: "Billing not enabled"
Go to: https://console.cloud.google.com/billing and enable billing

### Issue: Agent can't reach orchestrator
- Check orchestrator is deployed: `gcloud run services list`
- Verify URL is correct in agent env vars
- Check agent logs: `gcloud run logs read nexus-agent-{hash_id} --region us-central1`

### Issue: Frontend 404 errors
- Ensure `firebase.json` has correct rewrites
- Check that `pages` directory is set as public directory
- Redeploy: `firebase deploy --only hosting`

## 📊 Monitoring

### View Logs
```powershell
# Orchestrator logs
gcloud run logs read nexus-delta-orchestrator --region us-central1 --limit 50

# Agent logs
gcloud run logs read nexus-agent-{hash_id} --region us-central1 --limit 50
```

### View Metrics
```powershell
# Open Cloud Console
start https://console.cloud.google.com/run?project=$PROJECT_ID
```

### Setup Alerts
1. Go to Cloud Monitoring
2. Create alert for:
   - Request latency > 1s
   - Error rate > 5%
   - CPU utilization > 80%

## 🚀 Next Steps

1. **Add More Agents**
   - Create agents in Agent Architect
   - Orchestrator auto-deploys them to Cloud Run

2. **Implement Tool Handlers**
   - Edit `agent_runner.py`
   - Add real logic to tool handlers (web, code, database, etc.)

3. **Add Authentication**
   - Implement JWT tokens
   - Add user management
   - Restrict agent creation to admins

4. **Setup CI/CD**
   - GitHub Actions for auto-deployment
   - Automated testing
   - Blue-green deployments

5. **Add Monitoring**
   - Setup Cloud Monitoring dashboards
   - Configure error alerting
   - Track usage metrics

## 📚 Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Firebase Hosting Guide](https://firebase.google.com/docs/hosting)
- [Firestore Documentation](https://firebase.google.com/docs/firestore)
- [Architecture Document](./CLOUD_RUN_ARCHITECTURE.md)

---

**Ready to deploy?** Run: `.\deploy-cloud-run.ps1 -ProjectId "your-project-id"`
