"""
Authentication utilities for token-based authentication.
"""
import os
import hmac
import hashlib
import time
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class AuthManager:
    """Simple token-based authentication manager."""
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize authentication manager.
        
        Args:
            secret_key: Secret key for token validation. If None, uses AUTH_SECRET_KEY env var.
        """
        self.secret_key = secret_key or os.getenv('AUTH_SECRET_KEY', 'default-secret-key-change-in-production')
        self.enabled = os.getenv('AUTH_ENABLED', 'false').lower() == 'true'
    
    def validate_token(self, token: Optional[str]) -> bool:
        """
        Validate authentication token.
        
        Args:
            token: Token to validate
            
        Returns:
            True if token is valid, False otherwise
        """
        if not self.enabled:
            return True  # Authentication disabled
        
        if not token:
            return False
        
        # Simple token validation - in production, use JWT or similar
        # For now, check if token matches expected format
        expected_token = self._generate_token()
        return hmac.compare_digest(token, expected_token)
    
    def _generate_token(self) -> str:
        """Generate a token based on secret key."""
        timestamp = int(time.time() // 3600)  # Changes every hour
        message = f"{self.secret_key}:{timestamp}"
        return hashlib.sha256(message.encode()).hexdigest()
    
    def require_auth(self, token: Optional[str]) -> None:
        """
        Require authentication, raise exception if invalid.
        
        Args:
            token: Token to validate
            
        Raises:
            PermissionError: If token is invalid
        """
        if not self.validate_token(token):
            raise PermissionError("Invalid or missing authentication token")


# Global auth manager instance
_auth_manager: Optional[AuthManager] = None


def get_auth_manager() -> AuthManager:
    """Get or create global auth manager instance."""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager

