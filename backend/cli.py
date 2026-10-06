import argparse
import sys
import json
from core.scanner import run_scan
from core.database import init_db, list_scans, get_scan
from reports.report_generator import generate_json_report, generate_html_report

def main():
    parser = argparse.ArgumentParser(description="NetScope CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    scan_parser = subparsers.add_parser("scan", help="Run a new scan")
    scan_parser.add_argument("domain", help="Target domain")
    scan_parser.add_argument("--no-bruteforce", action="store_true", help="Disable subdomain bruteforcing")
    scan_parser.add_argument("--no-passive", action="store_true", help="Disable crt.sh passive lookup")
    scan_parser.add_argument("--threads", type=int, default=20, help="Threads for bruteforcing")
    scan_parser.add_argument("--json", action="store_true", help="Output raw JSON")
    scan_parser.add_argument("--report", choices=["html", "json"], help="Generate a report")
    
    subparsers.add_parser("history", help="List past scans")
    
    show_parser = subparsers.add_parser("show", help="Show details of a past scan")
    show_parser.add_argument("scan_id", type=int, help="Scan ID")
    
    args = parser.parse_args()
    init_db()
    
    if args.command == "scan":
        print("[!] LEGAL WARNING: Only scan domains you own or have permission to test.")
        options = {
            "bruteforce": not args.no_bruteforce,
            "passive": not args.no_passive,
            "threads": args.threads
        }
        res = run_scan(args.domain, options=options)
        
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"\n--- Scan Complete: {res['domain']} ---")
            print(f"Status: {res['status']} | Duration: {res['duration_seconds']:.2f}s")
            
        if args.report == "json":
            generate_json_report(res["id"])
            print(f"JSON report generated for scan {res['id']}")
        elif args.report == "html":
            generate_html_report(res["id"])
            print(f"HTML report generated for scan {res['id']}")
            
    elif args.command == "history":
        scans = list_scans()
        print(f"{'ID':<5} | {'Domain':<25} | {'Status':<10} | {'Started At'}")
        print("-" * 65)
        for s in scans:
            print(f"{s['id']:<5} | {s['domain']:<25} | {s['status']:<10} | {s['started_at']}")
            
    elif args.command == "show":
        res = get_scan(args.scan_id)
        if not res:
            print("Scan not found.")
            sys.exit(1)
        print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
