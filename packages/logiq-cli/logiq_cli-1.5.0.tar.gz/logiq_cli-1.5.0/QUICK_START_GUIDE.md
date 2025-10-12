# ForensIQ Dynamic Log Monitoring - Quick Start Guide

## Overview

The ForensIQ CLI tool now supports **Dynamic Log Extraction** that automatically gathers logs from various system sources without requiring static log files. This is perfect for real-time security monitoring.

## 🚀 Quick Setup (Dynamic Mode)

### Step 1: Authentication
```bash
# Use correct command syntax: auth login (not just login)
python cli_tool.py auth login --username vaibhav

# Register new user if needed
python cli_tool.py auth register --username vaibhav --email vaibhav@company.com

# Check your profile
python cli_tool.py auth profile
```

### Step 2: Check Available Log Sources
```bash
# See what log sources are available on your system
python cli_tool.py profile setup-dynamic --list-sources
```

Example output on Windows:
```
📋 Available Log Sources:
  • security_events: Windows Security Events (windows_eventlog)
  • system_events: Windows System Events (windows_eventlog)
  • application_events: Windows Application Events (windows_eventlog)
  • process_monitor: Running processes and new process creation (process_monitor)
  • network_connections: Active network connections (network_monitor)
  • file_system_activity: File system changes (filesystem_monitor)
```

### Step 3: Setup Dynamic Monitoring Profile
```bash
# Setup with all available sources (recommended)
python cli_tool.py profile setup-dynamic --interval 300

# Or setup with specific sources
python cli_tool.py profile setup-dynamic --sources security_events process_monitor --interval 300

# Check profile status
python cli_tool.py profile status
```

### Step 4: Start Dynamic Monitoring
```bash
# Start dynamic monitoring (extracts logs every 5 minutes and sends to MongoDB)
python cli_tool.py monitor --dynamic

# Or start with custom interval
python cli_tool.py monitor --dynamic --interval 300
```

## 📊 What You'll See

When monitoring starts, you'll see real-time updates like:
```
🚀 Starting dynamic system log monitoring...
📊 Logs will be extracted from system sources every 5 minutes
🔄 Data will be automatically sent to ForensIQ and stored in MongoDB
🤖 AI Agent will provide enhanced analysis and adaptive scheduling

🔍 Dynamic Analysis Complete [14:25:30]
  Extracted: 45 log entries
  Sources: security_events, process_monitor
  MITRE Techniques: 3
    - T1059.001: PowerShell (Score: 0.85)
    - T1078: Valid Accounts (Score: 0.72)
    - T1055: Process Injection (Score: 0.68)
  AI Agent: Adjusted interval to 120s based on medium threat level

⏳ Next extraction in 120 seconds...
```
# Start automated monitoring (sends logs every 5 minutes to MongoDB)
python cli_tool.py monitor --start
```

## 📋 Available Commands

### Authentication Commands
```bash
# User registration
python cli_tool.py auth register --username <username> --email <email>

# User login  
python cli_tool.py auth login --username <username> [--api-url <url>]

# Get user profile
python cli_tool.py auth profile
```

### Profile Management Commands
```bash
# Setup monitoring profile
python cli_tool.py profile setup --log-path <path> --interval <seconds> [--max-results <num>] [--no-enhance] [--no-ai-agent]

# Check profile status
python cli_tool.py profile status

# Update profile settings
python cli_tool.py profile update [--interval <seconds>] [--max-results <num>] [--enable-ai] [--disable-ai] [--enable-agent] [--disable-agent]
```

### Log Analysis Commands
```bash
# Send single log file for analysis
python cli_tool.py send --file <log_file> [--no-enhance]

# Enhanced analysis with AI agent
python cli_tool.py analyze --file <log_file> --enhanced [--ai-agent] [--output <file>]
```

### Monitoring Commands
```bash
# Start automated monitoring (5-minute intervals + MongoDB storage)
python cli_tool.py monitor --start

# Start scheduled analysis
python cli_tool.py monitor --schedule
```

### AI Agent Commands
```bash
# Check AI agent status
python cli_tool.py agent status

# Configure AI agent
python cli_tool.py agent configure [--enable] [--disable] [--learning-threshold <num>] [--high-threat-interval <seconds>]

# Reset AI agent learning data
python cli_tool.py agent reset --confirm
```

## 🎯 Key Features

### ✅ Automated 5-Minute Log Processing
- **Continuous Monitoring**: Automatically reads new log entries every 5 minutes
- **MongoDB Storage**: All analysis results stored in your MongoDB database
- **AI Enhancement**: Each analysis enhanced with AI agent intelligence
- **Adaptive Scheduling**: Intervals adjust based on threat levels

### ✅ Complete Server Integration
- **Authentication**: Full JWT token-based authentication with your FastAPI server
- **API Integration**: Direct integration with your `/api/v1/analyze` endpoint
- **Database Storage**: Results stored in `analysis_collection` and `monitoring_collection`
- **Session Tracking**: Monitoring sessions tracked in database

### ✅ AI Agent Intelligence
- **Pattern Learning**: Learns from log patterns to improve accuracy
- **Threat Assessment**: Provides severity scoring and confidence metrics
- **Adaptive Intervals**: Adjusts monitoring frequency based on threat levels
- **Enhanced Analysis**: Contextual analysis beyond basic MITRE matching

## 🗄️ Database Schema

### Analysis Collection (`log_analysis`)
```json
{
  "analysis_id": "abc123",
  "session_id": "session456", 
  "username": "vaibhav",
  "log_content_hash": "sha256hash",
  "log_file_path": "/path/to/logs",
  "summary": "AI-generated summary",
  "matched_techniques": [...],
  "ai_agent_analysis": {...},
  "created_at": "2025-08-29T13:30:00Z"
}
```

### Monitoring Sessions (`monitoring_sessions`)
```json
{
  "session_id": "session456",
  "username": "vaibhav", 
  "log_path": "/path/to/logs",
  "start_time": "2025-08-29T13:25:00Z",
  "status": "active",
  "interval_seconds": 300,
  "total_analyses": 15,
  "ai_agent_enabled": true
}
```

## 🔥 Real-World Example

```bash
# 1. First-time setup
python cli_tool.py auth register --username security_analyst --email analyst@company.com
python cli_tool.py auth login --username security_analyst

# 2. Configure monitoring for Windows Security logs
python cli_tool.py profile setup --log-path "C:\Windows\System32\winevt\Logs\Security.evtx" --interval 300

# 3. Start automated monitoring
python cli_tool.py monitor --start
```

**What happens:**
1. ✅ Authenticates with your ForensIQ server
2. ✅ Creates monitoring session in MongoDB
3. ✅ Every 5 minutes: reads new log entries
4. ✅ Sends logs to `/api/v1/analyze` endpoint 
5. ✅ AI agent enhances analysis with threat intelligence
6. ✅ Stores complete results in MongoDB
7. ✅ Adjusts intervals based on threat levels
8. ✅ Continues until stopped (Ctrl+C)

## 📊 Monitoring Dashboard

Check your MongoDB collections to see:
- **Real-time analysis results** in `log_analysis` collection
- **Active monitoring sessions** in `monitoring_sessions` collection 
- **AI agent learning patterns** stored persistently
- **Complete audit trail** of all security events

## 🛠️ Troubleshooting

### Common Issues & Solutions

**"Invalid choice: 'login'"**
```bash
# ❌ Wrong: python cli_tool.py login --username vaibhav
# ✅ Correct: python cli_tool.py auth login --username vaibhav
```

**"No valid credentials found"**
```bash
# First login with your credentials
python cli_tool.py auth login --username your_username
```

**"Log file not found"**
```bash
# Check the file path exists and is readable
python cli_tool.py profile setup --log-path "C:\full\path\to\logs.txt" --interval 300
```

**"Failed to create monitoring session"**
```bash
# Ensure you're authenticated and server is running
python cli_tool.py auth login --username your_username --api-url http://localhost:8000
```

## 🎯 Production Tips

1. **Start with authentication**: Always `auth login` first
2. **Use absolute paths**: Provide full paths to log files
3. **Monitor server logs**: Check FastAPI server logs for debugging
4. **Check MongoDB**: Verify data is being stored in collections
5. **AI agent warmup**: Let AI agent learn patterns for better accuracy

---

**🚀 Your CLI tool is now ready for automated 5-minute log processing with MongoDB storage!**
