"""
Cookie management for YOPmail client.

This module handles all cookie-related operations including setup,
validation, and management of authentication cookies.
"""

import time
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

from .exceptions import CookieSetupError
from .constants import DEFAULT_COOKIES

logger = logging.getLogger(__name__)


@dataclass
class CookieConfig:
    """Configuration for cookie setup."""
    domain: str = ".yopmail.com"
    path: str = "/"
    secure: bool = False
    httponly: bool = False
    samesite: Optional[str] = None


class CookieManager:
    """Manages cookies for YOPmail authentication."""
    
    def __init__(self, client):
        """Initialize cookie manager with HTTP client."""
        self.client = client
        self.config = CookieConfig()
        self._setup_default_cookies()
    
    def _setup_default_cookies(self) -> None:
        """Set up default authentication cookies."""
        try:
            current_time = time.strftime("%H:%M")
            
            # Set time cookie
            self._set_cookie("ytime", current_time)
            
            # Set default authentication cookies
            for name, value in DEFAULT_COOKIES.items():
                self._set_cookie(name, value)
                
            logger.debug("Default cookies set successfully")
            
        except Exception as e:
            raise CookieSetupError("default", str(e))
    
    def set_mailbox_cookie(self, mailbox: str) -> None:
        """Set mailbox-specific cookie."""
        try:
            self._set_cookie("ywm", mailbox)
            logger.debug(f"Mailbox cookie set for: {mailbox}")
        except Exception as e:
            raise CookieSetupError("ywm", str(e))
    
    def set_compte_cookie(self, compte_value: str) -> None:
        """Set compte cookie with mailbox information."""
        try:
            self._set_cookie("compte", compte_value)
            logger.debug("Compte cookie set successfully")
        except Exception as e:
            raise CookieSetupError("compte", str(e))
    
    def _set_cookie(self, name: str, value: str) -> None:
        """Set a cookie with proper configuration."""
        try:
            # httpx cookies.set() has different parameters than requests
            self.client.cookies.set(
                name,
                value,
                domain=self.config.domain,
                path=self.config.path
            )
            logger.debug(f"Cookie set: {name}={value}")
        except Exception as e:
            raise CookieSetupError(name, str(e))
    
    def get_cookie(self, name: str) -> Optional[str]:
        """Get cookie value by name."""
        cookie = self.client.cookies.get(name)
        return cookie.value if cookie else None
    
    def clear_cookies(self) -> None:
        """Clear all cookies."""
        self.client.cookies.clear()
        logger.debug("All cookies cleared")
    
    def validate_cookies(self) -> bool:
        """Validate that required cookies are set."""
        required_cookies = ["ytime", "ywm", "yc", "yses"]
        
        for cookie_name in required_cookies:
            if not self.get_cookie(cookie_name):
                logger.warning(f"Required cookie '{cookie_name}' not found")
                return False
        
        logger.debug("All required cookies are present")
        return True
    
    def update_time_cookie(self) -> None:
        """Update the time cookie with current time."""
        current_time = time.strftime("%H:%M")
        self._set_cookie("ytime", current_time)
        logger.debug(f"Time cookie updated to: {current_time}")
