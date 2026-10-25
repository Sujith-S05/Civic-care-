from datetime import datetime
from typing import Optional, List, Annotated
from pydantic import BaseModel, Field

from models import UserRole, ComplaintCategory, ComplaintPriority, ComplaintStatus

# Plain-syntax email check (one "@", a dot in the domain, no whitespace).
# Deliberately NOT pydantic's EmailStr: email-validator rejects reserved TLDs
# such as ".local" (our demo accounts, e.g. admin@civiccare.local), which made
# login fail with a validation error. Auth should depend on shape, not on
# whether a domain is "real".
EmailField = Annotated[str, Field(min_length=5, max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")]


# ---------------- Auth / User ----------------

class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120)
    email: EmailField
    password: str = Field(..., min_length=6)
    phone: Optional[str] = None
    role: UserRole = UserRole.CITIZEN  # citizen or staff; admin created via seed only


class UserLogin(BaseModel):
    email: EmailField
    password: str


class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailField
    phone: Optional[str]
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------------- Complaint ----------------

class ComplaintCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=150)
    description: str = Field(..., min_length=10)
    category: ComplaintCategory
    location: str = Field(..., min_length=3, max_length=255)


class ComplaintHistoryOut(BaseModel):
    status: ComplaintStatus
    note: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


class ComplaintOut(BaseModel):
    id: int
    title: str
    description: str
    category: ComplaintCategory
    priority: ComplaintPriority
    location: str
    status: ComplaintStatus
    admin_remarks: Optional[str]
    resolution_notes: Optional[str]
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]
    citizen_id: int
    citizen_name: Optional[str] = None
    citizen_phone: Optional[str] = None
    assigned_staff_id: Optional[int]
    assigned_staff_name: Optional[str] = None
    history: List[ComplaintHistoryOut] = []

    class Config:
        from_attributes = True


class ComplaintVerify(BaseModel):
    remarks: Optional[str] = None
    override_priority: Optional[ComplaintPriority] = None


class ComplaintAssign(BaseModel):
    staff_id: int
    remarks: Optional[str] = None


class ComplaintStatusUpdate(BaseModel):
    status: ComplaintStatus
    note: Optional[str] = None


class ComplaintResolve(BaseModel):
    resolution_notes: str = Field(..., min_length=5)
