from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ScanOptions(BaseModel):
    bruteforce: bool = True
    passive: bool = True
    threads: int = 20

class ScanRequest(BaseModel):
    domain: str = Field(..., max_length=253)
    options: Optional[ScanOptions] = ScanOptions()

class ScanResponse(BaseModel):
    scan_id: int
    status: str

class ProgressResponse(BaseModel):
    stage: str
    percent: int
    status: str
