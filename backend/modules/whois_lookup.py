import whois
from datetime import datetime
from typing import Dict, Any
from core.logger import get_logger

logger = get_logger(__name__)

def safe_date(d: Any) -> Any:
    if isinstance(d, list):
        if len(d) > 0:
            d = d[0]
        else:
            return None
    if isinstance(d, datetime):
        return d.isoformat()
    return d

def whois_lookup(domain: str) -> Dict[str, Any]:
    """Performs WHOIS lookup for a domain."""
    try:
        w = whois.whois(domain)
        
        ns = w.name_servers
        if isinstance(ns, str):
            ns = [ns]
        elif ns is None:
            ns = []
            
        return {
            "registrar": w.registrar,
            "creation_date": safe_date(w.creation_date),
            "expiration_date": safe_date(w.expiration_date),
            "updated_date": safe_date(w.updated_date),
            "name_servers": ns,
            "status": w.status if isinstance(w.status, list) else [w.status] if w.status else [],
            "org": w.org,
            "country": w.country
        }
    except Exception as e:
        logger.error(f"WHOIS lookup failed for {domain}: {e}")
        return {"error": str(e)}
