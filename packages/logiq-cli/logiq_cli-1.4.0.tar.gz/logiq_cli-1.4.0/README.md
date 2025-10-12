# LogiIQ CLI Tool v1.4.0

LogiIQ is an advanced automated log analysis client with AI-powered threat detection, dynamic monitoring capabilities, and enhanced security features.

## 🚀 New in v1.4.0

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

- AI agent integration for enhanced analysis with ML-powered threat detection
- Real-time log monitoring with MongoDB storage
- Secure authentication and encrypted credential storage
- Dynamic log extraction and analysis
- Advanced threat modeling and classification
- Cost-sensitive machine learning algorithms
- Comprehensive Scripts module with pre-trained models

## Installation

```bash
pip install logiq-cli
```

## Usage

```bash
logiq auth login --username <username>
logiq profile setup --log-path <path> --interval <seconds>
logiq monitor --start
```

## License

MIT License
