from fastapi import APIRouter, Depends, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.schemas.telemetry import TelemetryIngestCreate
from app.models.telemetry import TelemetryLog
from app.services.websocket import socket_manager

router = APIRouter(prefix="/telemetry", tags=["Telemetry Ingestion"])


async def check_vehicle_thresholds(payload: TelemetryIngestCreate) -> None:
    """
    Background worker that runs asynchronously after the client receives a response.
    Analyzes safety margins and pushes instant broadcast alerts to WebSockets.
    """
    alerts = []

    # 1. Check for physical engine anomalies
    if payload.engine_temp_celsius > 100.0:
        alerts.append("CRITICAL_ENGINE_OVERHEAT")
    elif payload.engine_temp_celsius > 80.0:
        alerts.append("WARNING_ENGINE_HIGH_TEMP")

    # 2. Check battery capacity constraints
    if payload.battery_percentage < 15.0:
        alerts.append("CRITICAL_LOW_BATTERY")

    # 3. If any thresholds are breached, broadcast to the dashboard stream instantly
    if alerts:
        alert_payload = {
            "event": "VEHICLE_ALERT",
            "device_id": str(payload.device_id),
            "alerts": alerts,
            "metrics": {
                "battery": payload.battery_percentage,
                "engine_temp": payload.engine_temp_celsius,
                "speed": payload.speed_kmh
            },
            "timestamp": payload.recorded_at.isoformat()
        }
        await socket_manager.broadcast(alert_payload)


@router.post(
    "/ingest",
    status_code=status.HTTP_202_ACCEPTED,
    summary="High-frequency edge data ingestion"
)
async def ingest_device_telemetry(
    payload: TelemetryIngestCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Accepts high-frequency metrics from delivery vehicles.
    Saves to the database asynchronously and handles alerts via background workers.
    """
    # 1. Transform incoming validation schema into our database record
    new_log = TelemetryLog(
        device_id=payload.device_id,
        battery_percentage=payload.battery_percentage,
        speed_kmh=payload.speed_kmh,
        latitude=payload.latitude,
        longitude=payload.longitude,
        engine_temp_celsius=payload.engine_temp_celsius,
        recorded_at=payload.recorded_at
    )

    # 2. Enqueue the asynchronous persistence write
    db.add(new_log)
    await db.commit()  # Flush transaction over the non-blocking async pg wire

    # 3. Offload anomaly evaluation to background loop to maximize router speed
    background_tasks.add_task(check_vehicle_thresholds, payload)

    return {
        "status": "queued",
        "device_id": payload.device_id
    }
