import asyncio
import random
import uuid
from datetime import datetime, timezone
import httpx
from app.core.config import settings

# 1. Targeting variables mapping directly to our running development app node
TARGET_URL = f"http://127.0.0.1:8000{settings.API_V1_STR}/telemetry/ingest"
HEADERS = {"X-API-Key": settings.API_KEY_SECRET}

# Mocking static device registry IDs to simulate persistent fleet tracked assets
MOCK_SCOOTER_IDS = [uuid.uuid4() for _ in range(5)]

async def simulate_single_scooter_ping(client: httpx.AsyncClient, scooter_id: uuid.UUID) -> None:
    """
    Simulates a continuous state broadcast packet coming from a single scooter edge node.
    """
    # Randomly inject extreme scenarios to force background worker threshold triggers
    is_anomaly = random.random() < 0.15 # 15% chance to force an engine overheat warning
    
    payload = {
        "device_id": str(scooter_id),
        "battery_percentage": random.uniform(5.0, 14.0) if is_anomaly else random.uniform(40.0, 99.0),
        "speed_kmh": random.uniform(0.0, 45.0),
        "latitude": 45.0 + random.uniform(-0.01, 0.01),
        "longitude": -122.0 + random.uniform(-0.01, 0.01),
        "engine_temp_celsius": random.uniform(101.0, 120.0) if is_anomaly else random.uniform(35.0, 75.0),
        "recorded_at": datetime.now(timezone.utc).isoformat()
    }

    try:
        response = await client.post(TARGET_URL, json=payload, headers=HEADERS)
        if response.status_code == 202:
            print(f"📡 [Scooter {str(scooter_id)[:6]}] Ingest Accepted -> "
                  f"Temp: {payload['engine_temp_celsius']:.1f}°C, Batt: {payload['battery_percentage']:.1f}%")
        else:
            print(f"❌ Ingestion Rejected: Code {response.status_code}")
    except Exception as e:
        print(f"💥 Network connection failed: {e}")

async def run_simulation_loop():
    """
    Main driver managing parallel device operations.
    """
    print(f"🚀 Initializing Concurrent Fleet Telemetry Simulation...")
    print(f"📡 Target Ingestion URL: {TARGET_URL}")
    print(f"📦 Simulating {len(MOCK_SCOOTER_IDS)} concurrent edge delivery vehicles. Press Ctrl+C to terminate.")
    
    async with httpx.AsyncClient() as client:
        while True:
            # Generate concurrent execution paths for all mock devices simultaneously
            tasks = [simulate_single_scooter_ping(client, sid) for sid in MOCK_SCOOTER_IDS]
            
            # Execute the concurrent pings together non-blockingly
            await asyncio.gather(*tasks)
            
            # Rest the edge hardware loop before broadcasting the next telemetry intervals
            await asyncio.sleep(2.0)

if __name__ == "__main__":
    try:
        asyncio.run(run_simulation_loop())
    except KeyboardInterrupt:
        print("\n🛑 Fleet simulation execution halted successfully.")
