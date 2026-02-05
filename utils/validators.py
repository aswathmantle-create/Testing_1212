"""
Utility functions for input validation.
"""
import re
from typing import Tuple


def validate_url(url: str) -> Tuple[bool, str]:
    """
    Validate a URL string.
    
    Args:
        url: URL string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return True, ""  # Empty URLs are allowed (optional)
    
    url = url.strip()
    
    # Basic URL pattern
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    
    if url_pattern.match(url):
        return True, ""
    else:
        return False, f"Invalid URL format: {url}"


def validate_csv(df, required_columns: list) -> Tuple[bool, str]:
    """
    Validate a DataFrame has required columns.
    
    Args:
        df: pandas DataFrame
        required_columns: List of required column names
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if df is None or df.empty:
        return False, "DataFrame is empty"
    
    missing = set(required_columns) - set(df.columns)
    
    if missing:
        return False, f"Missing required columns: {', '.join(missing)}"
    
    return True, ""


def validate_sku(sku: str) -> Tuple[bool, str]:
    """
    Validate SKU format.
    
    Args:
        sku: SKU string
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not sku:
        return False, "SKU is required"
    
    sku = sku.strip()
    
    if len(sku) < 2:
        return False, "SKU must be at least 2 characters"
    
    if len(sku) > 50:
        return False, "SKU must be less than 50 characters"
    
    return True, ""


def validate_ean(ean: str) -> Tuple[bool, str]:
    """
    Validate EAN/barcode format.
    
    Args:
        ean: EAN string
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not ean:
        return True, ""  # EAN is optional
    
    ean = ean.strip()
    
    # EAN-13 or EAN-8
    if not ean.isdigit():
        return False, "EAN must contain only digits"
    
    if len(ean) not in [8, 12, 13, 14]:
        return False, "EAN must be 8, 12, 13, or 14 digits"
    
    return True, ""
