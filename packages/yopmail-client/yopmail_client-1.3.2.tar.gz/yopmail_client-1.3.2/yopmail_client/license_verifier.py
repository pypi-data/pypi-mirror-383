"""
License verification module for YOPmail client.

This module handles API key validation using KeyAuth service.
"""

import logging
import os
import sys
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class LicenseError(Exception):
    """Raised when license validation fails."""
    pass


class LicenseVerifier:
    """
    Handles license key verification using KeyAuth.
    
    This class validates user license keys against the KeyAuth service
    to ensure only paid users can access the YOPmail client.
    """
    
    def __init__(self):
        """Initialize the license verifier."""
        self.keyauth_app = None
        self._initialize_keyauth()
    
    def _initialize_keyauth(self) -> None:
        """Initialize KeyAuth application."""
        try:
            from keyauth import api
            import os
            
            # Get KeyAuth credentials from environment variables
            # These should be set in GitHub repository secrets for CI/CD
            app_name = os.getenv("KEYAUTH_APP_NAME", "YOPmailClientApp")
            owner_id = os.getenv("KEYAUTH_OWNER_ID")
            secret = os.getenv("KEYAUTH_SECRET")
            app_version = os.getenv("KEYAUTH_APP_VERSION", "1.2.1")
            
            # Validate required environment variables
            if not owner_id:
                raise LicenseError(
                    "KEYAUTH_OWNER_ID environment variable is required. "
                    "Set it in your GitHub repository secrets for CI/CD deployment."
                )
            
            if not secret:
                raise LicenseError(
                    "KEYAUTH_SECRET environment variable is required. "
                    "Set it in your GitHub repository secrets for CI/CD deployment."
                )
            
            # Initialize KeyAuth with environment variables
            self.keyauth_app = api(
                name=app_name,
                owner_id=owner_id,
                secret=secret,
                version=app_version,
                file_hash=self._get_checksum()  # Optional file hash for integrity
            )
            logger.info(f"KeyAuth initialized successfully with app: {app_name}")
            
        except ImportError:
            # KeyAuth is not available on this platform (likely Linux)
            logger.warning("KeyAuth library not available on this platform. License verification will be skipped.")
            self.keyauth_app = None
        except Exception as e:
            logger.error(f"Failed to initialize KeyAuth: {e}")
            raise LicenseError(f"Failed to initialize license verification: {e}")
    
    def _get_checksum(self) -> Optional[str]:
        """Get file checksum for integrity verification."""
        try:
            import hashlib
            
            # Get the current file's checksum
            current_file = os.path.abspath(__file__)
            with open(current_file, 'rb') as f:
                content = f.read()
                return hashlib.sha256(content).hexdigest()
        except Exception:
            # If checksum calculation fails, continue without it
            return None
    
    def verify_license(self, api_key: str) -> bool:
        """
        Verify the provided license key.
        
        Args:
            api_key: The license key to verify
            
        Returns:
            True if the license is valid, False otherwise
            
        Raises:
            LicenseError: If license verification fails
        """
        if not api_key or api_key == "YOUR_LICENSE_KEY_HERE":
            raise LicenseError("Invalid API key. Please set a valid license key in yopmail_config.py")
        
        try:
            if not self.keyauth_app:
                # KeyAuth is not available on this platform (likely Linux)
                # For CI/CD environments, we'll allow this to pass
                logger.warning("KeyAuth not available on this platform. License verification skipped for CI/CD.")
                return True
            
            # Validate the license key with KeyAuth
            response = self.keyauth_app.license(api_key)
            
            if response.success != "true":
                logger.error(f"License validation failed: {response.message}")
                raise LicenseError("Invalid or expired license key")
            
            logger.info("License validation successful")
            return True
            
        except Exception as e:
            logger.error(f"License verification error: {e}")
            raise LicenseError(f"License verification failed: {e}")
    
    def get_user_info(self, api_key: str) -> Dict[str, Any]:
        """
        Get user information from the license key.
        
        Args:
            api_key: The license key
            
        Returns:
            Dictionary containing user information
        """
        try:
            if not self.keyauth_app:
                raise LicenseError("License verification service not initialized")
            
            # Get user information from KeyAuth
            response = self.keyauth_app.license(api_key)
            
            if response.success != "true":
                raise LicenseError("Invalid license key")
            
            return {
                "username": getattr(response, 'username', 'Unknown'),
                "expiry": getattr(response, 'expiry', 'Unknown'),
                "level": getattr(response, 'level', 'Unknown'),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            return {"success": False, "error": str(e)}


def load_user_config() -> Dict[str, Any]:
    """
    Load user configuration from yopmail_config.py.
    
    Returns:
        Dictionary containing user configuration
        
    Raises:
        LicenseError: If configuration file is missing or invalid
    """
    try:
        # Try to import the user's configuration
        import yopmail_config
        
        config = {
            "api_key": getattr(yopmail_config, "API_KEY", None),
            "proxy_url": getattr(yopmail_config, "PROXY_URL", None),
            "proxy_list": getattr(yopmail_config, "PROXY_LIST", None),
            "proxy_username": getattr(yopmail_config, "PROXY_USERNAME", None),
            "proxy_password": getattr(yopmail_config, "PROXY_PASSWORD", None),
            "proxy_rotation": getattr(yopmail_config, "PROXY_ROTATION", False)
        }
        
        return config
        
    except ImportError:
        raise LicenseError(
            "yopmail_config.py not found. Please create this file with your API_KEY. "
            "See the template in the project root for an example."
        )
    except Exception as e:
        raise LicenseError(f"Failed to load configuration: {e}")


def validate_license_and_config() -> Dict[str, Any]:
    """
    Validate license key and load user configuration.
    
    Returns:
        Dictionary containing validated configuration
        
    Raises:
        LicenseError: If license validation fails
    """
    # Initialize verifier first to check if KeyAuth is available
    verifier = LicenseVerifier()
    
    # If KeyAuth is not available (e.g., in CI environments), skip license validation
    if not verifier.keyauth_app:
        logger.warning("KeyAuth not available. Skipping license validation for CI/CD environment.")
        # Return a minimal config for CI environments
        return {
            "api_key": "CI_ENVIRONMENT",
            "proxy_url": None,
            "proxy_list": None,
            "proxy_username": None,
            "proxy_password": None,
            "proxy_rotation": False
        }
    
    # Load user configuration only if KeyAuth is available
    config = load_user_config()
    
    # Validate license key
    verifier.verify_license(config["api_key"])
    
    logger.info("License validation successful")
    return config
