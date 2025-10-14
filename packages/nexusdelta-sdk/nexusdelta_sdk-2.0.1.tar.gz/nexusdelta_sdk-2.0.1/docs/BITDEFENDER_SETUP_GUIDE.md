# MANUAL Bitdefender Configuration Guide for Nexus Delta
# Follow these steps carefully - requires Administrator access

## 🚨 IMPORTANT: Run Everything as Administrator
# Right-click PowerShell → "Run as administrator" for all commands

## Step 1: Configure Windows Firewall (Command Line)

# Open PowerShell as Administrator and run these commands:

# 1. Allow Agent Ports (8081-8130)
New-NetFirewallRule -DisplayName "Nexus Delta Agents" -Direction Inbound -Protocol TCP -LocalPort 8081-8130 -Action Allow -Profile Any

# 2. Allow Core Services (8080, 8090)
New-NetFirewallRule -DisplayName "Nexus Delta Core" -Direction Inbound -Protocol TCP -LocalPort 8080,8090 -Action Allow -Profile Any

# 3. Allow Inter-Machine Communication (change subnet to match your network)
New-NetFirewallRule -DisplayName "Nexus Delta Network" -Direction Inbound -RemoteAddress 192.168.1.0/24 -Action Allow -Profile Private

## Step 2: Configure Bitdefender Interface

### Open Bitdefender:
1. Click Bitdefender icon in system tray
2. Go to **Protection** → **Firewall**
3. Click **"Settings"** (gear icon)

### Add Custom Rules:

#### Rule 1: Agent Communications
- **Rule Name**: Nexus Delta Agents
- **Direction**: Both (Inbound/Outbound)
- **Action**: Allow
- **Protocol**: TCP
- **Local Ports**: 8081-8130
- **Remote Ports**: Any
- **Network Types**: All networks
- **Applications**: All applications

#### Rule 2: Core Services
- **Rule Name**: Nexus Delta Core Services
- **Direction**: Both
- **Action**: Allow
- **Protocol**: TCP
- **Local Ports**: 8080,8090
- **Network Types**: All networks

#### Rule 3: Docker Communications
- **Rule Name**: Docker Nexus Delta
- **Direction**: Both
- **Action**: Allow
- **Applications**: C:\Program Files\Docker\Docker\resources\bin\dockerd.exe
- **Network Types**: All networks

## Step 3: Add Exclusions

### In Bitdefender Main Interface:
1. Go to **Protection** → **Antivirus**
2. Click **"Settings"** → **"Manage Exceptions"**
3. Add these exclusions:

```
C:\homebase-db\Nexus-Delta\
C:\Program Files\Docker\
C:\ProgramData\Docker\
C:\Users\*\AppData\Local\Docker\
C:\Users\*\AppData\Roaming\Docker\
```

## Step 4: Test Configuration

### Run the connectivity test:
```powershell
python test-connectivity.py
```

### Expected Results:
- ✅ Bitdefender detected and running
- ✅ Core services (API Gateway, Registry, Auth) should work
- ⚠️ Agent ports (8081+) may show "blocked" (normal - no agents running yet)

## Step 5: Laptop Configuration

### On your laptop, repeat Steps 1-4, but:
- Change the subnet rule to allow your main machine's IP
- Example: `-RemoteAddress 192.168.1.100` (use your main machine's IP)

## Troubleshooting

### If tests still fail:
1. **Check Bitdefender Logs**: Protection → Firewall → View Logs
2. **Disable Bitdefender Temporarily**: For testing only!
3. **Verify Ports**: Use `netstat -an | find "8080"` to check if services are listening
4. **Check Windows Firewall**: May need separate configuration

### Common Issues:
- **"Access Denied"**: Not running as Administrator
- **"Invalid Path"**: Use exact paths, no wildcards
- **"Port Already in Use"**: Normal if services are running

## Verification Commands

```powershell
# Check firewall rules
Get-NetFirewallRule | Where-Object DisplayName -like "*Nexus*"

# Test specific port
Test-NetConnection -ComputerName localhost -Port 8080

# Check Bitdefender service
Get-Service | Where-Object Name -like "*bitdefender*"
```

## Next Steps After Configuration

1. **Test connectivity**: `python test-connectivity.py`
2. **Start agents**: `python agent_manager.py start-all`
3. **Test multi-host**: Configure laptop agents
4. **Monitor**: Check Bitdefender logs for blocked attempts

---
**Remember**: Bitdefender is protecting you - these rules are specifically for your development environment. In production, use more restrictive rules!