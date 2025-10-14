"""Exception classes for Source-License SDK"""

class SourceLicenseError(Exception):
    """Base exception class for all SDK errors"""
    pass

class ConfigurationError(SourceLicenseError):
    """Configuration related errors"""
    pass

class NetworkError(SourceLicenseError):
    """Network and HTTP related errors"""
    
    def __init__(self, message, response_code=None, response_body=None):
        super().__init__(message)
        self.response_code = response_code
        self.response_body = response_body

class LicenseError(SourceLicenseError):
    """License validation errors"""
    
    def __init__(self, message, error_code=None, retry_after=None):
        super().__init__(message)
        self.error_code = error_code
        self.retry_after = retry_after

class RateLimitError(LicenseError):
    """Rate limiting errors"""
    
    def __init__(self, message="Rate limit exceeded", retry_after=None):
        super().__init__(message, error_code="RATE_LIMIT_EXCEEDED", retry_after=retry_after)

class LicenseNotFoundError(LicenseError):
    """License not found errors"""
    
    def __init__(self, message="License not found"):
        super().__init__(message, error_code="LICENSE_NOT_FOUND")

class LicenseExpiredError(LicenseError):
    """License expired errors"""
    
    def __init__(self, message="License has expired"):
        super().__init__(message, error_code="LICENSE_EXPIRED")

class ActivationError(LicenseError):
    """License activation errors"""
    
    def __init__(self, message, error_code="ACTIVATION_FAILED"):
        super().__init__(message, error_code=error_code)

class MachineError(SourceLicenseError):
    """Machine ID related errors"""
    pass
