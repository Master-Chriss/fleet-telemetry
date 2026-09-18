import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class DeviceBase(BaseModel):
    device_code: str = Field(..., min_length=3,
                             max_length=50, examples=["SCOOT-001"])
    status: Literal["active", "maintenance", "offline"] = "active"


class DeviceCreate(DeviceBase):
    """Payload for registering a brand-new device."""
    pass


class DeviceResponse(DeviceBase):
    """Saves outgoing validation footprint, returning the full database state to clients."""
    device_id: uuid.UUID
    created_at: datetime

    model_config = {
        # Converts SQLAlchemy models directly into serialization patterns
        "from_attributes": True
    }
