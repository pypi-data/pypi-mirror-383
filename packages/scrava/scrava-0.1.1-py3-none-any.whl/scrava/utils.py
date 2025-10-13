"""Utility functions for Scrava."""

import hashlib
from typing import Optional, Dict
from urllib.parse import urljoin, urlparse


def normalize_url(url: str) -> str:
    """
    Normalize a URL for consistent comparison.
    
    Args:
        url: The URL to normalize
        
    Returns:
        Normalized URL
    """
    # Remove fragment
    parsed = urlparse(url)
    normalized = parsed._replace(fragment='').geturl()
    
    # Remove trailing slash
    if normalized.endswith('/') and normalized.count('/') > 2:
        normalized = normalized.rstrip('/')
    
    return normalized


def url_fingerprint(url: str, method: str = 'GET', body: Optional[bytes] = None) -> str:
    """
    Generate a unique fingerprint for a URL/request.
    
    Args:
        url: The URL
        method: HTTP method
        body: Request body
        
    Returns:
        SHA256 fingerprint
    """
    url_norm = normalize_url(url)
    data = f"{method}:{url_norm}"
    
    if body:
        data += f":{body.hex()}"
    
    return hashlib.sha256(data.encode()).hexdigest()


def extract_domain(url: str) -> str:
    """
    Extract domain from URL.
    
    Args:
        url: The URL
        
    Returns:
        Domain name
    """
    parsed = urlparse(url)
    return parsed.netloc


def join_url(base: str, path: str) -> str:
    """
    Join a base URL with a relative path.
    
    Args:
        base: Base URL
        path: Relative or absolute path
        
    Returns:
        Absolute URL
    """
    return urljoin(base, path)


def extract_links(selector, base_url: str = '') -> list:
    """
    Extract all links from a selector.
    
    Args:
        selector: Parsel selector
        base_url: Base URL for joining relative links
        
    Returns:
        List of absolute URLs
    """
    links = selector.css('a::attr(href)').getall()
    
    if base_url:
        links = [urljoin(base_url, link) for link in links]
    
    return links


def clean_text(text: Optional[str]) -> str:
    """
    Clean and normalize text.
    
    Args:
        text: Raw text
        
    Returns:
        Cleaned text
    """
    if not text:
        return ''
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Strip
    text = text.strip()
    
    return text


def parse_price(text: str, currency: str = '$') -> Optional[float]:
    """
    Parse a price string to float.
    
    Args:
        text: Price text (e.g., "$19.99", "£20.50")
        currency: Currency symbol to remove
        
    Returns:
        Price as float, or None if parsing fails
    """
    if not text:
        return None
    
    # Remove currency symbol and other non-numeric chars except . and ,
    cleaned = text.replace(currency, '').strip()
    cleaned = ''.join(c for c in cleaned if c.isdigit() or c in '.,')
    
    # Handle comma as decimal separator (European format)
    if ',' in cleaned and '.' not in cleaned:
        cleaned = cleaned.replace(',', '.')
    elif ',' in cleaned and '.' in cleaned:
        # Remove thousands separator
        cleaned = cleaned.replace(',', '')
    
    try:
        return float(cleaned)
    except ValueError:
        return None


def build_headers(user_agent: Optional[str] = None, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """
    Build common HTTP headers.
    
    Args:
        user_agent: User-Agent string
        extra: Additional headers
        
    Returns:
        Headers dictionary
    """
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    if user_agent:
        headers['User-Agent'] = user_agent
    else:
        headers['User-Agent'] = (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
    
    if extra:
        headers.update(extra)
    
    return headers


def rate_limit_key(domain: str) -> str:
    """
    Generate a rate limit key for a domain.
    
    Args:
        domain: Domain name
        
    Returns:
        Rate limit key
    """
    return f"ratelimit:{domain}"


def bytes_to_human(num_bytes: int) -> str:
    """
    Convert bytes to human-readable format.
    
    Args:
        num_bytes: Number of bytes
        
    Returns:
        Human-readable string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if num_bytes < 1024.0:
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.2f} PB"


def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix



