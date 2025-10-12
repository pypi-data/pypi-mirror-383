# Changelog

All notable changes to the LogIQ CLI Tool will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.8.0] - 2025-10-12

### Changed

- Reduced default logging noise during startup; ML fallback diagnostics moved to DEBUG
- Minor stability improvements in model initialization paths

### Docs

- Updated README to 1.8.0 with quieter logs note
- Added `RELEASE_NOTES_v1.8.0.md`

## [1.7.0] - 2025-10-12

### Added
- CLI UX polish and help improvements, clearer messages and exit codes
- Minor performance improvements in status update paths
- Documentation refresh for 1.7 including quick commands and screenshots placeholders

### Fixed
- Addressed intermittent Windows-specific cleanup edge cases
- Small typos and links in documentation

### Improved
- More resilient shutdown flow when Ctrl+C/terminal close occurs
- Streamlined dependency versions, validated against Python 3.12

## [1.6.0] - 2025-01-12

### Added
- **Enhanced Cleanup Mechanism**: Improved event loop handling and cleanup process for graceful CLI exit
- **Better Error Handling**: Enhanced error handling for shutdown scenarios and interpreter shutdown
- **Robust Status Updates**: More reliable status update mechanism during CLI exit
- **Download Metrics**: Added comprehensive download badges and metrics to project documentation

### Fixed
- **Cleanup Warnings**: Fixed "Cannot run the event loop while another loop is running" warnings
- **Event Loop Conflicts**: Resolved event loop conflicts during cleanup process
- **Shutdown Errors**: Improved handling of interpreter shutdown scenarios
- **Coroutine Warnings**: Fixed "coroutine was never awaited" warnings during cleanup

### Improved
- **Graceful Exit**: More robust cleanup process that handles various exit scenarios
- **Error Resilience**: Better error handling that doesn't disrupt normal CLI operation
- **User Experience**: Cleaner exit process without warning messages
- **Code Quality**: Improved code structure and error handling patterns

### Technical Improvements
- Enhanced `cleanup_handler()` function with better event loop management
- Improved `cleanup_cli_status()` method with graceful error handling
- Better `_update_cli_status()` method with shutdown scenario detection
- Added comprehensive download metrics and project badges

## [1.5.0] - 2025-01-12

### Added
- **Real-time CLI Status Updates**: CLI tool now properly updates user status to active/inactive on the frontend dashboard
- **Enhanced Authentication Flow**: Improved credential loading and username configuration for better status tracking
- **Automatic Status Management**: CLI status automatically updates when monitoring starts and stops
- **Better Error Handling**: Enhanced error handling for authentication and status update failures

### Fixed
- **Critical Authentication Bug**: Fixed issue where CLI status wasn't updating due to missing username configuration
- **Status Update Reliability**: Resolved problems with CLI status not changing to active when monitoring starts
- **Credential Loading**: Fixed username not being set in config after loading stored credentials
- **Cleanup Handling**: Improved cleanup mechanisms to ensure status is set to inactive when CLI exits

### Improved
- **User Experience**: Frontend dashboard now shows real-time CLI status (ACTIVE/INACTIVE)
- **Monitoring Integration**: Better integration between CLI monitoring and dashboard status display
- **Authentication Persistence**: More reliable authentication state management across CLI sessions
- **Status Synchronization**: Improved synchronization between CLI tool and server for user status

### Technical Improvements
- Enhanced `_load_stored_token()` method to properly set username in config
- Improved `_load_credentials()` method for better credential management
- Added comprehensive status update calls in all monitoring KeyboardInterrupt handlers
- Better error handling and logging for status update operations

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
