import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class TelemetryIngestCreate(BaseModel):
    """
    Validates incoming high-frequency telemetry requests right at the network edge.
    """
    device_id: uuid.UUID
    battery_percentage: float = Field(..., ge=0.0,
                                      le=100.0, description="Battery capacity left")
    speed_kmh: float = Field(..., ge=0.0, le=250.0,
                             description="Speed calculation in KMH")
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    engine_temp_celsius: float = Field(..., ge=-40.0, le=150.0)
    recorded_at: datetime

    model_config = {
        "frozen": True  # Drop lookup overhead by keeping validated instances immutable
    }


class FleetStatusSummary(BaseModel):
    """
    Schema for formatting high-level dashboard summaries.
    """
    device_id: uuid.UUID
    device_code: str
    status: str
    latest_speed_kmh: float
    latest_battery: float
