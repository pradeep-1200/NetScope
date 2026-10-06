import pytest
from utils.validators import is_valid_domain, normalize_domain

def test_is_valid_domain():
    assert is_valid_domain("example.com") is True
    assert is_valid_domain("sub.example.com") is True
    assert is_valid_domain("valid-domain123.org") is True
    
    assert is_valid_domain("invalid_domain.com") is False
    assert is_valid_domain("http://example.com") is False
    assert is_valid_domain("example.com/") is False
    assert is_valid_domain("") is False

def test_normalize_domain():
    assert normalize_domain("EXAMPLE.COM") == "example.com"
    assert normalize_domain("http://example.com") == "example.com"
    assert normalize_domain("https://example.com/") == "example.com"
    assert normalize_domain("example.com:8080") == "example.com"
    assert normalize_domain("example.com.") == "example.com"
