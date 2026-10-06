import sqlite3
import json
import os
from contextlib import contextmanager
from typing import Dict, Any, List, Optional
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "database" / "scans.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = 1")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT NOT NULL,
                status TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                duration_seconds REAL,
                whois_json TEXT,
                email_security_json TEXT,
                zone_transfer_json TEXT,
                error TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dns_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER NOT NULL,
                record_type TEXT NOT NULL,
                value TEXT NOT NULL,
                FOREIGN KEY (scan_id) REFERENCES scans(id) ON DELETE CASCADE
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS subdomains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER NOT NULL,
                subdomain TEXT NOT NULL,
                ip TEXT,
                source TEXT,
                resolved INTEGER NOT NULL,
                FOREIGN KEY (scan_id) REFERENCES scans(id) ON DELETE CASCADE
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ip_information (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER NOT NULL,
                ip TEXT NOT NULL,
                reverse_dns TEXT,
                asn TEXT,
                organization TEXT,
                network TEXT,
                country TEXT,
                FOREIGN KEY (scan_id) REFERENCES scans(id) ON DELETE CASCADE
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scan_timings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER NOT NULL,
                stage TEXT NOT NULL,
                seconds REAL NOT NULL,
                FOREIGN KEY (scan_id) REFERENCES scans(id) ON DELETE CASCADE
            )
        """)

def create_scan(domain: str, started_at: str) -> int:
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO scans (domain, status, started_at) VALUES (?, ?, ?)",
            (domain, "running", started_at)
        )
        return cursor.lastrowid

def update_scan_status(scan_id: int, status: str, error: Optional[str] = None, completed_at: Optional[str] = None, duration: Optional[float] = None):
    with get_db() as conn:
        if error:
            conn.execute("UPDATE scans SET status = ?, error = ?, completed_at = ?, duration_seconds = ? WHERE id = ?", 
                         (status, error, completed_at, duration, scan_id))
        else:
            conn.execute("UPDATE scans SET status = ?, completed_at = ?, duration_seconds = ? WHERE id = ?", 
                         (status, completed_at, duration, scan_id))

def save_dns_records(scan_id: int, records_dict: Dict[str, List[str]]):
    with get_db() as conn:
        for rtype, values in records_dict.items():
            for val in values:
                conn.execute(
                    "INSERT INTO dns_records (scan_id, record_type, value) VALUES (?, ?, ?)",
                    (scan_id, rtype, val)
                )

def save_subdomains(scan_id: int, subdomain_list: List[Dict[str, Any]]):
    with get_db() as conn:
        for sub in subdomain_list:
            ips = sub.get("ips", [])
            ip_str = ",".join(ips) if ips else None
            conn.execute(
                "INSERT INTO subdomains (scan_id, subdomain, ip, source, resolved) VALUES (?, ?, ?, ?, ?)",
                (scan_id, sub["subdomain"], ip_str, sub.get("source", ""), 1 if sub.get("resolved") else 0)
            )

def save_ip_information(scan_id: int, ip_list: List[Dict[str, Any]]):
    with get_db() as conn:
        for ip in ip_list:
            conn.execute(
                "INSERT INTO ip_information (scan_id, ip, reverse_dns, asn, organization, network, country) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (scan_id, ip["ip"], ip.get("reverse_dns"), ip.get("asn"), ip.get("organization"), ip.get("network"), ip.get("country"))
            )

def save_timing(scan_id: int, stage: str, seconds: float):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO scan_timings (scan_id, stage, seconds) VALUES (?, ?, ?)",
            (scan_id, stage, seconds)
        )

def save_scan_meta(scan_id: int, whois_data: Dict, email_security: Dict, zone_transfer: Dict):
    with get_db() as conn:
        conn.execute(
            """UPDATE scans SET 
               whois_json = ?, email_security_json = ?, zone_transfer_json = ?
               WHERE id = ?""",
            (json.dumps(whois_data), json.dumps(email_security), json.dumps(zone_transfer), scan_id)
        )

def get_scan(scan_id: int) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        scan_row = conn.execute("SELECT * FROM scans WHERE id = ?", (scan_id,)).fetchone()
        if not scan_row:
            return None
            
        result = dict(scan_row)
        result["whois"] = json.loads(result["whois_json"]) if result.get("whois_json") else None
        result["email_security"] = json.loads(result["email_security_json"]) if result.get("email_security_json") else None
        result["zone_transfer"] = json.loads(result["zone_transfer_json"]) if result.get("zone_transfer_json") else None
        
        dns_rows = conn.execute("SELECT * FROM dns_records WHERE scan_id = ?", (scan_id,)).fetchall()
        records = {}
        for row in dns_rows:
            rtype = row["record_type"]
            if rtype not in records:
                records[rtype] = []
            records[rtype].append(row["value"])
        result["dns"] = {"domain": result["domain"], "records": records, "total_records": len(dns_rows), "errors": {}}
        
        sub_rows = conn.execute("SELECT * FROM subdomains WHERE scan_id = ?", (scan_id,)).fetchall()
        subdomains = []
        for row in sub_rows:
            sub = dict(row)
            sub["resolved"] = bool(sub["resolved"])
            sub["ips"] = sub["ip"].split(",") if sub["ip"] else []
            del sub["ip"]
            subdomains.append(sub)
        result["subdomains"] = {"domain": result["domain"], "subdomains": subdomains, "total": len(subdomains)}
        
        ip_rows = conn.execute("SELECT * FROM ip_information WHERE scan_id = ?", (scan_id,)).fetchall()
        result["ips"] = [dict(r) for r in ip_rows]
        
        time_rows = conn.execute("SELECT * FROM scan_timings WHERE scan_id = ?", (scan_id,)).fetchall()
        result["timings"] = {r["stage"]: r["seconds"] for r in time_rows}
        
        return result

def list_scans() -> List[Dict[str, Any]]:
    with get_db() as conn:
        rows = conn.execute("""
            SELECT s.id, s.domain, s.status, s.started_at,
                   (SELECT COUNT(*) FROM subdomains WHERE scan_id = s.id) as subdomains_count,
                   (SELECT COUNT(*) FROM ip_information WHERE scan_id = s.id) as ips_count
            FROM scans s
            ORDER BY s.id DESC
        """).fetchall()
        return [dict(r) for r in rows]

def delete_scan(scan_id: int):
    with get_db() as conn:
        conn.execute("DELETE FROM scans WHERE id = ?", (scan_id,))

def get_stats() -> Dict[str, int]:
    with get_db() as conn:
        return {
            "scans": conn.execute("SELECT COUNT(*) FROM scans").fetchone()[0],
            "subdomains": conn.execute("SELECT COUNT(*) FROM subdomains").fetchone()[0],
            "ips": conn.execute("SELECT COUNT(*) FROM ip_information").fetchone()[0],
            "dns_records": conn.execute("SELECT COUNT(*) FROM dns_records").fetchone()[0],
        }
