from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_db
from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceResponse

# 🔥 ENSURE THIS IS EXACTLY 'router = ...' (Not api_router, not devices_router)
router = APIRouter(prefix="/devices", tags=["Device Registry"])


@router.post(
    "",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new delivery vehicle"
)
async def register_device(payload: DeviceCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.scalar(
        select(Device).where(Device.device_code == payload.device_code)
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Device '{payload.device_code}' is already registered."
        )

    device = Device(
        device_code=payload.device_code,
        status=payload.status,
    )
    db.add(device)
    await db.commit()
    await db.refresh(device)
    return device


@router.get(
    "",
    response_model=list[DeviceResponse],
    summary="Retrieve all registered vehicles"
)
async def list_devices(status_filter: str | None = None, db: AsyncSession = Depends(get_db)):
    query = select(Device)
    if status_filter:
        query = query.where(Device.status == status_filter)

    result = await db.execute(query)
    return result.scalars().all()
