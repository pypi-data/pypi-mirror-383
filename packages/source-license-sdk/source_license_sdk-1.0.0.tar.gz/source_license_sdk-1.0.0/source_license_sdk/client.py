"""HTTP client for communicating with Source-License API"""

import json
import urllib.request
import urllib.parse
import urllib.error
from urllib.request import Request, urlopen
from typing import Dict, Any, Optional
from .exceptions import (
    ConfigurationError, NetworkError, LicenseError, RateLimitError,
    LicenseNotFoundError, LicenseExpiredError, ActivationError
)
from .license_validator import LicenseValidationResult
from .machine_identifier import MachineIdentifier

class Client:
    """HTTP client for communicating with Source-License API"""
    
    def __init__(self, config):
        """Initialize client with configuration
        
        Args:
            config: Configuration object containing server settings
        """
        self.config = config
        self._validate_config()
    
    def validate_license(self, license_key: str, machine_id: Optional[str] = None, 
                        machine_fingerprint: Optional[str] = None) -> LicenseValidationResult:
        """Validate a license key
        
        Args:
            license_key: License key to validate
            machine_id: Optional machine identifier
            machine_fingerprint: Optional machine fingerprint
            
        Returns:
            LicenseValidationResult: Result of the validation
        """
        try:
            if machine_id and not machine_fingerprint:
                machine_fingerprint = MachineIdentifier.generate_fingerprint()
            
            path = f"/api/license/{license_key}/validate"
            params = {}
            
            if machine_id:
                params['machine_id'] = machine_id
            if machine_fingerprint:
                params['machine_fingerprint'] = machine_fingerprint
            
            response_data = self._make_request('GET', path, params=params)
            return LicenseValidationResult(response_data)
        
        except NetworkError as e:
            return self._handle_network_error(e)
    
    def activate_license(self, license_key: str, machine_id: str, 
                        machine_fingerprint: Optional[str] = None) -> LicenseValidationResult:
        """Activate a license on this machine
        
        Args:
            license_key: License key to activate
            machine_id: Unique machine identifier
            machine_fingerprint: Optional machine fingerprint
            
        Returns:
            LicenseValidationResult: Result of the activation
        """
        try:
            if not machine_fingerprint:
                machine_fingerprint = MachineIdentifier.generate_fingerprint()
            
            path = f"/api/license/{license_key}/activate"
            body = {
                'machine_id': machine_id,
                'machine_fingerprint': machine_fingerprint,
            }
            
            response_data = self._make_request('POST', path, body=body)
            return LicenseValidationResult(response_data)
        
        except NetworkError as e:
            return self._handle_network_error(e)
    
    def _validate_config(self):
        """Validate client configuration"""
        if not self.config.server_url:
            raise ConfigurationError("Server URL is required")
        
        if not self._is_valid_url(self.config.server_url):
            raise ConfigurationError("Invalid server URL format")
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        try:
            parsed = urllib.parse.urlparse(url)
            return parsed.scheme in ('http', 'https') and parsed.netloc
        except Exception:
            return False
    
    def _make_request(self, method: str, path: str, params: Optional[Dict[str, Any]] = None,
                     body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make HTTP request to the API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path
            params: Query parameters
            body: Request body data
            
        Returns:
            Dict containing response data
        """
        url = self._build_url(path, params)
        request = self._create_request(method, url, body)
        
        try:
            with urlopen(request, timeout=self.config.timeout) as response:
                return self._handle_response(response)
        
        except urllib.error.HTTPError as e:
            return self._handle_http_error(e)
        
        except urllib.error.URLError as e:
            raise NetworkError(f"Network error: {e.reason}")
        
        except Exception as e:
            raise NetworkError(f"Unexpected error: {str(e)}")
    
    def _build_url(self, path: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Build complete URL from path and parameters"""
        base_url = self.config.server_url.rstrip('/')
        url = f"{base_url}{path}"
        
        if params:
            query_string = urllib.parse.urlencode(params)
            url = f"{url}?{query_string}"
        
        return url
    
    def _create_request(self, method: str, url: str, body: Optional[Dict[str, Any]] = None) -> Request:
        """Create HTTP request object"""
        headers = {
            'User-Agent': self.config.user_agent,
            'Accept': 'application/json',
        }
        
        data = None
        if body:
            headers['Content-Type'] = 'application/json'
            data = json.dumps(body).encode('utf-8')
        
        request = Request(url, data=data, headers=headers)
        request.get_method = lambda: method.upper()
        
        return request
    
    def _handle_response(self, response) -> Dict[str, Any]:
        """Handle successful HTTP response"""
        content = response.read().decode('utf-8')
        
        if not content:
            return {}
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            raise NetworkError("Invalid JSON response from server", response_body=content)
    
    def _handle_http_error(self, error: urllib.error.HTTPError) -> Dict[str, Any]:
        """Handle HTTP error responses"""
        try:
            content = error.read().decode('utf-8')
            data = json.loads(content) if content else {}
        except (json.JSONDecodeError, UnicodeDecodeError):
            data = {'error': 'Invalid response from server'}
        
        status_code = error.code
        
        if status_code == 400:
            self._raise_license_error(data, status_code)
        elif status_code == 404:
            raise LicenseNotFoundError(data.get('error', 'License not found'))
        elif status_code == 429:
            retry_after = error.headers.get('Retry-After')
            if retry_after:
                retry_after = int(retry_after)
            else:
                retry_after = data.get('retry_after')
            raise RateLimitError(data.get('error', 'Rate limit exceeded'), retry_after=retry_after)
        elif 500 <= status_code <= 599:
            raise NetworkError(
                'Server error occurred',
                response_code=status_code,
                response_body=content
            )
        else:
            raise NetworkError(
                f"Unexpected response: {status_code}",
                response_code=status_code,
                response_body=content
            )
    
    def _raise_license_error(self, data: Dict[str, Any], status_code: int):
        """Raise appropriate license error based on response data"""
        error_message = data.get('error', data.get('message', 'License validation failed'))
        error_message_lower = error_message.lower()
        
        if 'expired' in error_message_lower:
            raise LicenseExpiredError(error_message)
        elif 'rate limit' in error_message_lower:
            retry_after = data.get('retry_after')
            raise RateLimitError(error_message, retry_after=retry_after)
        elif 'not found' in error_message_lower:
            raise LicenseNotFoundError(error_message)
        elif 'activation' in error_message_lower:
            raise ActivationError(error_message)
        else:
            raise LicenseError(error_message, error_code=data.get('error_code'))
    
    def _handle_network_error(self, error: NetworkError) -> LicenseValidationResult:
        """Convert network errors to license validation results for consistency"""
        if isinstance(error, RateLimitError):
            return LicenseValidationResult(
                valid=False,
                success=False,
                error=str(error),
                error_code=error.error_code,
                retry_after=error.retry_after
            )
        elif isinstance(error, (LicenseNotFoundError, LicenseExpiredError, ActivationError)):
            return LicenseValidationResult(
                valid=False,
                success=False,
                error=str(error),
                error_code=error.error_code
            )
        else:
            # Re-raise other network errors
            raise error
