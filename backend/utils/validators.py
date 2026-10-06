import re
from urllib.parse import urlparse

# Basic regex for domain validation
DOMAIN_REGEX = re.compile(
    r"^(?:[a-zA-Z0-9]"
    r"(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+"
    r"[a-zA-Z]{2,}$"
)

def is_valid_domain(domain: str) -> bool:
    """
    Validates a given string to see if it is a structurally valid domain name.
    """
    if not domain:
        return False
    # Check max length of a domain name (253 characters)
    if len(domain) > 253:
        return False
    
    # Run the regex
    return bool(DOMAIN_REGEX.match(domain))

def normalize_domain(domain: str) -> str:
    """
    Normalizes a domain by lowercasing, stripping protocols, paths, ports, and trailing dots.
    """
    if not domain:
        return ""
        
    domain = domain.lower().strip()
    
    # Remove protocol if present
    if "://" in domain:
        parsed = urlparse(domain)
        domain = parsed.netloc
    
    # Strip paths
    if "/" in domain:
        domain = domain.split("/")[0]
        
    # Strip ports
    if ":" in domain:
        domain = domain.split(":")[0]
        
    # Strip trailing dots
    domain = domain.rstrip(".")
    
    return domain
