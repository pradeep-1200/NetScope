import json
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from core.database import get_scan

REPORTS_DIR = Path(__file__).parent.parent.parent / "output"
TEMPLATES_DIR = Path(__file__).parent / "templates"

def setup_dirs():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def generate_json_report(scan_id: int) -> str:
    setup_dirs()
    scan = get_scan(scan_id)
    if not scan:
        raise ValueError(f"Scan {scan_id} not found")
        
    domain = scan["domain"]
    filepath = REPORTS_DIR / f"report_{domain}_{scan_id}.json"
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(scan, f, indent=2)
        
    return str(filepath)

def analyze_findings(scan: dict) -> list:
    findings = []
    
    if scan.get("zone_transfer") and scan["zone_transfer"].get("vulnerable"):
        findings.append({"level": "high", "message": f"Zone transfer allowed on nameserver: {scan['zone_transfer'].get('nameserver')}"})
        
    email_sec = scan.get("email_security", {})
    if not email_sec:
        findings.append({"level": "medium", "message": "Could not verify email security records (SPF/DMARC)"})
    else:
        if not email_sec.get("spf"):
            findings.append({"level": "medium", "message": "Missing SPF record. Domain might be vulnerable to spoofing."})
        if not email_sec.get("dmarc"):
            findings.append({"level": "medium", "message": "Missing DMARC record."})
            
    if scan.get("subdomains", {}).get("wildcard"):
        findings.append({"level": "info", "message": "Wildcard DNS record detected."})
        
    unresolved = sum(1 for s in scan.get("subdomains", {}).get("subdomains", []) if not s["resolved"])
    if unresolved > 0:
        findings.append({"level": "info", "message": f"{unresolved} subdomains failed to resolve."})
        
    return findings

def generate_html_report(scan_id: int) -> str:
    setup_dirs()
    scan = get_scan(scan_id)
    if not scan:
        raise ValueError(f"Scan {scan_id} not found")
        
    domain = scan["domain"]
    filepath = REPORTS_DIR / f"report_{domain}_{scan_id}.html"
    
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("report.html")
    
    findings = analyze_findings(scan)
    
    html_content = template.render(
        scan=scan,
        findings=findings,
        generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    )
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    return str(filepath)
