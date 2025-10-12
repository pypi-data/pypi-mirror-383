# Changelog

All notable changes to the LogIQ CLI Tool will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2024-12-19

### Fixed
- **Critical Bug Fix**: Fixed Pre-RAG classifier issue causing all logs to be classified as threats
- **Model Quality Check**: Added automatic detection of poor ML model performance
- **Intelligent Fallback**: Improved rule-based classification fallback when ML model fails
- **Conservative Filtering**: Changed default behavior to filter uncertain logs instead of sending to RAG
- **Cache Management**: Fixed Redis cache issues affecting classification results

### Improved
- **Threat Detection Accuracy**: Dramatically reduced false positive rate in log filtering
- **Performance**: Better classification performance with quality checks
- **Reliability**: More robust error handling in classifier initialization
- **Pattern Matching**: Enhanced threat and benign pattern recognition

### Technical Improvements
- Added model quality validation to prevent identical predictions
- Improved rule-based classification with better default behavior
- Enhanced logging and debugging information for classifier issues
- Better error handling and fallback mechanisms

## [1.3.0] - 2024-12-19

### Added
- Enhanced threat detection model with improved accuracy
- Thread-based threat modeling for better performance
- Advanced CLI tool integration with frontend capabilities
- Improved encryption/decryption security using password-based authentication
- Enhanced user management and authentication system
- Comprehensive Scripts module with machine learning models
- Advanced threat detection and classification algorithms
- Cost-sensitive training and evaluation capabilities

### Changed
- Updated package structure for better modularity
- Improved CLI command interface and user experience
- Enhanced security with stronger encryption methods
- Optimized threat detection algorithms for better performance

### Fixed
- Resolved authentication issues with user ID-based encryption
- Fixed thread model implementation for stable operation
- Improved error handling and logging throughout the application

### Technical Improvements
- Added comprehensive machine learning models in Scripts/models/
- Enhanced threat detection with multiple classification approaches
- Improved data preprocessing and feature extraction
- Better integration between CLI tool and server components

## [1.1.2] - Previous Release

### Features
- Basic CLI tool functionality
- MongoDB integration
- AI agent capabilities
- Authentication system
- Real-time monitoring

## [1.0.0] - Initial Release

### Features
- Initial LogIQ CLI tool release
- Basic log analysis capabilities
- MongoDB storage integration
- Authentication and user management
