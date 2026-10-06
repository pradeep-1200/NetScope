import socket
import concurrent.futures
import ipaddress
from typing import List, Dict, Any, Optional
from ipwhois import IPWhois
from core.logger import get_logger
from utils.resolver import shared_resolver

logger = get_logger(__name__)

def collect_ips(dns_result: Dict[str, Any], subdomain_result: Dict[str, Any]) -> List[str]:
    """Gather unique A/AAAA IPs from DNS and subdomain results."""
    ips = set()
    
    if "records" in dns_result:
        for rtype in ["A", "AAAA"]:
            for ip in dns_result["records"].get(rtype, []):
                ips.add(ip)
                
    for sub in subdomain_result.get("subdomains", []):
        if sub.get("resolved"):
            for ip in sub.get("ips", []):
                ips.add(ip)
                
    return list(ips)

def get_reverse_dns(ip: str) -> Optional[str]:
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return None

def analyze_ip(ip: str) -> Dict[str, Any]:
    """Analyzes a single IP address."""
    result = {
        "ip": ip,
        "reverse_dns": None,
        "asn": None,
        "asn_description": None,
        "organization": None,
        "network": None,
        "country": None,
        "private": False,
        "error": None
    }
    
    try:
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_private or ip_obj.is_reserved or ip_obj.is_loopback:
            result["private"] = True
            return result
            
        result["reverse_dns"] = get_reverse_dns(ip)
        
        # IPWhois query
        obj = IPWhois(ip)
        res = obj.lookup_rdap(depth=1)
        
        result["asn"] = res.get("asn")
        result["asn_description"] = res.get("asn_description")
        network = res.get("network", {})
        result["network"] = network.get("cidr")
        result["country"] = network.get("country")
        
        objects = res.get("objects", {})
        for obj_id, obj_data in objects.items():
            contact = obj_data.get("contact", {})
            name = contact.get("name")
            if name:
                result["organization"] = name
                break
                
    except Exception as e:
        logger.debug(f"IP analysis failed for {ip}: {e}")
        result["error"] = str(e)
        
    return result

def analyze_ips(ips: List[str], threads: int = 5) -> List[Dict[str, Any]]:
    """Analyzes multiple IPs concurrently."""
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        future_to_ip = {executor.submit(analyze_ip, ip): ip for ip in ips}
        for future in concurrent.futures.as_completed(future_to_ip):
            results.append(future.result())
    return results
