from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: str
    incident_type: str
    status: str
    description: Optional[str] = None
    opened_at: datetime
    resolved_at: Optional[datetime] = None
