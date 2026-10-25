import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from database import Base


class UserRole(str, enum.Enum):
    CITIZEN = "citizen"
    ADMIN = "admin"
    STAFF = "staff"


class ComplaintCategory(str, enum.Enum):
    ELECTRICITY = "Electricity"
    WATER_SUPPLY = "Water Supply"
    ROAD_POTHOLE = "Road / Pothole"
    GARBAGE_SANITATION = "Garbage / Sanitation"
    STREETLIGHT = "Streetlight"
    SEWAGE_DRAINAGE = "Sewage / Drainage"
    PUBLIC_SAFETY = "Public Safety"
    NOISE_POLLUTION = "Noise Pollution"
    OTHERS = "Others"


class ComplaintPriority(str, enum.Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class ComplaintStatus(str, enum.Enum):
    SUBMITTED = "Submitted"
    VERIFIED = "Verified"
    ASSIGNED = "Assigned"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    REJECTED = "Rejected"
    CLOSED = "Closed"


# ---------------------------------------------------------------------------
# Category -> Priority mapping (core business rule from the requirement:
# "electricity mean higher priority like that")
# ---------------------------------------------------------------------------
CATEGORY_PRIORITY_MAP = {
    ComplaintCategory.ELECTRICITY: ComplaintPriority.HIGH,
    ComplaintCategory.WATER_SUPPLY: ComplaintPriority.HIGH,
    ComplaintCategory.PUBLIC_SAFETY: ComplaintPriority.HIGH,
    ComplaintCategory.SEWAGE_DRAINAGE: ComplaintPriority.MEDIUM,
    ComplaintCategory.ROAD_POTHOLE: ComplaintPriority.MEDIUM,
    ComplaintCategory.GARBAGE_SANITATION: ComplaintPriority.MEDIUM,
    ComplaintCategory.STREETLIGHT: ComplaintPriority.LOW,
    ComplaintCategory.NOISE_POLLUTION: ComplaintPriority.LOW,
    ComplaintCategory.OTHERS: ComplaintPriority.LOW,
}


def get_priority_for_category(category: ComplaintCategory) -> ComplaintPriority:
    """Auto-assign priority based on complaint category."""
    return CATEGORY_PRIORITY_MAP.get(category, ComplaintPriority.LOW)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(SAEnum(UserRole), default=UserRole.CITIZEN, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    complaints = relationship(
        "Complaint",
        back_populates="citizen",
        foreign_keys="Complaint.citizen_id"
    )


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(SAEnum(ComplaintCategory), nullable=False)
    priority = Column(SAEnum(ComplaintPriority), nullable=False)
    location = Column(String(255), nullable=False)
    status = Column(SAEnum(ComplaintStatus), default=ComplaintStatus.SUBMITTED, nullable=False)

    citizen_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_staff_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    admin_remarks = Column(Text, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    image_path = Column(String(255), nullable=True)  # citizen-uploaded photo of the issue

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    citizen = relationship("User", back_populates="complaints", foreign_keys=[citizen_id])
    assigned_staff = relationship("User", foreign_keys=[assigned_staff_id])
    history = relationship("ComplaintHistory", back_populates="complaint", order_by="ComplaintHistory.timestamp")


class ComplaintHistory(Base):
    """Tracks every status change for the citizen 'track complaint' timeline."""
    __tablename__ = "complaint_history"

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), nullable=False)
    status = Column(SAEnum(ComplaintStatus), nullable=False)
    note = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    complaint = relationship("Complaint", back_populates="history")
