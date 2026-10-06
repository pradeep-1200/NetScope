import concurrent.futures
import requests
import string
import random
from typing import List, Dict, Any

from utils.resolver import shared_resolver
from core.logger import get_logger

logger = get_logger(__name__)

def generate_random_subdomain(length: int = 12) -> str:
    """Generates a random subdomain string."""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))

def detect_wildcard(domain: str) -> Dict[str, Any]:
    """
    Attempts to detect if the domain has a wildcard DNS record.
    Returns a dict with 'is_wildcard' (bool) and 'ips' (list) if found.
    """
    random_sub = generate_random_subdomain() + f".{domain}"
    try:
        answers = shared_resolver.resolve(random_sub, "A")
        ips = [rdata.to_text() for rdata in answers]
        return {"is_wildcard": True, "ips": ips}
    except Exception:
        return {"is_wildcard": False, "ips": []}

def resolve_subdomain(subdomain: str) -> Dict[str, Any]:
    """Resolves a single subdomain's A records."""
    try:
        answers = shared_resolver.resolve(subdomain, "A")
        ips = [rdata.to_text() for rdata in answers]
        return {"subdomain": subdomain, "ips": ips, "resolved": True}
    except Exception:
        return {"subdomain": subdomain, "ips": [], "resolved": False}

def bruteforce_subdomains(domain: str, wordlist_path: str, threads: int = 20) -> List[Dict[str, Any]]:
    """
    Bruteforces subdomains using a wordlist and a thread pool.
    """
    try:
        with open(wordlist_path, "r", encoding="utf-8") as f:
            words = [line.strip() for line in f if line.strip()]
    except Exception as e:
        logger.error(f"Failed to read wordlist {wordlist_path}: {e}")
        return []

    subdomains_to_check = [f"{word}.{domain}" for word in words]
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        future_to_sub = {executor.submit(resolve_subdomain, sub): sub for sub in subdomains_to_check}
        for future in concurrent.futures.as_completed(future_to_sub):
            res = future.result()
            if res["resolved"]:
                results.append(res)
                
    return results

def passive_crtsh(domain: str) -> List[str]:
    """
    Queries crt.sh for subdomains passively.
    """
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    unique_names = set()
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        for entry in data:
            name_value = entry.get("name_value", "")
            for name in name_value.split("\n"):
                name = name.strip().lower()
                # Strip wildcards
                if name.startswith("*."):
                    name = name[2:]
                
                # Ensure it ends with the target domain
                if name.endswith(f".{domain}") and name != domain:
                    unique_names.add(name)
                    
    except Exception as e:
        logger.error(f"crt.sh lookup failed for {domain}: {e}")
        
    return list(unique_names)

def enumerate_subdomains(domain: str, use_bruteforce: bool = True, use_passive: bool = True, wordlist_path: str = "wordlists/subdomains.txt") -> Dict[str, Any]:
    """
    Enumerates subdomains using bruteforce and/or crt.sh, merges the results,
    and handles wildcard DNS records.
    """
    wildcard_info = detect_wildcard(domain)
    
    brute_results = []
    if use_bruteforce:
        brute_results = bruteforce_subdomains(domain, wordlist_path)
        
    passive_names = []
    if use_passive:
        passive_names = passive_crtsh(domain)
        
    merged = {}
    
    # Process bruteforce results
    for b_res in brute_results:
        sub = b_res["subdomain"]
        merged[sub] = {
            "subdomain": sub,
            "ips": set(b_res["ips"]),
            "source": "bruteforce",
            "resolved": True
        }
        
    # Process passive results
    names_to_resolve = []
    for p_name in passive_names:
        if p_name in merged:
            merged[p_name]["source"] = "both"
        else:
            merged[p_name] = {
                "subdomain": p_name,
                "ips": set(),
                "source": "crtsh",
                "resolved": False
            }
            names_to_resolve.append(p_name)
            
    # Resolve passive-only subdomains
    if names_to_resolve:
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            future_to_sub = {executor.submit(resolve_subdomain, sub): sub for sub in names_to_resolve}
            for future in concurrent.futures.as_completed(future_to_sub):
                res = future.result()
                sub = res["subdomain"]
                if res["resolved"]:
                    merged[sub]["ips"] = set(res["ips"])
                    merged[sub]["resolved"] = True
                    
    # Filter out wildcard-only IP matches
    final_subdomains = []
    wildcard_ips = set(wildcard_info["ips"])
    
    for sub, data in merged.items():
        if data["resolved"] and wildcard_info["is_wildcard"]:
            # If all IPs for this subdomain match wildcard IPs, it's a wildcard catch-all
            if data["ips"].issubset(wildcard_ips):
                continue
                
        # Convert set back to list for JSON serialization
        data["ips"] = list(data["ips"])
        final_subdomains.append(data)
        
    resolved_count = sum(1 for s in final_subdomains if s["resolved"])
    
    result = {
        "domain": domain,
        "subdomains": final_subdomains,
        "total": len(final_subdomains),
        "resolved_count": resolved_count,
        "unresolved_count": len(final_subdomains) - resolved_count,
        "wildcard": wildcard_info["is_wildcard"]
    }
    
    return result
