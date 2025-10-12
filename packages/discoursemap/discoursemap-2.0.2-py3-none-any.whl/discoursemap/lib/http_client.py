#!/usr/bin/env python3
"""HTTP Client Module

Custom HTTP client with retry logic and connection pooling.
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, Dict, Any

class HTTPClient:
    """Custom HTTP client with enhanced features"""
    
    def __init__(self, 
                 timeout: int = 10,
                 max_retries: int = 3,
                 proxy: Optional[str] = None,
                 verify_ssl: bool = True,
                 user_agent: Optional[str] = None):
        """
        Initialize HTTP client
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            proxy: Proxy server URL
            verify_ssl: Whether to verify SSL certificates
            user_agent: Custom User-Agent string
        """
        self.timeout = timeout
        self.proxy = proxy
        self.verify_ssl = verify_ssl
        self.user_agent = user_agent or "DiscourseMap/2.0"
        
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set headers
        self.session.headers.update({
            'User-Agent': self.user_agent
        })
        
        # Set proxy if provided
        if self.proxy:
            self.session.proxies.update({
                'http': self.proxy,
                'https': self.proxy
            })
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """Send GET request"""
        kwargs.setdefault('timeout', self.timeout)
        kwargs.setdefault('verify', self.verify_ssl)
        return self.session.get(url, **kwargs)
    
    def post(self, url: str, **kwargs) -> requests.Response:
        """Send POST request"""
        kwargs.setdefault('timeout', self.timeout)
        kwargs.setdefault('verify', self.verify_ssl)
        return self.session.post(url, **kwargs)
    
    def close(self):
        """Close the session"""
        self.session.close()
