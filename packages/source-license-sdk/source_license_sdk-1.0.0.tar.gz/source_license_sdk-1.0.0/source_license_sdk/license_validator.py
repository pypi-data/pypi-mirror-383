"""License validation result classes"""

from datetime import datetime
from typing import Optional, Dict, Any, Union

class LicenseValidationResult:
    """Represents the result of a license validation or activation request"""
    
    def __init__(self, data: Union[Dict[str, Any], None] = None, **kwargs):
        """Initialize validation result
        
        Args:
            data: Dictionary containing response data
            **kwargs: Direct field assignments
        """
        self._data = data or {}
        
        # Allow direct field assignment via kwargs
        for key, value in kwargs.items():
            self._data[key] = value
        
        self._initialize_fields()
    
    def _initialize_fields(self):
        """Initialize all result fields from data"""
        # Validation fields
        self.valid = self._extract_value('valid', False)
        self.token = self._extract_value('token')
        
        # Activation fields
        self.success = self._extract_value('success', False)
        self.activations_remaining = self._extract_value('activations_remaining')
        
        # Common fields
        self.error_message = self._extract_error_message()
        self.error_code = self._extract_value('error_code')
        self.expires_at = self._parse_datetime(self._extract_value('expires_at'))
        self.retry_after = self._extract_value('retry_after')
        self.timestamp = self._parse_datetime(self._extract_value('timestamp'))
        
        # Rate limit fields
        self.rate_limit_remaining = self._extract_rate_limit_value('remaining')
        self.rate_limit_reset_at = self._parse_datetime(self._extract_rate_limit_value('reset_at'))
    
    def is_valid(self) -> bool:
        """Check if the license is valid"""
        return self.valid is True
    
    def is_success(self) -> bool:
        """Check if the operation was successful"""
        return self.success is True
    
    def is_expired(self) -> bool:
        """Check if the license is expired"""
        if not self.expires_at:
            return False
        
        return self.expires_at < datetime.now()
    
    def is_rate_limited(self) -> bool:
        """Check if the request was rate limited"""
        if self.error_message and 'rate limit' in self.error_message.lower():
            return True
        
        return self.error_code == 'RATE_LIMIT_EXCEEDED'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            'valid': self.valid,
            'success': self.success,
            'error_message': self.error_message,
            'error_code': self.error_code,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'activations_remaining': self.activations_remaining,
            'retry_after': self.retry_after,
            'token': self.token,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'rate_limit_remaining': self.rate_limit_remaining,
            'rate_limit_reset_at': self.rate_limit_reset_at.isoformat() if self.rate_limit_reset_at else None,
        }
    
    def __repr__(self) -> str:
        """String representation of the result"""
        return f"<{self.__class__.__name__} valid={self.valid} success={self.success} error='{self.error_message}'>"
    
    def _extract_value(self, key: str, default: Any = None) -> Any:
        """Extract value from data dictionary"""
        return self._data.get(key, default)
    
    def _extract_error_message(self) -> Optional[str]:
        """Extract error message from data"""
        return self._extract_value('error') or self._extract_value('message')
    
    def _extract_rate_limit_value(self, key: str) -> Optional[Any]:
        """Extract rate limit specific value"""
        rate_limit_data = self._data.get('rate_limit', {})
        if isinstance(rate_limit_data, dict):
            return rate_limit_data.get(key)
        return None
    
    def _parse_datetime(self, value: Any) -> Optional[datetime]:
        """Parse datetime from various formats"""
        if value is None:
            return None
        
        if isinstance(value, datetime):
            return value
        
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value)
        
        try:
            # Try ISO format first
            if isinstance(value, str):
                # Handle various datetime formats
                for fmt in ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S']:
                    try:
                        return datetime.strptime(value, fmt)
                    except ValueError:
                        continue
                
                # Try parsing as ISO format
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
        
        except (ValueError, AttributeError):
            pass
        
        return None
