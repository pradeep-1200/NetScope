import pytest
import sqlite3
from core.database import get_db, init_db, create_scan, update_scan_status, get_scan, save_dns_records

@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    monkeypatch.setattr("core.database.DB_PATH", db_file)
    init_db()

def test_scan_lifecycle():
    domain = "example.com"
    scan_id = create_scan(domain, "2023-01-01T00:00:00")
    
    scan = get_scan(scan_id)
    assert scan is not None
    assert scan["domain"] == domain
    assert scan["status"] == "running"
    
    update_scan_status(scan_id, "completed", None, "2023-01-01T00:01:00", 60.0)
    
    scan = get_scan(scan_id)
    assert scan["status"] == "completed"
    assert scan["duration_seconds"] == 60.0

def test_save_dns():
    scan_id = create_scan("example.com", "2023-01-01T00:00:00")
    records = {"A": ["1.1.1.1", "2.2.2.2"], "MX": ["mail.example.com"]}
    save_dns_records(scan_id, records)
    
    scan = get_scan(scan_id)
    assert "A" in scan["dns"]["records"]
    assert len(scan["dns"]["records"]["A"]) == 2
