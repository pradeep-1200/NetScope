import dns.resolver
import dns.zone
import dns.query
from typing import Dict, Any

from utils.resolver import shared_resolver

RECORD_TYPES = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA", "SRV", "CAA"]

def enumerate_dns(domain: str) -> Dict[str, Any]:
    """
    Enumerates common DNS records for a given domain.
    """
    result = {
        "domain": domain,
        "records": {},
        "total_records": 0,
        "errors": {}
    }

    for record_type in RECORD_TYPES:
        try:
            answers = shared_resolver.resolve(domain, record_type)
            records = []
            for rdata in answers:
                records.append(rdata.to_text().strip('"'))
            if records:
                result["records"][record_type] = records
                result["total_records"] += len(records)
        except dns.resolver.NXDOMAIN:
            result["errors"][record_type] = "NXDOMAIN"
        except dns.resolver.NoAnswer:
            pass # Expected for many record types
        except dns.resolver.Timeout:
            result["errors"][record_type] = "Timeout"
        except dns.resolver.NoNameservers:
            result["errors"][record_type] = "NoNameservers"
        except Exception as e:
            result["errors"][record_type] = str(e)
            
    return result

def attempt_zone_transfer(domain: str) -> Dict[str, Any]:
    """
    Attempts a DNS zone transfer (AXFR) against all NS records of the domain.
    NOTE: This is a misconfiguration CHECK only. Zone transfers should generally
    be restricted to trusted secondary nameservers.
    """
    result = {
        "vulnerable": False,
        "nameserver": None,
        "records": []
    }
    
    try:
        ns_answers = shared_resolver.resolve(domain, "NS")
        nameservers = [str(ns.target) for ns in ns_answers]
    except Exception:
        return result
        
    for ns in nameservers:
        try:
            ns_ips = shared_resolver.resolve(ns, "A")
            for ns_ip in ns_ips:
                try:
                    # Attempt the zone transfer
                    zone = dns.zone.from_xfr(dns.query.xfr(str(ns_ip), domain, timeout=3, lifetime=5))
                    if zone:
                        result["vulnerable"] = True
                        result["nameserver"] = str(ns)
                        records = []
                        for name, node in zone.nodes.items():
                            rdatasets = node.rdatasets
                            for rdataset in rdatasets:
                                records.append(f"{name} {rdataset.to_text()}")
                        result["records"] = records
                        return result
                except Exception:
                    continue
        except Exception:
            continue
            
    return result

def check_email_security(domain: str) -> Dict[str, bool]:
    """
    Checks for the presence of SPF and DMARC records.
    """
    result = {
        "spf": False,
        "dmarc": False
    }
    
    # Check SPF (TXT record on the root domain starting with v=spf1)
    try:
        answers = shared_resolver.resolve(domain, "TXT")
        for rdata in answers:
            txt = rdata.to_text().strip('"').lower()
            if txt.startswith("v=spf1"):
                result["spf"] = True
                break
    except Exception:
        pass
        
    # Check DMARC (TXT record on _dmarc.domain starting with v=DMARC1)
    try:
        answers = shared_resolver.resolve(f"_dmarc.{domain}", "TXT")
        for rdata in answers:
            txt = rdata.to_text().strip('"').lower()
            if txt.startswith("v=dmarc1"):
                result["dmarc"] = True
                break
    except Exception:
        pass
        
    return result
