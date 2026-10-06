import pytest
from modules.dns_enum import enumerate_dns, attempt_zone_transfer, check_email_security

def test_enumerate_dns_valid():
    domain = "example.com"
    result = enumerate_dns(domain)
    
    assert result["domain"] == domain
    assert "A" in result["records"]
    assert len(result["records"]["A"]) > 0
    assert result["total_records"] > 0

def test_enumerate_dns_invalid():
    domain = "this-domain-definitely-does-not-exist-12345.com"
    result = enumerate_dns(domain)
    
    assert result["domain"] == domain
    assert result["total_records"] == 0
    assert "NXDOMAIN" in result["errors"].values()

def test_attempt_zone_transfer():
    domain = "example.com"
    result = attempt_zone_transfer(domain)
    # example.com should not be vulnerable to zone transfer
    assert result["vulnerable"] is False

def test_check_email_security():
    domain = "example.com"
    result = check_email_security(domain)
    
    assert "spf" in result
    assert "dmarc" in result
