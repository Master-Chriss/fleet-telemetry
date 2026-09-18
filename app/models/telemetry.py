import uuid
from datetime import datetime
from sqlalchemy import Float, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class TelemetryLog(Base):
    __tablename__ = "telemetry_logs"

    # Unique transactional row tracking ID
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # Cascade tracking back to our modified device primary key
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("devices.device_id", ondelete="CASCADE"),
        nullable=False
    )

    # Hardware Telemetry Parameters
    battery_percentage: Mapped[float] = mapped_column(Float, nullable=False)
    speed_kmh: Mapped[float] = mapped_column(Float, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    engine_temp_celsius: Mapped[float] = mapped_column(Float, nullable=False)

    # Exact epoch boundary reported from the edge device clock
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)

    # Performance Tuning: Multi-column time-series query indexing layout
    __table_args__ = (
        Index("ix_telemetry_device_recorded_at", "device_id", "recorded_at"),
    )
