# ForensIQ Dynamic Monitoring - Complete Setup Guide

## 🚀 Dynamic Log Extraction Every 5 Minutes with MongoDB Storage

This guide shows you how to set up automated log extraction from your Windows system that sends data to your ForensIQ server every 5 minutes and stores it in MongoDB.

## 📋 Prerequisites

1. **ForensIQ Server Running**: Make sure your FastAPI server is running on `http://localhost:8000`
2. **MongoDB Connection**: Ensure MongoDB is configured in your server
3. **User Account**: You need a registered user account

## 🔧 Step-by-Step Setup

### Step 1: Start Your ForensIQ Server
```bash
cd d:\forensiq\server
python main.py
```

### Step 2: Authenticate with the CLI Tool
```bash
cd d:\forensiq\aiagent

# Login to your account
python cli_tool.py auth login --username vaibhav

# Or register a new account if needed
python cli_tool.py auth register --username vaibhav --email vaibhav@example.com
```

### Step 3: Check Available Log Sources
```bash
# List all available dynamic log sources on your system
python cli_tool.py profile setup-dynamic --list-sources
```

**Available Sources:**
- `security_events`: Windows Security Events
- `system_events`: Windows System Events  
- `application_events`: Windows Application Events
- `powershell_logs`: PowerShell Execution Logs
- `process_monitor`: Running processes and new process creation
- `network_connections`: Active network connections
- `file_system_activity`: File system changes

### Step 4: Setup Dynamic Monitoring Profile
```bash
# Setup monitoring with specific log sources and 5-minute intervals
python cli_tool.py profile setup-dynamic \
  --sources security_events,system_events,process_monitor \
  --interval 300 \
  --enable-ai-agent \
  --auto-enhance
```

### Step 5: Start Automated Monitoring
```bash
# Start continuous monitoring (runs every 5 minutes)
python cli_tool.py monitor --start-dynamic

# Or start with specific session name for tracking
python cli_tool.py monitor --start-dynamic --session-id security_monitoring_1
```

## 🔄 What Happens Every 5 Minutes

1. **Dynamic Log Extraction**: 
   - Extracts real-time logs from Windows Event Logs
   - Monitors process creation/termination
   - Captures network connections
   - Tracks file system changes

2. **AI Analysis**:
   - Sends extracted logs to `/api/v1/analyze` endpoint
   - AI agent provides enhanced threat analysis
   - Matches against MITRE ATT&CK techniques

3. **MongoDB Storage**:
   - Stores analysis results in `analysis_results` collection
   - Maintains monitoring session data in `monitoring_sessions` collection
   - Tracks user activity and patterns

## 📊 Monitoring Commands

### Check Monitoring Status
```bash
# View current monitoring status
python cli_tool.py monitor --status

# View detailed profile information
python cli_tool.py profile status
```

### View Recent Analysis Results
```bash
# Show last 5 analysis results
python cli_tool.py monitor --show-results --limit 5

# Export results to file
python cli_tool.py monitor --export-results --output monitoring_results.json
```

### AI Agent Management
```bash
# Check AI agent status and learned patterns
python cli_tool.py agent status

# Configure AI agent for high-security monitoring
python cli_tool.py agent configure --learning-threshold 3 --high-threat-interval 60
```

## 🗄️ MongoDB Data Structure

### Analysis Results Collection
```json
{
  "_id": "analysis_20250829_155523",
  "session_id": "security_monitoring_1", 
  "user": "vaibhav",
  "timestamp": "2025-08-29T15:55:23Z",
  "log_sources": ["security_events", "system_events", "process_monitor"],
  "analysis_data": {
    "summary": "AI-generated summary of detected events",
    "matched_techniques": [
      {
        "technique_id": "T1078",
        "name": "Valid Accounts",
        "relevance_score": 0.85
      }
    ],
    "ai_agent_analysis": {
      "threat_level": "medium",
      "confidence_score": 0.78,
      "recommendations": ["Monitor failed logins", "Review process execution"]
    }
  }
}
```

### Monitoring Sessions Collection
```json
{
  "_id": "security_monitoring_1",
  "user": "vaibhav",
  "started_at": "2025-08-29T15:50:00Z",
  "status": "active",
  "interval_seconds": 300,
  "log_sources": ["security_events", "system_events", "process_monitor"],
  "total_cycles": 48,
  "successful_analyses": 47,
  "last_analysis": "2025-08-29T19:50:00Z"
}
```

## ⚙️ Configuration Options

### Update Monitoring Settings
```bash
# Change interval to 2 minutes for high-security environments
python cli_tool.py profile update --interval 120

# Add more log sources
python cli_tool.py profile setup-dynamic \
  --sources security_events,system_events,process_monitor,network_connections \
  --interval 300

# Enable/disable AI agent
python cli_tool.py profile update --enable-agent
python cli_tool.py profile update --disable-agent
```

### Advanced AI Configuration
```bash
# Configure for high-security environment
python cli_tool.py agent configure \
  --learning-threshold 2 \
  --high-threat-interval 30 \
  --medium-threat-interval 120 \
  --low-threat-interval 300
```

## 🛡️ Security Considerations

1. **Administrative Privileges**: Some log sources require administrator privileges
2. **Network Access**: Ensure firewall allows connection to ForensIQ server
3. **Data Privacy**: Logs may contain sensitive system information
4. **Storage Space**: MongoDB will grow with continuous monitoring data

## 🔍 Troubleshooting

### Common Issues and Solutions

**Authentication Failed**:
```bash
# Clear credentials and re-authenticate
python cli_tool.py auth login --username vaibhav --api-url http://localhost:8000
```

**Log Source Access Denied**:
```bash
# Run CLI as Administrator for Windows Event Logs
# Right-click Command Prompt -> "Run as Administrator"
```

**Server Connection Issues**:
```bash
# Check server status
curl http://localhost:8000/health

# Verify server is running
netstat -an | findstr :8000
```

**MongoDB Storage Issues**:
```bash
# Check MongoDB connection in server logs
# Verify MONGO_URL in server .env file
```

## 📈 Monitoring Dashboard

After data collection starts, you can:

1. **View Analysis Results**: Check MongoDB `analysis_results` collection
2. **Track Patterns**: AI agent learns and adapts to your environment
3. **Export Data**: Use CLI export commands for external analysis
4. **Generate Reports**: Create security reports from stored data

## 🚦 Quick Start Commands

```bash
# Complete setup in one go (after server is running)
cd d:\forensiq\aiagent

# 1. Authenticate
python cli_tool.py auth login --username vaibhav

# 2. Setup dynamic monitoring
python cli_tool.py profile setup-dynamic --sources security_events,system_events,process_monitor --interval 300

# 3. Start monitoring
python cli_tool.py monitor --start-dynamic

# 4. Check status (in another terminal)
python cli_tool.py monitor --status
```

## 🎯 Expected Results

Once running, you'll see:
- New analysis results in MongoDB every 5 minutes
- AI agent learning from your system's patterns
- Automatic threat detection and MITRE technique matching
- Continuous security monitoring with minimal manual intervention

The system is designed to run 24/7, providing continuous security monitoring of your Windows system with intelligent analysis and automated storage in MongoDB.
