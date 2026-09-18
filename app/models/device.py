import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Device(Base):
    __tablename__ = "devices"

    # Primary Key utilizing native indexing UUIDs
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # Human-readable custom asset identifier (e.g., "SCOOT-001")
    device_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    # Current fleet operating status boundary
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",  # e.g., active, maintenance, offline
        nullable=False
    )

    # Registration timeline anchor
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
