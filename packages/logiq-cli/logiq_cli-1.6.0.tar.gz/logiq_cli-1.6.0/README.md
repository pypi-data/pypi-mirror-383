# LogiIQ CLI Tool v1.6.0

[![PyPI version](https://badge.fury.io/py/logiq-cli.svg)](https://badge.fury.io/py/logiq-cli)
[![Downloads](https://pepy.tech/badge/logiq-cli)](https://pepy.tech/project/logiq-cli)
[![Downloads](https://pepy.tech/badge/logiq-cli/month)](https://pepy.tech/project/logiq-cli)
[![Downloads](https://pepy.tech/badge/logiq-cli/week)](https://pepy.tech/project/logiq-cli)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

LogiIQ is an advanced automated log analysis client with AI-powered threat detection, dynamic monitoring capabilities, and enhanced security features.

## 🚀 New in v1.6.0

- **Enhanced Cleanup Mechanism**: Improved event loop handling and cleanup process for graceful CLI exit
- **Better Error Handling**: Enhanced error handling for shutdown scenarios and interpreter shutdown
- **Robust Status Updates**: More reliable status update mechanism during CLI exit
- **Download Metrics**: Added comprehensive download badges and metrics to project documentation
- **Cleaner Exit Process**: Resolved cleanup warnings and event loop conflicts

## 🔧 Previous Features (v1.5.0)

- **Real-time CLI Status Updates**: CLI tool now properly updates user status to active/inactive on the frontend dashboard
- **Enhanced Authentication Flow**: Improved credential loading and username configuration for better status tracking
- **Automatic Status Management**: CLI status automatically updates when monitoring starts and stops
- **Better Dashboard Integration**: Frontend dashboard shows real-time CLI status with visual indicators
- **Improved Error Handling**: Enhanced error handling for authentication and status update failures

## 🔧 Previous Features (v1.4.0)

- **Critical Bug Fix**: Fixed Pre-RAG classifier issue that was causing all logs to be classified as threats
- **Model Quality Validation**: Automatic detection and fallback when ML models perform poorly
- **Improved Accuracy**: Dramatically reduced false positive rate in threat detection
- **Better Performance**: Enhanced classification speed and reliability
- **Robust Error Handling**: More reliable system with better fallback mechanisms

## 🔧 Previous Features (v1.3.0)

- **Enhanced Threat Detection**: Improved ML models with better accuracy and performance
- **Advanced Thread Modeling**: Optimized threat detection with thread-based processing
- **Enhanced Security**: Stronger encryption using password-based authentication
- **Comprehensive ML Suite**: Advanced threat classification and cost-sensitive training
- **Improved User Experience**: Better CLI interface and error handling

## Features

- **Real-time CLI Status Tracking**: Dashboard integration showing live CLI activity status
- AI agent integration for enhanced analysis with ML-powered threat detection
- Real-time log monitoring with MongoDB storage
- Secure authentication and encrypted credential storage
- Dynamic log extraction and analysis
- Advanced threat modeling and classification
- Cost-sensitive machine learning algorithms
- Comprehensive Scripts module with pre-trained models
- **Enhanced Dashboard Integration**: Visual status indicators for CLI tool activity

## Installation

```bash
pip install logiq-cli
```

## Usage

```bash
# Authentication
logiq auth login --username <username>

# Setup monitoring profile
logiq profile setup --log-path <path> --interval <seconds>

# Start monitoring (status will update on dashboard)
logiq monitor --start

# Start dynamic monitoring with real-time status updates
logiq monitor --dynamic --interval 300
```

## CLI Status Dashboard Integration

The CLI tool now provides real-time status updates to the dashboard:

- **ACTIVE** 🖥️: CLI monitoring is running
- **INACTIVE** 💤: CLI monitoring is stopped
- **Real-time Updates**: Status changes automatically when monitoring starts/stops
- **Visual Indicators**: Clear color-coded status display on the dashboard

## License

MIT License
