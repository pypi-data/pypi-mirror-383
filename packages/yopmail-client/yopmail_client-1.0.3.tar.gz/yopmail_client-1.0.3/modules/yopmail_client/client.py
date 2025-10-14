"""
Main YOPmail client implementation.

This module contains the core YOPMailClient class that provides
a clean API for interacting with YOPmail services.
"""

import logging
import time
from typing import List, Optional, Dict, Any
import httpx
from bs4 import BeautifulSoup

from .exceptions import (
    YOPMailError, 
    HTTPError, 
    MissingTokenError, 
    AuthenticationError,
    NetworkError
)
from .utils import HTMLParser, RequestBuilder, Message, validate_mailbox_name, sanitize_mailbox_name
from .cookies import CookieManager
from .cookie_detector import CookieDetector
from .rate_limiter import RateLimiter
from .proxy_manager import ProxyManager
from .constants import (
    BASE_URL, 
    DEFAULT_HEADERS, 
    LOGIN_HEADERS, 
    INBOX_HEADERS, 
    ENDPOINTS,
    DEFAULT_CONFIG
)

logger = logging.getLogger(__name__)


class YOPMailClient:
    """
    A clean, modular client for YOPmail disposable email service.
    
    This client provides methods to interact with YOPmail services including
    inbox access, message retrieval, and basic email operations.
    
    Example:
        >>> client = YOPMailClient("testuser")
        >>> client.open_inbox()
        >>> messages = client.list_messages()
        >>> for msg in messages:
        ...     print(f"Subject: {msg.subject}")
    """
    
    def __init__(
        self, 
        mailbox: str, 
        config: Optional[Dict[str, Any]] = None,
        client: Optional[httpx.Client] = None
    ):
        """
        Initialize YOPmail client.
        
        Args:
            mailbox: Mailbox name (without @yopmail.com)
            config: Optional configuration dictionary
            client: Optional httpx client instance
        """
        self.mailbox = sanitize_mailbox_name(mailbox)
        self.config = self._merge_config(config or {})
        self.yp_token: Optional[str] = None
        
        # Initialize managers first
        self.rate_limiter = RateLimiter(self.config)
        self.proxy_manager = ProxyManager(self.config)
        
        # Initialize HTTP client (after managers are ready)
        self.client = client or self._create_http_client()
        self.cookie_manager = CookieManager(self.client)
        self.cookie_detector = CookieDetector(self.client)
        
        logger.info(f"YOPmail client initialized for mailbox: {self.mailbox}")
    
    def _merge_config(self, user_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user configuration with defaults."""
        config = DEFAULT_CONFIG.__dict__.copy()
        config.update(user_config)
        return config
    
    def _create_http_client(self) -> httpx.Client:
        """Create configured HTTP client with proxy support."""
        client_kwargs = {
            "base_url": self.config.get("base_url", BASE_URL),
            "headers": DEFAULT_HEADERS,
            "follow_redirects": self.config.get("follow_redirects", True),
            "timeout": self.config.get("timeout", 30)
        }
        
        # Add proxy configuration if enabled
        if self.proxy_manager.is_proxy_enabled():
            proxies = self.proxy_manager.get_httpx_proxies()
            if proxies:
                client_kwargs["proxies"] = proxies
                logger.info(f"Using proxy: {self.proxy_manager.get_proxy_info()}")
        
        return httpx.Client(**client_kwargs)
    
    def open_inbox(self) -> None:
        """
        Initialize inbox access and extract authentication token.
        
        This method must be called before accessing messages.
        
        Raises:
            HTTPError: If the request fails
            MissingTokenError: If authentication token cannot be extracted
        """
        try:
            # Check rate limiting before making request
            delay = self.rate_limiter.get_request_delay()
            if delay > 0:
                logger.debug(f"Rate limiting delay: {delay:.1f}s")
                time.sleep(delay)
            
            # Ensure we have fresh cookies
            if not self.cookie_detector.ensure_fresh_cookies(self.mailbox):
                logger.warning("Failed to refresh cookies, using fallback method")
                # Fallback to basic cookie setup
                self.cookie_manager.set_mailbox_cookie(self.mailbox)
            
            # Access main page to establish session
            logger.debug("Accessing main page to establish session")
            main_resp = self.client.get(ENDPOINTS["main"])
            
            # Check for rate limiting
            if self._handle_rate_limit_response(main_resp):
                return self.open_inbox()  # Retry after rate limiting
            
            main_resp.raise_for_status()
            
            # Try to extract yp token from the response
            detected_cookies = self.cookie_detector.detect_cookies_from_response(main_resp.text)
            if 'yp_token' in detected_cookies:
                self.yp_token = detected_cookies['yp_token']
                logger.info(f"Extracted yp token from main page: {self.yp_token[:10]}...")
            else:
                # Fallback to known working token
                self.yp_token = "ZAGplZmp0ZmR3ZQN4ZGx1ZGR"
                logger.warning("Using fallback yp token")
            
            logger.info(f"Inbox opened successfully for {self.mailbox}")
            
        except httpx.HTTPStatusError as e:
            raise HTTPError(e.response.status_code, str(e.request.url), e.response.text)
        except httpx.RequestError as e:
            raise NetworkError("inbox initialization", str(e))
        except Exception as e:
            logger.error(f"Failed to open inbox: {e}")
            raise YOPMailError(f"Failed to open inbox: {e}")
    
    def list_messages(self, page: int = 1) -> List[Message]:
        """
        Retrieve list of messages from inbox.
        
        Args:
            page: Page number to retrieve (default: 1)
            
        Returns:
            List of Message objects
            
        Raises:
            HTTPError: If the request fails
            ParseError: If message parsing fails
        """
        if self.yp_token is None:
            self.open_inbox()
        
        try:
            # Build request parameters
            params = RequestBuilder.build_inbox_params(
                self.mailbox, 
                self.yp_token, 
                page
            )
            
            # Make request with proper headers
            headers = {**DEFAULT_HEADERS, **INBOX_HEADERS}
            resp = self.client.get(ENDPOINTS["inbox"], params=params, headers=headers)
            resp.raise_for_status()
            
            # Check if we got a valid response (not "Loading..." page)
            if self._is_loading_page(resp.text):
                logger.warning("Received loading page, cookies may be expired")
                # Try to refresh cookies and retry
                if self._refresh_and_retry():
                    return self.list_messages(page)
                else:
                    raise AuthenticationError("Failed to refresh authentication")
            
            # Parse messages from response
            messages = HTMLParser.parse_messages(resp.text)
            
            logger.info(f"Retrieved {len(messages)} messages from page {page}")
            return messages
            
        except httpx.HTTPStatusError as e:
            # Check if it's an authentication error
            if e.response.status_code == 400:
                logger.warning("Authentication error, attempting to refresh cookies")
                if self._refresh_and_retry():
                    return self.list_messages(page)
            raise HTTPError(e.response.status_code, str(e.request.url), e.response.text)
        except httpx.RequestError as e:
            raise NetworkError("message listing", str(e))
        except Exception as e:
            logger.error(f"Failed to list messages: {e}")
            raise YOPMailError(f"Failed to list messages: {e}")
    
    def fetch_message(self, message_id: str) -> str:
        """
        Fetch email message content (body only, not full HTML page).
        
        Args:
            message_id: ID of the message to fetch
            
        Returns:
            Email message body content (text only)
            
        Raises:
            HTTPError: If the request fails
        """
        try:
            # Use requests library for message fetching (httpx doesn't work with YOPmail)
            import requests
            import time
            from bs4 import BeautifulSoup
            
            # Create session with cookies
            session = requests.Session()
            session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            })
            
            # Set cookies like browser
            current_time = time.strftime("%H:%M")
            session.cookies.set("ytime", current_time, domain=".yopmail.com", path="/")
            session.cookies.set("ywm", self.mailbox, domain=".yopmail.com", path="/")
            session.cookies.set("yc", "EAGNlBGD2Awx4ZmpkZGN4ZQV", domain=".yopmail.com", path="/")
            session.cookies.set("yses", "zz6dtenHstru+L/GLPPQD4a5iJbTzoLzBsyP3HkfhNIwBQRWRdGPgRYto8uoBVoi", domain=".yopmail.com", path="/")
            
            # Access pages to establish session
            session.get("https://yopmail.com/")
            session.get("https://yopmail.com/en/wm")
            
            # Format message ID properly
            from .utils import format_message_id
            formatted_id = format_message_id(message_id)
            
            # Build the exact URL like the working test
            mail_url = f"https://yopmail.com/mail?b={self.mailbox}&id={formatted_id}"
            
            # Add proper headers for mail request (like browser)
            mail_headers = {
                "Referer": "https://yopmail.com/wm",
                "Sec-Fetch-Dest": "iframe",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
            }
            
            # Make request with proper headers
            resp = session.get(mail_url, headers=mail_headers)
            resp.raise_for_status()
            
            # Parse HTML and extract only the email body content
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Try to find the email body in different possible containers
            email_body = None
            
            # First, look for iframe content (YOPmail often loads email in iframe)
            iframes = soup.find_all('iframe')
            if iframes:
                # If there's an iframe, the email content might be in its src
                for iframe in iframes:
                    src = iframe.get('src', '')
                    if 'mail' in src.lower() or 'message' in src.lower():
                        # This might be the email content iframe
                        logger.debug(f"Found potential email iframe: {src}")
            
            # Look for email content in various containers
            body_selectors = [
                '#mailctn #mail',  # YOPmail specific email body container
                '#mailctn',  # YOPmail email container
                '#mail',  # Direct mail container
                'div[style*="font-family"]',  # YOPmail often uses inline styles
                'div[style*="padding"]',  # Email content usually has padding
                'div[class*="mail"]',
                'div[class*="message"]', 
                'div[class*="content"]',
                'div[class*="body"]',
                '.mail-body',
                '#mail-body',
                'div[style*="background"]',  # Email content areas
            ]
            
            for selector in body_selectors:
                body_element = soup.select_one(selector)
                if body_element:
                    text = body_element.get_text(strip=True)
                    # Look for content that seems like email body (not headers)
                    # For YOPmail, we want to accept shorter content if it's from the mail container
                    if (len(text) > 5 and 
                        not any(header in text.lower() for header in ['subject:', 'from:', 'date:', 'to:']) and
                        not any(ui in text.lower() for ui in ['deliverability', 'reply', 'forward', 'print', 'delete', 'html', 'text', 'headers', 'source', 'download'])):
                        email_body = body_element
                        logger.debug(f"Found email body with selector: {selector} -> {text}")
                        break
            
            # If no specific body found, look for the actual email content
            if not email_body:
                all_divs = soup.find_all('div')
                best_div = None
                best_score = 0
                
                for div in all_divs:
                    text = div.get_text(strip=True)
                    # Look for content that appears to be email body (not headers)
                    if len(text) > 5 and len(text) < 1000:  # Reasonable email body length
                        score = 0
                        
                        # Bonus for content that looks like email body
                        email_body_indicators = [
                            'hello', 'dear', 'thanks', 'regards', 'sincerely', 'best',
                            'hi', 'hey', 'greetings', 'yours', 'kind regards',
                            'please', 'thank you', 'welcome', 'congratulations'
                        ]
                        
                        for indicator in email_body_indicators:
                            if indicator in text.lower():
                                score += 10
                        
                        # Penalize if it contains header-like content
                        header_indicators = ['subject:', 'from:', 'date:', 'to:', 'sent:', 'received:']
                        for header in header_indicators:
                            if header in text.lower():
                                score -= 20
                        
                        # Bonus for content that doesn't look like navigation/UI
                        ui_indicators = ['deliverability', 'reply', 'forward', 'print', 'delete', 'html', 'text', 'headers', 'source', 'download']
                        ui_penalty = 0
                        for ui in ui_indicators:
                            if ui in text.lower():
                                ui_penalty += 5
                        score -= ui_penalty
                        
                        # Base score on length (but not too long)
                        score += min(len(text), 100)
                        
                        if score > best_score and score > 0:
                            best_score = score
                            best_div = div
                            logger.debug(f"Found potential email body with score {score}: {text[:50]}...")
                
                if best_div:
                    email_body = best_div
            
            # Extract text content
            if email_body:
                message_content = email_body.get_text(strip=True)
                # Clean up the content
                message_content = message_content.replace('\n', ' ').replace('\r', ' ')
                # Remove multiple spaces
                import re
                message_content = re.sub(r'\s+', ' ', message_content).strip()
                
                logger.info(f"Extracted message content for ID: {message_id} ({len(message_content)} chars)")
                return message_content
            else:
                # Fallback: return the full page text if we can't find specific body
                logger.warning("Could not find email body, returning full page text")
                full_text = soup.get_text(strip=True)
                return re.sub(r'\s+', ' ', full_text).strip()
            
        except Exception as e:
            logger.error(f"Failed to fetch message: {e}")
            raise YOPMailError(f"Failed to fetch message: {e}")
    
    def send_message(self, to: str, subject: str, body: str) -> None:
        """
        Send an email message.
        
        Note: This functionality is not yet implemented as the exact
        YOPmail send API is not publicly documented.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            
        Raises:
            NotImplementedError: This feature is not yet implemented
        """
        # TODO: Implement send functionality
        # The exact endpoint for sending mail via the web UI is not
        # publicly documented. The YOPmail front-end calls a POST using
        # JavaScript (callpost) when the send button is enabled.
        raise NotImplementedError(
            "YOPmail send API is undocumented; "
            "inspect callpost() in webmail.js for implementation"
        )
    
    def get_inbox_info(self) -> Dict[str, Any]:
        """
        Get basic information about the inbox.
        
        Returns:
            Dictionary with inbox information
        """
        messages = self.list_messages()
        return {
            "mailbox": self.mailbox,
            "message_count": len(messages),
            "has_messages": len(messages) > 0,
            "messages": [
                {
                    "id": msg.id,
                    "subject": msg.subject,
                    "sender": msg.sender,
                    "time": msg.time
                }
                for msg in messages
            ]
        }
    
    def close(self) -> None:
        """Close the HTTP client and clean up resources."""
        if hasattr(self, 'client'):
            self.client.close()
        logger.info("YOPmail client closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def _is_loading_page(self, html: str) -> bool:
        """Check if the response is a loading page indicating expired cookies."""
        loading_indicators = [
            "Loading ...",
            "w.rwm()",
            "reload webmail",
            "javascript:void(0)"
        ]
        
        html_lower = html.lower()
        return any(indicator.lower() in html_lower for indicator in loading_indicators)
    
    def _refresh_and_retry(self) -> bool:
        """Refresh cookies and authentication tokens."""
        try:
            logger.info("Attempting to refresh authentication...")
            
            # Try to refresh cookies from main page
            if self.cookie_detector.refresh_cookies_from_main_page():
                # Update yp token
                new_yp_token = self.cookie_detector.get_yp_token()
                if new_yp_token:
                    self.yp_token = new_yp_token
                    logger.info("Authentication refreshed successfully")
                    return True
            
            # Try WM page as fallback
            if self.cookie_detector.refresh_cookies_from_wm_page(self.mailbox):
                new_yp_token = self.cookie_detector.get_yp_token()
                if new_yp_token:
                    self.yp_token = new_yp_token
                    logger.info("Authentication refreshed from WM page")
                    return True
            
            logger.error("Failed to refresh authentication")
            return False
            
        except Exception as e:
            logger.error(f"Error during authentication refresh: {e}")
            return False
    
    def _handle_rate_limit_response(self, response: httpx.Response) -> bool:
        """
        Handle rate limiting response and return True if retry is needed.
        
        Args:
            response: HTTP response to check
            
        Returns:
            True if rate limited and retry is needed, False otherwise
        """
        try:
            should_retry, delay = self.rate_limiter.handle_rate_limit(
                response.status_code,
                dict(response.headers),
                response.text
            )
            
            if should_retry:
                logger.warning(f"Rate limited, waiting {delay:.1f} seconds...")
                time.sleep(delay)
                self.rate_limiter.record_request()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error handling rate limit: {e}")
            return False
    
    def get_proxy_info(self) -> Dict[str, Any]:
        """Get information about current proxy configuration."""
        return self.proxy_manager.get_proxy_info()
    
    def test_proxy_connection(self) -> bool:
        """Test proxy connection if enabled."""
        return self.proxy_manager.test_proxy_connection()
    
    def __repr__(self) -> str:
        """String representation of the client."""
        return f"YOPMailClient(mailbox='{self.mailbox}')"
