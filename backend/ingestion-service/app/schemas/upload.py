from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class UploadResponse(BaseModel):
    file_id: str
    filename: str
    size: int
    upload_time: datetime
    status: str
    metadata: Optional[dict] = None

class UploadStatus(BaseModel):
    status: str
    message: str
    details: Optional[dict] = None
