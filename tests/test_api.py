import uuid
from datetime import datetime, timezone
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_device_lifecycle(client: AsyncClient):
    unique_code = f"SCOOT-{uuid.uuid4().hex[:6].upper()}"
    payload = {
        "device_code": unique_code,
        "status": "active"
    }

    # 🔥 Fix: Point explicitly to your correct versioned URL path
    response = await client.post("/api/v1/devices", json=payload)
    assert response.status_code == 201
    json_data = response.json()
    assert json_data["device_code"] == unique_code
    assert json_data["status"] == "active"
    assert "device_id" in json_data

    # 🔥 Fix: Point explicitly to your correct versioned URL path
    duplicate_response = await client.post("/api/v1/devices", json=payload)
    assert duplicate_response.status_code == 400
    assert "already registered" in duplicate_response.json()["detail"]


async def test_telemetry_ingestion_pipeline(client: AsyncClient):
    device_payload = {
        "device_code": f"TRACK-{uuid.uuid4().hex[:6].upper()}",
        "status": "active"
    }
    # 🔥 Fix: Point explicitly to your correct versioned URL path
    device_response = await client.post("/api/v1/devices", json=device_payload)
    assert device_response.status_code == 201
    target_device_id = device_response.json()["device_id"]

    telemetry_payload = {
        "device_id": target_device_id,
        "battery_percentage": 88.5,
        "speed_kmh": 22.4,
        "latitude": -1.9441,
        "longitude": 30.0619,
        "engine_temp_celsius": 42.1,
        "recorded_at": datetime.now(timezone.utc).isoformat()
    }

    # 🔥 Fix: Point explicitly to your correct versioned URL path
    ingest_response = await client.post("/api/v1/telemetry/ingest", json=telemetry_payload)
    assert ingest_response.status_code == 202
    assert ingest_response.json()["status"] == "queued"
    assert ingest_response.json()["device_id"] == target_device_id
