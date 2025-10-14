# Source-License Python SDK

A Python package for easy integration with the Source-License platform for license validation and activation.

## Features

- **Simple License Validation**: Check if a license key is valid with one method call
- **License Activation**: Activate licenses on specific machines with automatic machine fingerprinting
- **License Enforcement**: Automatically exit your application if license validation fails
- **Rate Limiting Handling**: Built-in handling of API rate limits with retry information
- **Secure Communication**: Uses HTTPS and handles all Source-License API security requirements
- **Cross-Platform Machine Identification**: Works on Windows, macOS, and Linux
- **Zero Dependencies**: Uses only Python standard library (optional psutil for enhanced machine ID)

## Installation

Install using pip:

```bash
pip install source-license-sdk
```

For enhanced machine identification (optional):

```bash
pip install source-license-sdk[system]
```

## Quick Start

### 🚀 Copy-Paste Examples for Instant Setup

#### 1. Simple License Check (Most Common)
Copy-paste this code and replace with your server URL:

```python
import source_license_sdk as sls

# Get license key from user (command line, config file, environment variable, etc.)
license_key = input("Enter your license key: ")

# Setup (replace server URL with your actual server)
sls.setup(
    server_url='http://localhost:4567',     # Your Source-License server
    license_key=license_key                 # License key from user
)

# Validate license
result = sls.validate_license()
if result.is_valid():
    print("✅ License is valid! Application can continue.")
else:
    print(f"❌ License invalid: {result.error_message}")
    exit(1)

# Your application code here...
print("🎉 Your application is running!")
```

#### 2. License Activation (One-Time Setup)
For applications that need to activate on first run:

```python
import source_license_sdk as sls
from source_license_sdk import MachineIdentifier

# Get license key from user
license_key = input("Enter your license key: ")

# Setup
sls.setup(
    server_url='http://localhost:4567',     # Your Source-License server
    license_key=license_key
)

# Generate machine ID for activation
machine_id = MachineIdentifier.generate()
print(f"Machine ID: {machine_id}")

# Try to activate the license
print("Activating license...")
result = sls.activate_license(license_key, machine_id=machine_id)

if result.is_success():
    print("✅ License activated successfully!")
    print(f"📊 Activations remaining: {result.activations_remaining}")
else:
    print(f"❌ Activation failed: {result.error_message}")
    exit(1)
```

#### 3. Complete App Protection (Recommended)
One-liner that handles everything automatically:

```python
import source_license_sdk as sls
import sys
import os

# Get license key from user (or load from config file)
license_key = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('LICENSE_KEY') or input("Enter your license key: ")

# Setup and enforce in one go - app exits if license is invalid
sls.setup(
    server_url='http://localhost:4567',     # Your Source-License server
    license_key=license_key
)

# This line will exit your app if license is invalid - no other code needed!
sls.enforce_license(custom_message="Please provide a valid license key to use this application.")

# Your protected application code starts here
print("🔐 Application running with valid license protection!")
```

#### 4. Custom Machine ID (For Server Applications)
When you need to specify a particular machine identifier:

**Note:** Be very careful using custom machine identifiers as machine identifiers must be unique. If the machine identifier matches ANY OTHER machine identifier in the Source-License database, activation ***WILL*** fail. We strongly suggest using the built-in machine identifier generation method.

```python
import source_license_sdk as sls
from source_license_sdk import MachineIdentifier
import os

# Get license key from user or environment
license_key = os.environ.get('LICENSE_KEY') or input("Enter your license key: ")

# Generate machine ID (recommended) or use custom identifier
machine_id = MachineIdentifier.generate()
# OR use custom ID: machine_id = 'SERVER-PROD-001'

# Setup
sls.setup(
    server_url='http://localhost:4567',     # Your Source-License server
    license_key=license_key,
    machine_id=machine_id
)

# Activate with the machine ID
result = sls.activate_license(license_key, machine_id=machine_id)
print("✅ Activated on " + machine_id if result.is_success() else f"❌ {result.error_message}")
```

### 📋 Core Methods Overview

| Method | Purpose | Returns | Use Case |
|--------|---------|---------|----------|
| `validate_license()` | Check if license is valid | `LicenseValidationResult` | Regular license checking |
| `activate_license()` | Activate license on machine | `LicenseValidationResult` | First-time setup |
| `enforce_license()` | Validate and exit if invalid | Nothing (exits on failure) | Application protection |

### Method 1: License Validation

Check if a license is valid without activating it:

```python
import source_license_sdk as sls

result = sls.validate_license()

if result.is_valid():
    print("License is valid!")
    if result.expires_at:
        print(f"Expires at: {result.expires_at}")
else:
    print(f"License validation failed: {result.error_message}")
```

### Method 2: License Activation

Activate a license on the current machine:

```python
import source_license_sdk as sls
from source_license_sdk import MachineIdentifier

# Generate machine ID for activation
machine_id = MachineIdentifier.generate()

# Activate with explicit machine ID
result = sls.activate_license(license_key, machine_id=machine_id)

if result.is_success():
    print("License activated successfully!")
    print(f"Activations remaining: {result.activations_remaining}")
else:
    print(f"Activation failed: {result.error_message}")
```

### Method 3: License Enforcement

Automatically exit the application if license validation fails:

```python
import source_license_sdk as sls

# This will exit the program with code 1 if the license is invalid
sls.enforce_license()

# Your application code continues here only if license is valid
print("Application starting with valid license...")
```

## Advanced Usage

### Custom Configuration

```python
import source_license_sdk as sls

sls.configure(
    server_url='https://your-license-server.com',
    license_key='YOUR-LICENSE-KEY',
    machine_id='custom-machine-id',
    timeout=30,
    verify_ssl=True,
    user_agent='MyApp/1.0.0'
)
```

### Manual Machine ID Generation

```python
from source_license_sdk import MachineIdentifier

# Generate a unique machine identifier
machine_id = MachineIdentifier.generate()
print(f"Machine ID: {machine_id}")

# Generate a machine fingerprint (more detailed)
fingerprint = MachineIdentifier.generate_fingerprint()
print(f"Machine Fingerprint: {fingerprint}")
```

### Error Handling

```python
import source_license_sdk as sls
from source_license_sdk import (
    NetworkError, RateLimitError, ConfigurationError
)

try:
    result = sls.validate_license()
    
    if result.is_valid():
        print("License is valid")
    else:
        print(f"License invalid: {result.error_message}")

except NetworkError as e:
    print(f"Network error: {e} (Code: {e.response_code})")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

### Working with Results

```python
import source_license_sdk as sls

result = sls.validate_license()

# Check various result properties
print(f"Valid: {result.is_valid()}")
print(f"Expires at: {result.expires_at}")
print(f"Rate limited: {result.is_rate_limited()}")
print(f"Rate limit remaining: {result.rate_limit_remaining}")
if result.error_code:
    print(f"Error code: {result.error_code}")

# Convert to dictionary
print(result.to_dict())
```

### Custom License Enforcement

```python
import source_license_sdk as sls

# Custom exit code and message
sls.enforce_license(
    exit_code=2,
    custom_message="This software requires a valid license to run."
)

# Use specific license key and machine ID
sls.enforce_license(
    license_key='SPECIFIC-LICENSE-KEY',
    machine_id='specific-machine-id'
)
```

## Integration Examples

### Django Application

```python
# settings.py
import source_license_sdk as sls

sls.setup(
    server_url='https://license.mycompany.com',
    license_key='YOUR-LICENSE-KEY'
)

# middleware.py
from django.http import HttpResponseForbidden
import source_license_sdk as sls

class LicenseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        result = sls.validate_license()
        
        if not result.is_valid():
            return HttpResponseForbidden("Invalid license")
        
        response = self.get_response(request)
        return response
```

### Flask Application

```python
from flask import Flask, jsonify
import source_license_sdk as sls

app = Flask(__name__)

# Setup license checking
sls.setup(
    server_url='https://license.mycompany.com',
    license_key='YOUR-LICENSE-KEY'
)

@app.before_request
def validate_license():
    result = sls.validate_license()
    
    if not result.is_valid():
        return jsonify({'error': 'Invalid license'}), 403

@app.route('/')
def index():
    return "Application running with valid license!"

if __name__ == '__main__':
    app.run()
```

### Command Line Tool

```python
#!/usr/bin/env python3
import source_license_sdk as sls
import sys
import os

# Setup license checking
sls.setup(
    server_url='https://license.mycompany.com',
    license_key=sys.argv[1] if len(sys.argv) > 1 else os.environ.get('LICENSE_KEY')
)

# Enforce license before running
sls.enforce_license(
    custom_message="Please provide a valid license key to use this tool."
)

# Your application logic here
print("Tool is running with valid license!")
```

### Desktop Application

```python
import source_license_sdk as sls
from source_license_sdk import MachineIdentifier
import os

class MyApplication:
    def __init__(self):
        self.setup_licensing()

    def setup_licensing(self):
        sls.setup(
            server_url='https://licensing.myapp.com',
            license_key=self.load_license_key(),
            auto_generate_machine_id=True
        )

        # Try to activate license if not already done
        self.activate_license_if_needed()
        
        # Validate license on startup
        self.validate_license()

    def load_license_key(self):
        # Load from config file, registry, etc.
        try:
            with open('license.key', 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            return None

    def activate_license_if_needed(self):
        result = sls.validate_license()
        
        if not result.is_valid():
            print("Activating license...")
            
            # Generate machine ID for activation
            machine_id = MachineIdentifier.generate()
            license_key = self.load_license_key()
            
            activation_result = sls.activate_license(license_key, machine_id=machine_id)
            
            if not activation_result.is_success():
                print(f"Failed to activate license: {activation_result.error_message}")
                exit(1)

    def validate_license(self):
        sls.enforce_license(
            custom_message="This application requires a valid license."
        )

if __name__ == "__main__":
    MyApplication()
```

## 🛠️ Troubleshooting & Common Issues

### Quick Diagnostics
Test your setup with this diagnostic snippet:

```python
import source_license_sdk as sls
from source_license_sdk import MachineIdentifier

print("🔍 Source-License SDK Diagnostics")
print("==================================")

# Test configuration
try:
    sls.setup(
        server_url='http://localhost:4567',
        license_key='VB6K-FSEY-VYWT-HTRJ'
    )
    print("✅ Configuration: OK")
except Exception as e:
    print(f"❌ Configuration Error: {e}")

# Test machine ID generation
try:
    machine_id = MachineIdentifier.generate()
    print(f"✅ Machine ID: {machine_id}")
except Exception as e:
    print(f"❌ Machine ID Error: {e}")

# Test server connectivity
try:
    result = sls.validate_license()
    print("✅ Server Connection: OK")
    print(f"📊 License Status: {'Valid' if result.is_valid() else 'Invalid'}")
except Exception as e:
    print(f"❌ Network Error: {e}")
```

### Common Problems & Solutions

#### Problem: "Connection refused" or similar network errors
```python
# ❌ Error: Connection refused
# ✅ Solution: Check your server URL and ensure the server is running

sls.setup(
    server_url='https://your-actual-domain.com',  # Not localhost in production
    license_key='YOUR-KEY'
)
```

#### Problem: "License key is required"
```python
# ❌ This will fail
result = sls.validate_license()  # No license key configured

# ✅ Always provide a license key
sls.setup(license_key='YOUR-ACTUAL-LICENSE-KEY')
result = sls.validate_license()
```

#### Problem: "Machine ID is required for activation"
```python
# ❌ This might fail
sls.setup(auto_generate_machine_id=False)
result = sls.activate_license(license_key)  # No machine ID provided

# ✅ Either enable auto-generation or provide manual ID
sls.setup(
    license_key='YOUR-KEY',
    machine_id='MY-SERVER-001'  # Manual ID
)
# OR
sls.setup(
    license_key='YOUR-KEY',
    auto_generate_machine_id=True  # Auto-generate (default)
)
```

#### Problem: Rate limiting
```python
from source_license_sdk import RateLimitError
import time

# Handle rate limits gracefully
try:
    result = sls.validate_license()
except RateLimitError as e:
    print(f"Rate limited. Waiting {e.retry_after} seconds...")
    time.sleep(e.retry_after)
    result = sls.validate_license()  # Try again after waiting
```

### 🧪 Testing Your Integration

#### Test Script Template
Save this as `test_license.py` to verify your setup:

```python
#!/usr/bin/env python3
import source_license_sdk as sls
from source_license_sdk import MachineIdentifier

# Replace these with your actual values
SERVER_URL = 'http://localhost:4567'
LICENSE_KEY = 'VB6K-FSEY-VYWT-HTRJ'

print("🧪 Testing Source-License Integration")
print("=====================================")

# Setup
sls.setup(
    server_url=SERVER_URL,
    license_key=LICENSE_KEY
)

# Test 1: Basic validation
print("\n1️⃣  Testing license validation...")
result = sls.validate_license()
if result.is_valid():
    print("✅ License is valid")
    print(f"   Expires: {result.expires_at or 'Never'}")
else:
    print(f"❌ License invalid: {result.error_message}")

# Test 2: Activation (if needed)
print("\n2️⃣  Testing license activation...")
machine_id = MachineIdentifier.generate()
activation_result = sls.activate_license(LICENSE_KEY, machine_id=machine_id)
if activation_result.is_success():
    print("✅ Activation successful")
    print(f"   Remaining: {activation_result.activations_remaining}")
else:
    print(f"ℹ️  Activation result: {activation_result.error_message}")

# Test 3: Machine ID
print("\n3️⃣  Testing machine identification...")
machine_id = MachineIdentifier.generate()
print(f"🖥️  Machine ID: {machine_id}")

print("\n🎉 Integration test complete!")
```

Run it with: `python test_license.py`

## Error Types

The SDK defines several exception types for different error scenarios:

- `SourceLicenseError` - Base exception class for all SDK errors
- `ConfigurationError` - Invalid SDK configuration
- `NetworkError` - HTTP/network related errors  
- `LicenseError` - General license validation errors
- `RateLimitError` - API rate limiting errors
- `LicenseNotFoundError` - License not found
- `LicenseExpiredError` - License has expired
- `ActivationError` - License activation errors
- `MachineError` - Machine identification errors

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `server_url` | str | None | Source-License server URL (required) |
| `license_key` | str | None | License key to validate/activate |
| `machine_id` | str | None | Unique machine identifier |
| `auto_generate_machine_id` | bool | True | Auto-generate machine ID if not provided |
| `timeout` | int | 30 | HTTP request timeout in seconds |
| `user_agent` | str | "SourceLicenseSDK-Python/VERSION" | HTTP User-Agent header |
| `verify_ssl` | bool | True | Verify SSL certificates |

## Development

After cloning the repository:

```bash
cd SL_SDKS/SL_Python_SDK
pip install -e .[dev]
```

To run tests:

```bash
pytest
```

To build the package:

```bash
python -m build
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create a new Pull Request

## License

This package is available as open source under the terms of the [GPL-3.0 License](LICENSE).

## Support

For support with this SDK and the Source-License platform, join our Discord community:

**🎮 Discord Server:** [discord.gg/j6v99ZPkrQ](https://discord.gg/j6v99ZPkrQ)

**💬 SDK Support Channel:** [#source-license-support](https://discord.com/channels/1419376086390800474/1419385647394984007)

Our community and developers are active on Discord to help with:
- SDK integration questions
- Troubleshooting license issues  
- Best practices and implementation guidance
- Feature requests and feedback

For urgent issues or enterprise support, please contact your license provider directly.
