import pytest
from unittest.mock import patch
from modules.subdomain_enum import enumerate_subdomains

@patch('modules.subdomain_enum.detect_wildcard')
@patch('modules.subdomain_enum.bruteforce_subdomains')
@patch('modules.subdomain_enum.passive_crtsh')
@patch('modules.subdomain_enum.resolve_subdomain')
def test_enumerate_subdomains_merge(mock_resolve, mock_passive, mock_brute, mock_wildcard):
    # Setup mock returns
    mock_wildcard.return_value = {"is_wildcard": False, "ips": []}
    
    mock_brute.return_value = [
        {"subdomain": "www.example.com", "ips": ["1.1.1.1"], "resolved": True},
        {"subdomain": "mail.example.com", "ips": ["2.2.2.2"], "resolved": True}
    ]
    
    mock_passive.return_value = [
        "www.example.com",      # overlap with brute (should become 'both')
        "api.example.com",      # new, resolved successfully
        "old.example.com"       # new, fails to resolve
    ]
    
    def side_effect_resolve(sub):
        if sub == "api.example.com":
            return {"subdomain": sub, "ips": ["3.3.3.3"], "resolved": True}
        return {"subdomain": sub, "ips": [], "resolved": False}
        
    mock_resolve.side_effect = side_effect_resolve
    
    result = enumerate_subdomains("example.com", wordlist_path="dummy")
    
    assert result["domain"] == "example.com"
    assert result["total"] == 4
    assert result["resolved_count"] == 3
    assert result["unresolved_count"] == 1
    
    subs = {s["subdomain"]: s for s in result["subdomains"]}
    
    assert subs["www.example.com"]["source"] == "both"
    assert subs["mail.example.com"]["source"] == "bruteforce"
    assert subs["api.example.com"]["source"] == "crtsh"
    assert subs["api.example.com"]["resolved"] is True
    assert subs["old.example.com"]["resolved"] is False

@patch('modules.subdomain_enum.detect_wildcard')
@patch('modules.subdomain_enum.bruteforce_subdomains')
@patch('modules.subdomain_enum.passive_crtsh')
def test_wildcard_filtering(mock_passive, mock_brute, mock_wildcard):
    wildcard_ip = "9.9.9.9"
    mock_wildcard.return_value = {"is_wildcard": True, "ips": [wildcard_ip]}
    
    mock_brute.return_value = [
        {"subdomain": "www.example.com", "ips": ["1.1.1.1"], "resolved": True},
        {"subdomain": "random123.example.com", "ips": [wildcard_ip], "resolved": True} # Should be filtered
    ]
    
    mock_passive.return_value = []
    
    result = enumerate_subdomains("example.com", wordlist_path="dummy")
    
    assert result["total"] == 1
    assert result["subdomains"][0]["subdomain"] == "www.example.com"
