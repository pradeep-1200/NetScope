import time
from datetime import datetime
from typing import Dict, Any, Optional

from core.logger import get_logger
from core import database
from utils.validators import is_valid_domain, normalize_domain
from modules.dns_enum import enumerate_dns, attempt_zone_transfer, check_email_security
from modules.subdomain_enum import enumerate_subdomains
from modules.ip_footprint import collect_ips, analyze_ips
from modules.whois_lookup import whois_lookup

logger = get_logger(__name__)

SCAN_PROGRESS = {}

def get_progress(scan_id: int) -> Dict[str, Any]:
    return SCAN_PROGRESS.get(scan_id, {"stage": "unknown", "percent": 0, "status": "unknown"})

def run_scan(domain: str, scan_id: Optional[int] = None, options: Optional[Dict] = None) -> Dict[str, Any]:
    options = options or {}
    use_brute = options.get("bruteforce", True)
    use_passive = options.get("passive", True)
    threads = options.get("threads", 20)
    
    start_time = datetime.utcnow()
    started_at = start_time.isoformat()
    
    if scan_id is None:
        scan_id = database.create_scan(domain, started_at)
        
    SCAN_PROGRESS[scan_id] = {"stage": "validation", "percent": 5, "status": "running"}
    
    if not is_valid_domain(domain):
        error_msg = "Invalid domain format."
        database.update_scan_status(scan_id, "failed", error_msg, datetime.utcnow().isoformat(), 0)
        SCAN_PROGRESS[scan_id] = {"stage": "validation", "percent": 100, "status": "failed"}
        return {"error": error_msg}
        
    normalized = normalize_domain(domain)
    
    try:
        SCAN_PROGRESS[scan_id] = {"stage": "dns", "percent": 20, "status": "running"}
        t0 = time.perf_counter()
        dns_res = enumerate_dns(normalized)
        database.save_dns_records(scan_id, dns_res["records"])
        database.save_timing(scan_id, "dns", time.perf_counter() - t0)
        
        SCAN_PROGRESS[scan_id] = {"stage": "security", "percent": 30, "status": "running"}
        t0 = time.perf_counter()
        zt_res = attempt_zone_transfer(normalized)
        email_sec = check_email_security(normalized)
        database.save_timing(scan_id, "security", time.perf_counter() - t0)
        
        SCAN_PROGRESS[scan_id] = {"stage": "subdomains", "percent": 50, "status": "running"}
        t0 = time.perf_counter()
        sub_res = enumerate_subdomains(normalized, use_bruteforce=use_brute, use_passive=use_passive)
        database.save_subdomains(scan_id, sub_res["subdomains"])
        database.save_timing(scan_id, "subdomains", time.perf_counter() - t0)
        
        SCAN_PROGRESS[scan_id] = {"stage": "ips", "percent": 75, "status": "running"}
        t0 = time.perf_counter()
        ips = collect_ips(dns_res, sub_res)
        ip_info = analyze_ips(ips, threads=5)
        database.save_ip_information(scan_id, ip_info)
        database.save_timing(scan_id, "ips", time.perf_counter() - t0)
        
        SCAN_PROGRESS[scan_id] = {"stage": "whois", "percent": 90, "status": "running"}
        t0 = time.perf_counter()
        whois_res = whois_lookup(normalized)
        database.save_timing(scan_id, "whois", time.perf_counter() - t0)
        
        database.save_scan_meta(scan_id, whois_res, email_sec, zt_res)
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        database.update_scan_status(scan_id, "completed", None, end_time.isoformat(), duration)
        SCAN_PROGRESS[scan_id] = {"stage": "completed", "percent": 100, "status": "completed"}
        
    except Exception as e:
        logger.exception("Scan failed.")
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        database.update_scan_status(scan_id, "completed", str(e), end_time.isoformat(), duration) 
        SCAN_PROGRESS[scan_id] = {"stage": "error", "percent": 100, "status": "completed"}
        
    return database.get_scan(scan_id)
