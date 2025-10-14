# MICROSERVICES ARCHITECTURE - HIGH-LEVEL DESIGN
**Replacing Monolithic Orchestrator with Scalable Microservices**

---

## 🎯 EXECUTIVE SUMMARY

**Problem**: Current monolithic `main.py` handles registry, authentication, agent execution, tool routing, and static file serving - creating a single point of failure and scalability bottleneck.

**Solution**: Decompose into 6 independent microservices with clear boundaries, isolated deployment, and horizontal scaling capabilities.

**Benefits**:
- **Scalability**: Each service scales independently based on load
- **Resilience**: Service failures are isolated
- **Development Velocity**: Teams can deploy services independently
- **Cost Efficiency**: Pay only for what you use (scale-to-zero for low-traffic services)

---

## 🏗️ MICROSERVICES ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                      FIREBASE HOSTING (CDN)                      │
│                     Static Assets + SPA Frontend                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     API GATEWAY (Cloud Run)                      │
│        Rate Limiting • Authentication • Request Routing          │
│                     /api/v1/* → Services                         │
└─────┬──────┬──────┬──────┬──────┬──────┬───────────────────────┘
      │      │      │      │      │      │
      ▼      ▼      ▼      ▼      ▼      ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│ REGISTRY│ │  AUTH   │ │EXECUTOR │ │  TOOL   │ │ANALYTICS│ │ VETTING │
│ SERVICE │ │ SERVICE │ │ SERVICE │ │ SERVICE │ │ SERVICE │ │ SERVICE │
└────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘
     │           │           │           │           │           │
     └───────────┴───────────┴───────────┴───────────┴───────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │   FIRESTORE DB    │
                    │  (Shared State)   │
                    └───────────────────┘
```

---

## 📦 SERVICE BREAKDOWN

### **1. API Gateway Service** (`api-gateway/`)
**Purpose**: Single entry point, authentication, rate limiting, request routing

**Responsibilities**:
- Verify Firebase ID tokens
- Enforce rate limits (Redis-backed)
- Route requests to appropriate services
- CORS handling
- Request/response transformation

**Tech Stack**: FastAPI, Redis, Cloud Run (always-on, 1 instance)

**Endpoints**:
- `POST /api/v1/agents/register` → Registry Service
- `POST /api/v1/agents/execute` → Executor Service
- `GET /api/v1/registry/search` → Registry Service
- `GET /api/v1/tools/*` → Tool Service

**Scaling**: 1-3 instances (rarely needs more)

---

### **2. Registry Service** (`registry-service/`)
**Purpose**: Agent registration, discovery, and metadata management

**Responsibilities**:
- Register new agents (write to Firestore)
- Search/filter agents
- Manage agent status (pending → vetted → active)
- Serve agent manifests
- Validate agent cards

**Tech Stack**: FastAPI, Firestore, Cloud Run (scale-to-zero)

**Database Schema**:
```
agents/{agent_id}:
  - hash_id: string
  - name: string
  - owner_uid: string
  - tools: array
  - deployment: object
  - status: 'pending-vetting' | 'vetted' | 'active' | 'suspended'
  - created_at: timestamp
  - updated_at: timestamp
```

**Endpoints**:
- `POST /register` - Register new agent
- `GET /search` - Search agents
- `GET /{agent_id}` - Get agent details
- `PATCH /{agent_id}` - Update agent (owner only)
- `DELETE /{agent_id}` - Delete agent (owner only)

**Scaling**: Scale-to-zero → 10 instances (registration spikes)

---

### **3. Auth Service** (`auth-service/`)
**Purpose**: Token management and user operations

**Responsibilities**:
- Issue custom tokens for agents
- Manage API key encryption/decryption
- User profile management
- Refresh token handling
- Admin role verification

**Tech Stack**: FastAPI, Firebase Admin SDK, Cloud KMS (key encryption)

**Endpoints**:
- `POST /token/verify` - Verify Firebase ID token
- `POST /token/custom` - Issue custom agent token
- `GET /user/profile` - Get user profile
- `PATCH /user/api-keys` - Update encrypted API keys
- `POST /admin/verify` - Verify admin role

**Scaling**: Scale-to-zero → 5 instances

---

### **4. Executor Service** (`executor-service/`)
**Purpose**: Route execution requests to agent containers

**Responsibilities**:
- Validate agent permissions
- Route to agent Cloud Run URL
- Monitor agent health
- Handle agent timeouts
- Log execution metrics

**Tech Stack**: FastAPI, aiohttp (async HTTP client), Cloud Run

**Endpoints**:
- `POST /execute` - Execute tool via agent
- `GET /health/{agent_id}` - Check agent health
- `POST /deploy` - Deploy new agent container

**Agent Container Communication**:
```
Executor Service → HTTP → Agent Container (Cloud Run)
  POST https://agent-{hash_id}-xxx.run.app/execute
  Headers: X-Agent-Auth: {hash_id}
  Body: { tool_name, payload }
```

**Scaling**: 1 instance always-on → 20 instances (high load)

---

### **5. Tool Service** (`tool-service/`)
**Purpose**: Tool registry, discovery, and Tool Factory

**Responsibilities**:
- Tool catalog management
- Tool code generation (Tool Factory)
- Tool validation
- Tool versioning
- Custom tool approval workflow

**Tech Stack**: FastAPI, Firestore, Code Generation Engine

**Endpoints**:
- `GET /catalog` - List all tools
- `GET /{tool_id}` - Get tool details
- `POST /generate` - Generate tool code (Tool Factory)
- `POST /submit` - Submit custom tool for approval
- `PATCH /{tool_id}/approve` - Approve tool (admin only)

**Scaling**: Scale-to-zero → 5 instances

---

### **6. Analytics Service** (`analytics-service/`)
**Purpose**: Metrics, logging, and monitoring

**Responsibilities**:
- Aggregate execution logs
- Cost tracking per agent
- Usage analytics
- Alert on anomalies
- Dashboard data API

**Tech Stack**: FastAPI, BigQuery, Cloud Monitoring

**Endpoints**:
- `POST /log` - Ingest execution log
- `GET /metrics/{agent_id}` - Get agent metrics
- `GET /costs` - Cost breakdown
- `GET /dashboard` - Dashboard data

**Scaling**: Scale-to-zero → 3 instances

---

### **7. Vetting Service** (`vetting-service/`)
**Purpose**: Agent approval workflow and security scanning

**Responsibilities**:
- Queue new agent submissions
- Run security scans
- Manual review interface
- Approve/reject agents
- Deploy approved agents to Cloud Run

**Tech Stack**: FastAPI, Cloud Tasks, Firestore

**Endpoints**:
- `GET /queue` - Pending agents (admin only)
- `POST /{agent_id}/approve` - Approve agent
- `POST /{agent_id}/reject` - Reject agent
- `POST /{agent_id}/scan` - Trigger security scan

**Scaling**: Scale-to-zero → 2 instances

---

## 🔐 SECURITY MODEL

### Authentication Flow
```
1. User logs in with Firebase → Gets ID token
2. Frontend sends ID token in Authorization header
3. API Gateway verifies token with Firebase
4. Gateway adds X-User-ID header to internal requests
5. Services trust Gateway's user identification
```

### Service-to-Service Auth
- All internal communication uses **IAM service accounts**
- Cloud Run services verify caller IAM identity
- No API keys between services (IAM only)

### Agent Container Auth
- Agents authenticate with **X-Agent-Auth: agent_{hash}**
- Executor Service validates hash against Firestore
- Failed auth = immediate 403, logged to Analytics

---

## 💾 DATA ARCHITECTURE

### Firestore Collections
```
/agents/{agent_id}           - Agent registry
/users/{user_id}             - User profiles
/api_keys/{user_id}          - Encrypted API keys
/tools/{tool_id}             - Tool catalog
/execution_logs/{log_id}     - Execution history
/vetting_queue/{agent_id}    - Pending approvals
/analytics/{metric_id}       - Aggregated metrics
```

### Redis (Shared State)
```
rate_limit:{user_id}         - Request counts (TTL: 60s)
agent_health:{agent_id}      - Health status (TTL: 300s)
cache:registry_search:{hash} - Search results (TTL: 600s)
```

---

## 📈 SCALING STRATEGY

| Service       | Min Instances | Max Instances | Trigger Metric     |
|---------------|---------------|---------------|--------------------|
| API Gateway   | 1             | 3             | Request count      |
| Registry      | 0             | 10            | Request latency    |
| Auth          | 0             | 5             | Token ops/min      |
| Executor      | 1             | 20            | Pending executions |
| Tool Service  | 0             | 5             | Request count      |
| Analytics     | 0             | 3             | Log ingestion rate |
| Vetting       | 0             | 2             | Queue length       |

**Auto-scaling Configuration**:
- Scale up when CPU > 70% or requests queued > 10
- Scale down after 5 minutes of low activity
- Max scale-up rate: 1 instance per 60 seconds

---

## 🚀 PHASED MIGRATION PLAN

### **Phase 1: Foundation (Week 1-2)**
**Goal**: Set up infrastructure and API Gateway

**Tasks**:
1. Create Cloud Run services (empty stubs)
2. Set up Firestore collections with security rules
3. Deploy Redis instance (Memorystore)
4. Implement API Gateway with routing
5. Migrate static files to Firebase Hosting

**Deliverables**:
- API Gateway routing requests
- Firebase Hosting serving frontend
- Firestore security rules deployed

**Validation**:
- Curl API Gateway → Returns 503 (services not ready)
- Frontend loads from Firebase Hosting

---

### **Phase 2: Core Services (Week 3-4)**
**Goal**: Migrate Registry and Auth services

**Tasks**:
1. Extract Registry logic from main.py → registry-service/
2. Extract Auth logic → auth-service/
3. Deploy both services to Cloud Run
4. Update API Gateway routing
5. Migrate database operations to Firestore

**Deliverables**:
- Registry Service: Agent registration working
- Auth Service: Token validation working
- Firestore as primary database

**Validation**:
- Register agent via API Gateway → Success
- Search agents → Returns results from Firestore
- Invalid token → 401 response

---

### **Phase 3: Execution Pipeline (Week 5-6)**
**Goal**: Migrate agent execution logic

**Tasks**:
1. Create Executor Service
2. Migrate agent_runner.py to individual agent containers
3. Implement agent health checks
4. Set up execution logging
5. Deploy Genesis and QuantFlow to isolated containers

**Deliverables**:
- Executor Service routing to agent containers
- Genesis agent executing in isolated container
- QuantFlow agent executing in isolated container

**Validation**:
- Execute tool via Genesis → Success
- Execution logged to Analytics
- Agent health check → Returns healthy status

---

### **Phase 4: Tools & Analytics (Week 7-8)**
**Goal**: Complete tool ecosystem and monitoring

**Tasks**:
1. Create Tool Service
2. Migrate Tool Factory logic
3. Create Analytics Service
4. Set up BigQuery for log aggregation
5. Build dashboard API

**Deliverables**:
- Tool Service: Catalog and Tool Factory working
- Analytics Service: Metrics API working
- BigQuery ingesting execution logs

**Validation**:
- Generate tool via Tool Factory → Success
- Query agent metrics → Returns usage data
- Dashboard displays live metrics

---

### **Phase 5: Vetting & Polish (Week 9-10)**
**Goal**: Complete vetting workflow and optimize

**Tasks**:
1. Create Vetting Service
2. Build admin approval interface
3. Implement security scanning
4. Optimize service performance
5. Load testing and tuning

**Deliverables**:
- Vetting Service: Approval workflow working
- Admin interface for agent approval
- Performance benchmarks documented

**Validation**:
- Submit agent → Appears in vetting queue
- Admin approves → Agent deployed to Cloud Run
- Load test: 1000 req/min → All services stable

---

## 💰 COST ANALYSIS

### Current Monolith
- 1 Cloud Run service: 1GB RAM, always-on
- Cost: ~$50/month (idle) + $150/month (moderate load) = **$200/month**

### Microservices (Projected)
| Service       | Cost (Idle) | Cost (Moderate) | Cost (High Load) |
|---------------|-------------|-----------------|------------------|
| API Gateway   | $20         | $40             | $80              |
| Registry      | $0          | $20             | $50              |
| Auth          | $0          | $15             | $30              |
| Executor      | $15         | $60             | $150             |
| Tool Service  | $0          | $10             | $25              |
| Analytics     | $0          | $20             | $40              |
| Vetting       | $0          | $5              | $10              |
| Redis         | $30         | $30             | $30              |
| **TOTAL**     | **$65**     | **$200**        | **$415**         |

**Key Insight**: At moderate load, cost is similar, but microservices provide:
- 10x better scalability
- Independent deployment
- Isolated failures
- Scale-to-zero savings during low traffic

---

## 🎯 SUCCESS METRICS

### Performance
- ✅ API Gateway latency: < 50ms (p95)
- ✅ Service-to-service latency: < 100ms (p95)
- ✅ End-to-end execution: < 3s (p95)
- ✅ Scale-up time: < 60s

### Reliability
- ✅ Service uptime: 99.9% per service
- ✅ Data consistency: 100% (Firestore ACID)
- ✅ Failed request rate: < 0.1%

### Scalability
- ✅ Support 1000 concurrent users
- ✅ Handle 10,000 executions/hour
- ✅ Zero-downtime deployments

---

## 🔧 IMPLEMENTATION NOTES

### Service Template Structure
```
service-name/
├── main.py              # FastAPI app
├── models.py            # Pydantic models
├── routes.py            # Endpoint handlers
├── dependencies.py      # FastAPI dependencies
├── database.py          # Firestore operations
├── Dockerfile           # Container image
├── requirements.txt     # Python deps
└── cloudbuild.yaml      # CI/CD config
```

### Deployment Command (per service)
```bash
gcloud run deploy SERVICE_NAME \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated=false \
  --min-instances 0 \
  --max-instances 10 \
  --memory 512Mi \
  --cpu 1 \
  --concurrency 80 \
  --set-env-vars PROJECT_ID=censaisystems
```

---

## 📋 MIGRATION CHECKLIST

**Pre-Migration**:
- [ ] Back up registry.db.json
- [ ] Export all agent data
- [ ] Document current API endpoints
- [ ] Set up staging environment

**Phase 1** (Infrastructure):
- [ ] Create Cloud Run services (stubs)
- [ ] Deploy Firestore security rules
- [ ] Set up Redis instance
- [ ] Deploy API Gateway
- [ ] Migrate static files to Firebase Hosting

**Phase 2** (Core Services):
- [ ] Deploy Registry Service
- [ ] Deploy Auth Service
- [ ] Migrate data to Firestore
- [ ] Update API Gateway routing
- [ ] Test registration flow

**Phase 3** (Execution):
- [ ] Deploy Executor Service
- [ ] Containerize agent_runner.py
- [ ] Deploy Genesis agent
- [ ] Deploy QuantFlow agent
- [ ] Test execution flow

**Phase 4** (Tools & Analytics):
- [ ] Deploy Tool Service
- [ ] Deploy Analytics Service
- [ ] Set up BigQuery
- [ ] Migrate Tool Factory
- [ ] Test analytics pipeline

**Phase 5** (Vetting & Launch):
- [ ] Deploy Vetting Service
- [ ] Build admin interface
- [ ] Load testing
- [ ] Performance optimization
- [ ] Production launch

**Post-Migration**:
- [ ] Monitor all services for 7 days
- [ ] Optimize scaling parameters
- [ ] Update documentation
- [ ] Decommission monolith

---

## 🚨 ROLLBACK PLAN

If any phase fails critically:

1. **Immediate**: Route traffic back to monolithic main.py
2. **Short-term**: Identify failed service, roll back to previous version
3. **Long-term**: Fix issue in staging, test, redeploy

**Rollback Trigger**: 
- Error rate > 5% for 5 minutes
- Manual trigger by ops team

---

## 📞 SUPPORT & ESCALATION

**Architecture Questions**: Review ARCHITECTURE_REVIEW.md  
**Security Issues**: Review firestore.rules and auth_validator.py  
**Deployment Help**: Follow phased migration plan above

---

**Document Status**: ✅ Ready for Review  
**Last Updated**: October 11, 2025  
**Next Review**: After Phase 1 completion
