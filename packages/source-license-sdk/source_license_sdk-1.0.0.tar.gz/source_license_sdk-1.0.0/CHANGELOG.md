# Changelog

All notable changes to the Source-License Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-10

### Added
- Initial release of Source-License Python SDK
- License validation functionality
- License activation functionality  
- License enforcement with automatic exit on failure
- Cross-platform machine identifier generation
- Comprehensive error handling with specific exception types
- Rate limiting support with retry information
- SSL/TLS support with optional verification
- Zero-dependency implementation (uses only Python standard library)
- Optional psutil integration for enhanced machine identification
- Comprehensive documentation with examples
- Support for Python 3.7+
- Django, Flask, and command-line integration examples
- Diagnostic and troubleshooting tools
- Complete test suite

### Features
- **Simple API**: Easy-to-use methods for license validation and activation
- **Machine Fingerprinting**: Automatic generation of unique machine identifiers
- **Network Resilience**: Built-in error handling and retry logic
- **Security**: Secure communication with HTTPS support
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Framework Integration**: Ready-to-use examples for popular Python frameworks

### Configuration Options
- Server URL configuration
- License key management
- Machine ID customization
- Timeout settings
- SSL verification control
- Custom User-Agent headers

### Exception Types
- `SourceLicenseError` - Base exception
- `ConfigurationError` - Configuration issues
- `NetworkError` - Network/HTTP errors
- `LicenseError` - License validation errors
- `RateLimitError` - API rate limiting
- `LicenseNotFoundError` - License not found
- `LicenseExpiredError` - License expired
- `ActivationError` - Activation failures
- `MachineError` - Machine identification errors

### Methods
- `setup()` - Quick configuration
- `configure()` - Advanced configuration
- `validate_license()` - License validation
- `activate_license()` - License activation
- `enforce_license()` - Validation with automatic exit

### Classes
- `MachineIdentifier` - Machine ID generation
- `LicenseValidationResult` - Validation results
- `Configuration` - SDK configuration management
- `Client` - HTTP client for API communication
