import os
import uuid
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import case

from database import get_db
from config import settings
from models import (
    User, UserRole, Complaint, ComplaintHistory,
    ComplaintStatus, ComplaintPriority, ComplaintCategory, get_priority_for_category
)
from schemas import (
    ComplaintOut, ComplaintVerify, ComplaintAssign,
    ComplaintStatusUpdate, ComplaintResolve
)
from auth import get_current_user, require_role
from notifications import notify_status_change, notify_resolved

router = APIRouter(prefix="/api/complaints", tags=["complaints"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}

# Used to sort complaints so High priority always surfaces first for admins
PRIORITY_SORT_ORDER = case(
    (Complaint.priority == ComplaintPriority.HIGH, 0),
    (Complaint.priority == ComplaintPriority.MEDIUM, 1),
    (Complaint.priority == ComplaintPriority.LOW, 2),
    else_=3,
)


def _to_out(c: Complaint) -> ComplaintOut:
    out = ComplaintOut.model_validate(c)
    out.citizen_name = c.citizen.full_name if c.citizen else None
    out.citizen_phone = c.citizen.phone if c.citizen else None
    out.assigned_staff_name = c.assigned_staff.full_name if c.assigned_staff else None
    out.image_url = f"/uploads/{c.image_path}" if c.image_path else None
    return out


def _add_history(db: Session, complaint: Complaint, status_: ComplaintStatus, note: Optional[str] = None):
    entry = ComplaintHistory(complaint_id=complaint.id, status=status_, note=note)
    db.add(entry)


def _save_image(image: Optional[UploadFile]) -> Optional[str]:
    if image is None or not image.filename:
        return None
    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG or WEBP images are allowed")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(image.filename)[1] or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)

    contents = image.file.read()
    if len(contents) > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"Image must be under {settings.MAX_UPLOAD_MB}MB")

    with open(filepath, "wb") as f:
        f.write(contents)
    return filename


# --------------------------- CITIZEN ENDPOINTS ---------------------------

@router.post("", response_model=ComplaintOut, status_code=status.HTTP_201_CREATED)
def submit_complaint(
    title: str = Form(...),
    description: str = Form(...),
    category: ComplaintCategory = Form(...),
    location: str = Form(...),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CITIZEN)),
):
    # Priority is auto-derived from category (e.g. Electricity -> High)
    priority = get_priority_for_category(category)
    image_filename = _save_image(image)

    complaint = Complaint(
        title=title,
        description=description,
        category=category,
        priority=priority,
        location=location,
        status=ComplaintStatus.SUBMITTED,
        citizen_id=current_user.id,
        image_path=image_filename,
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    _add_history(db, complaint, ComplaintStatus.SUBMITTED, "Complaint submitted by citizen")
    db.commit()
    db.refresh(complaint)

    return _to_out(complaint)


@router.get("/mine", response_model=List[ComplaintOut])
def my_complaints(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.CITIZEN)),
):
    complaints = (
        db.query(Complaint)
        .filter(Complaint.citizen_id == current_user.id)
        .order_by(Complaint.created_at.desc())
        .all()
    )
    return [_to_out(c) for c in complaints]


@router.get("/{complaint_id}", response_model=ComplaintOut)
def get_complaint(
    complaint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    # Citizens may only view their own complaint; admin/staff can view all
    if current_user.role == UserRole.CITIZEN and complaint.citizen_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this complaint")

    return _to_out(complaint)


# --------------------------- ADMIN ENDPOINTS ---------------------------

@router.get("", response_model=List[ComplaintOut])
def list_all_complaints(
    status_filter: Optional[ComplaintStatus] = None,
    category_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.STAFF)),
):
    query = db.query(Complaint)
    if status_filter:
        query = query.filter(Complaint.status == status_filter)
    if category_filter:
        query = query.filter(Complaint.category == category_filter)

    # High priority complaints (e.g. Electricity, Water) surface first,
    # then ordered by oldest first within the same priority
    complaints = query.order_by(PRIORITY_SORT_ORDER, Complaint.created_at.asc()).all()
    return [_to_out(c) for c in complaints]


@router.patch("/{complaint_id}/verify", response_model=ComplaintOut)
def verify_complaint(
    complaint_id: int,
    payload: ComplaintVerify,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    if complaint.status != ComplaintStatus.SUBMITTED:
        raise HTTPException(status_code=400, detail="Only submitted complaints can be verified")

    complaint.status = ComplaintStatus.VERIFIED
    if payload.remarks:
        complaint.admin_remarks = payload.remarks
    if payload.override_priority:
        complaint.priority = payload.override_priority  # admin can escalate/de-escalate

    db.commit()
    db.refresh(complaint)
    _add_history(db, complaint, ComplaintStatus.VERIFIED, payload.remarks or "Verified by admin")
    db.commit()
    db.refresh(complaint)
    return _to_out(complaint)


@router.patch("/{complaint_id}/assign", response_model=ComplaintOut)
def assign_complaint(
    complaint_id: int,
    payload: ComplaintAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    if complaint.status not in (ComplaintStatus.VERIFIED, ComplaintStatus.ASSIGNED):
        raise HTTPException(status_code=400, detail="Complaint must be verified before assignment")

    staff = db.query(User).filter(User.id == payload.staff_id, User.role == UserRole.STAFF).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")

    complaint.assigned_staff_id = staff.id
    complaint.status = ComplaintStatus.ASSIGNED
    if payload.remarks:
        complaint.admin_remarks = payload.remarks

    db.commit()
    db.refresh(complaint)
    _add_history(db, complaint, ComplaintStatus.ASSIGNED, f"Assigned to {staff.full_name}")
    db.commit()
    db.refresh(complaint)
    notify_status_change(complaint.citizen.phone, complaint.citizen.full_name, complaint.title, "Assigned to field staff")
    return _to_out(complaint)


@router.patch("/{complaint_id}/status", response_model=ComplaintOut)
def update_status(
    complaint_id: int,
    payload: ComplaintStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.STAFF)),
):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    complaint.status = payload.status
    if payload.status == ComplaintStatus.RESOLVED:
        complaint.resolved_at = datetime.utcnow()

    db.commit()
    db.refresh(complaint)
    _add_history(db, complaint, payload.status, payload.note)
    db.commit()
    db.refresh(complaint)
    notify_status_change(complaint.citizen.phone, complaint.citizen.full_name, complaint.title, payload.status.value)
    return _to_out(complaint)


@router.patch("/{complaint_id}/resolve", response_model=ComplaintOut)
def resolve_complaint(
    complaint_id: int,
    payload: ComplaintResolve,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.STAFF)),
):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    complaint.status = ComplaintStatus.RESOLVED
    complaint.resolution_notes = payload.resolution_notes
    complaint.resolved_at = datetime.utcnow()

    db.commit()
    db.refresh(complaint)
    _add_history(db, complaint, ComplaintStatus.RESOLVED, payload.resolution_notes)
    db.commit()
    db.refresh(complaint)
    # SMS the citizen who filed the complaint that it has been resolved
    notify_resolved(complaint.citizen.phone, complaint.citizen.full_name, complaint.title)
    return _to_out(complaint)


@router.get("/meta/staff-list")
def list_staff(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    staff = db.query(User).filter(User.role == UserRole.STAFF).all()
    return [{"id": s.id, "full_name": s.full_name, "email": s.email} for s in staff]


@router.get("/meta/dashboard-stats")
def dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.STAFF)),
):
    total = db.query(Complaint).count()
    by_status = {}
    for s in ComplaintStatus:
        by_status[s.value] = db.query(Complaint).filter(Complaint.status == s).count()
    by_priority = {}
    for p in ComplaintPriority:
        by_priority[p.value] = db.query(Complaint).filter(Complaint.priority == p).count()
    return {"total": total, "by_status": by_status, "by_priority": by_priority}
