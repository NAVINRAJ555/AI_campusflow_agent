from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.session import Base
from app.models.enums import ConflictType

class NegotiationCase(Base):
    __tablename__ = "negotiation_cases"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="OPEN", nullable=False)  # OPEN, RESOLVED, FAILED
    conflict_type = Column(SQLEnum(ConflictType), default=ConflictType.TIME_OVERLAP, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    booking = relationship("Booking", back_populates="negotiation_cases")
    options = relationship("NegotiationOption", back_populates="negotiation_case", cascade="all, delete-orphan")

class NegotiationOption(Base):
    __tablename__ = "negotiation_options"

    id = Column(Integer, primary_key=True, index=True)
    negotiation_case_id = Column(Integer, ForeignKey("negotiation_cases.id", ondelete="CASCADE"), nullable=False)
    option_data = Column(Text, nullable=False)  # JSON-encoded candidate plan
    score = Column(Float, default=0.0, nullable=False)
    selected = Column(Boolean, default=False, nullable=False)

    negotiation_case = relationship("NegotiationCase", back_populates="options")
