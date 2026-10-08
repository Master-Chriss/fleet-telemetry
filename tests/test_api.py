import uuid
from datetime import datetime, timezone
import pytest
from httpx import AsyncClient
from app.core.config import settings

# Inform pytest-asyncio that all tests in this file are async operations
pytestmark = pytest.mark.asyncio

# Global auth header constructed dynamically from our cached configuration engine
AUTH_HEADERS = {"X-API-Key": settings.API_KEY_SECRET}


async def test_device_lifecycle(client: AsyncClient):
    """
    Verifies that an administrator can register a new device cleanly,
    and blocks duplicate registrations of the same device code.
    """
    unique_code = f"SCOOT-{uuid.uuid4().hex[:6].upper()}"
    payload = {
        "device_code": unique_code,
        "status": "active"
    }

    # 1. Test Successful Creation
    response = await client.post("/api/v1/devices", json=payload)
    assert response.status_code == 201
    json_data = response.json()
    assert json_data["device_code"] == unique_code
    assert json_data["status"] == "active"
    assert "device_id" in json_data

    # 2. Test Rejection of Duplicate Records
    duplicate_response = await client.post("/api/v1/devices", json=payload)
    assert duplicate_response.status_code == 400
    assert "already registered" in duplicate_response.json()["detail"]


async def test_telemetry_ingestion_pipeline(client: AsyncClient):
    """
    Registers a scooter asset and verifies that incoming high-frequency telemetry 
    metrics are safely parsed and accepted by the ingestion endpoint when signed.
    """
    # 1. Bootstrap a registered device asset identity
    device_payload = {
        "device_code": f"TRACK-{uuid.uuid4().hex[:6].upper()}",
        "status": "active"
    }
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

    # 2. Test that a request WITHOUT headers fails with a 403
    unauthorized_response = await client.post("/api/v1/telemetry/ingest", json=telemetry_payload)
    assert unauthorized_response.status_code == 403

    # 3. Test that a request WITH valid headers passes with a 202
    ingest_response = await client.post(
        "/api/v1/telemetry/ingest",
        json=telemetry_payload,
        headers=AUTH_HEADERS  # 🔥 Passing our secure validation keys
    )
    assert ingest_response.status_code == 202
    assert ingest_response.json()["status"] == "queued"
    assert ingest_response.json()["device_id"] == target_device_id
