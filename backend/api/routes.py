from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from datetime import datetime
import os
from pathlib import Path

from api.schemas import ScanRequest, ScanResponse, ProgressResponse
from core.database import create_scan, get_scan, list_scans, delete_scan, get_stats
from core.scanner import run_scan, get_progress
from utils.validators import is_valid_domain, normalize_domain
from reports.report_generator import generate_html_report, generate_json_report

router = APIRouter()

RUNNING_DOMAINS = set()

def background_scan_task(domain: str, scan_id: int, options: dict):
    try:
        run_scan(domain, scan_id=scan_id, options=options)
    finally:
        RUNNING_DOMAINS.discard(domain)

@router.post("/scans", response_model=ScanResponse)
def start_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    domain = normalize_domain(request.domain)
    
    if not is_valid_domain(domain):
        raise HTTPException(status_code=400, detail="Invalid domain format")
        
    if domain in RUNNING_DOMAINS:
        raise HTTPException(status_code=400, detail="A scan is already running for this domain")
        
    scan_id = create_scan(domain, datetime.utcnow().isoformat())
    RUNNING_DOMAINS.add(domain)
    
    background_tasks.add_task(background_scan_task, domain, scan_id, request.options.model_dump())
    
    return {"scan_id": scan_id, "status": "running"}

@router.get("/scans", response_model=list)
def get_history():
    return list_scans()

@router.get("/scans/{scan_id}")
def get_scan_result(scan_id: int):
    scan = get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan

@router.get("/scans/{scan_id}/progress", response_model=ProgressResponse)
def get_scan_progress(scan_id: int):
    scan = get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    if scan["status"] == "running":
        return get_progress(scan_id)
    else:
        return {"stage": "completed", "percent": 100, "status": scan["status"]}

@router.delete("/scans/{scan_id}")
def delete_scan_endpoint(scan_id: int):
    scan = get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    delete_scan(scan_id)
    return {"status": "deleted"}

@router.get("/scans/{scan_id}/report")
def get_scan_report(scan_id: int, format: str = "html"):
    scan = get_scan(scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    if scan["status"] == "running":
        raise HTTPException(status_code=400, detail="Scan is still running")
        
    if format == "html":
        path = generate_html_report(scan_id)
        return FileResponse(path, media_type="text/html", filename=f"report_{scan['domain']}.html")
    elif format == "json":
        path = generate_json_report(scan_id)
        return FileResponse(path, media_type="application/json", filename=f"report_{scan['domain']}.json")
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Use 'html' or 'json'")

@router.get("/stats")
def get_dashboard_stats():
    return get_stats()
