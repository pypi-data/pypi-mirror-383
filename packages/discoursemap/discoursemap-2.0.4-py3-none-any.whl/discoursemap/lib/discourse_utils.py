#!/usr/bin/env python3
"""Discourse Utility Functions

Core utility functions for Discourse forum detection and manipulation.
"""

import re
import requests
from urllib.parse import urlparse, urljoin
from typing import Optional, List, Dict, Any

def validate_url(url: str) -> bool:
    """Validate if URL is properly formatted"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def normalize_url(url: str) -> str:
    """Normalize URL by removing trailing slashes"""
    return url.rstrip('/')

def clean_url(url: str) -> str:
    """Clean and normalize URL"""
    return normalize_url(url)

def extract_csrf_token(html: str) -> Optional[str]:
    """Extract CSRF token from HTML"""
    match = re.search(r'csrf["\']?\s*[:=]\s*["\']([^"\']+)', html, re.IGNORECASE)
    return match.group(1) if match else None

def extract_discourse_version(html: str) -> Optional[str]:
    """Extract Discourse version from HTML"""
    match = re.search(r'discourse["\']?\s*[:=]\s*["\']([^"\']+)', html, re.IGNORECASE)
    return match.group(1) if match else None

def is_discourse_forum(url: str) -> bool:
    """Check if URL is a Discourse forum"""
    try:
        response = requests.get(url, timeout=10)
        return 'discourse' in response.text.lower()
    except:
        return False

def is_discourse_site(url: str) -> bool:
    """Alias for is_discourse_forum"""
    return is_discourse_forum(url)

def generate_payloads(payload_type: str) -> List[str]:
    """Generate security testing payloads"""
    payloads = {
        'xss': ['<script>alert(1)</script>', '"><script>alert(1)</script>'],
        'sqli': ["' OR '1'='1", "1' OR '1'='1' --"],
    }
    return payloads.get(payload_type, [])

def random_user_agent() -> str:
    """Return a random user agent string"""
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def print_progress(message: str, verbose: bool = False):
    """Print progress message if verbose mode is enabled"""
    if verbose:
        print(message)

def make_request(url: str, method: str = 'GET', **kwargs):
    """Make HTTP request with error handling"""
    try:
        if method.upper() == 'GET':
            return requests.get(url, **kwargs)
        elif method.upper() == 'POST':
            return requests.post(url, **kwargs)
        elif method.upper() == 'PUT':
            return requests.put(url, **kwargs)
        elif method.upper() == 'DELETE':
            return requests.delete(url, **kwargs)
        else:
            return requests.request(method, url, **kwargs)
    except Exception as e:
        print(f"Request error: {e}")
        return None

def detect_waf(url: str) -> Optional[str]:
    """Detect Web Application Firewall"""
    try:
        response = requests.get(url, timeout=10)
        
        # Check headers for WAF indicators
        waf_headers = {
            'cloudflare': ['cf-ray', 'cf-cache-status'],
            'akamai': ['akamai-grn', 'x-akamai-transformed'],
            'aws': ['x-amz-cf-id', 'x-amz-cf-pop'],
            'imperva': ['x-iinfo', 'x-cdn'],
        }
        
        for waf_name, headers in waf_headers.items():
            for header in headers:
                if header in response.headers.keys():
                    return waf_name.upper()
        
        return None
    except:
        return None
