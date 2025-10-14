"""Source-License Python SDK

A Python package for easy integration with the Source-License platform for license validation and activation.
"""

from .client import Client
from .machine_identifier import MachineIdentifier
from .license_validator import LicenseValidationResult
from .exceptions import (
    SourceLicenseError,
    ConfigurationError,
    NetworkError,
    LicenseError,
    RateLimitError,
    LicenseNotFoundError,
    LicenseExpiredError,
    ActivationError,
    MachineError
)

__version__ = "1.0.0"
__author__ = "PixelRidge Softworks"

class Configuration:
    """SDK Configuration class"""
    
    def __init__(self):
        self.server_url = None
        self.license_key = None
        self.machine_id = None
        self.auto_generate_machine_id = True
        self.timeout = 30
        self.user_agent = f"SourceLicenseSDK-Python/{__version__}"
        self.verify_ssl = True
    
    def is_valid(self):
        """Check if configuration is valid"""
        return self.server_url is not None and self.server_url.strip() != ""

# Global configuration instance
_config = Configuration()

def configure(**kwargs):
    """Configure the SDK with your Source-License server details
    
    Args:
        server_url (str): Source-License server URL
        license_key (str): License key to validate/activate
        machine_id (str, optional): Unique machine identifier
        auto_generate_machine_id (bool): Auto-generate machine ID if not provided
        timeout (int): HTTP request timeout in seconds
        user_agent (str): HTTP User-Agent header
        verify_ssl (bool): Verify SSL certificates
    """
    global _config
    
    for key, value in kwargs.items():
        if hasattr(_config, key):
            setattr(_config, key, value)
        else:
            raise ConfigurationError(f"Unknown configuration option: {key}")
    
    return _config

def setup(server_url, license_key, machine_id=None, auto_generate_machine_id=True):
    """Quick setup method for common use cases
    
    Args:
        server_url (str): Source-License server URL
        license_key (str): License key to validate/activate
        machine_id (str, optional): Unique machine identifier
        auto_generate_machine_id (bool): Auto-generate machine ID if not provided
    """
    return configure(
        server_url=server_url,
        license_key=license_key,
        machine_id=machine_id,
        auto_generate_machine_id=auto_generate_machine_id
    )

def validate_license(license_key=None, machine_id=None):
    """Validate a license key
    
    Args:
        license_key (str, optional): License key to validate. Uses configured key if not provided.
        machine_id (str, optional): Machine identifier. Uses configured or auto-generated if not provided.
    
    Returns:
        LicenseValidationResult: Result of the validation
    
    Raises:
        ConfigurationError: If license key is not provided or configured
    """
    # Check for empty string explicitly
    if license_key == "":
        raise ConfigurationError("License key cannot be empty")
    
    license_key = license_key or _config.license_key
    machine_id = machine_id or _config.machine_id
    
    if not license_key:
        raise ConfigurationError("License key is required")
    
    client = Client(_config)
    return client.validate_license(license_key, machine_id=machine_id)

def activate_license(license_key=None, machine_id=None):
    """Activate a license on this machine
    
    Args:
        license_key (str, optional): License key to activate. Uses configured key if not provided.
        machine_id (str, optional): Machine identifier. Uses configured or auto-generated if not provided.
    
    Returns:
        LicenseValidationResult: Result of the activation
    
    Raises:
        ConfigurationError: If license key or machine ID is not provided
    """
    # Check for empty string explicitly
    if machine_id == "":
        raise ConfigurationError("Machine ID cannot be empty")
    
    license_key = license_key or _config.license_key
    machine_id = machine_id or _config.machine_id
    
    if not license_key:
        raise ConfigurationError("License key is required")
    
    if not machine_id and _config.auto_generate_machine_id:
        machine_id = MachineIdentifier.generate()
    
    if not machine_id:
        raise ConfigurationError("Machine ID is required for activation")
    
    client = Client(_config)
    return client.activate_license(license_key, machine_id=machine_id)

def enforce_license(license_key=None, machine_id=None, exit_code=1, custom_message=None):
    """Validate license and exit application if invalid
    
    Args:
        license_key (str, optional): License key to validate. Uses configured key if not provided.
        machine_id (str, optional): Machine identifier. Uses configured or auto-generated if not provided.
        exit_code (int): Exit code to use when license is invalid
        custom_message (str, optional): Custom error message to display
    
    Returns:
        LicenseValidationResult: Result of the validation (only if valid)
    """
    import sys
    
    try:
        result = validate_license(license_key, machine_id)
        
        if not result.is_valid():
            message = custom_message or f"License validation failed: {result.error_message}"
            print(f"[LICENSE ERROR] {message}")
            sys.exit(exit_code)
        
        return result
    
    except SourceLicenseError as e:
        message = custom_message or f"License check failed: {e}"
        print(f"[LICENSE ERROR] {message}")
        sys.exit(exit_code)

# Convenience aliases
get_config = lambda: _config
