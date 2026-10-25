"""
Run with:  python seed.py
Creates the database tables plus a demo admin, a demo staff member,
a demo citizen, and a handful of sample complaints across categories
so the priority sorting is visible immediately in the admin dashboard.
"""
from database import Base, engine, SessionLocal
from models import User, UserRole, Complaint, ComplaintHistory, ComplaintCategory, ComplaintStatus, get_priority_for_category
from auth import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

def get_or_create_user(full_name, email, password, role, phone=None):
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user
    user = User(
        full_name=full_name,
        email=email,
        hashed_password=hash_password(password),
        phone=phone,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# --- Demo accounts ---
admin = get_or_create_user("City Admin", "admin@civiccare.local", "Admin@123", UserRole.ADMIN)
staff = get_or_create_user("Ravi Kumar (Field Staff)", "staff@civiccare.local", "Staff@123", UserRole.STAFF)
citizen = get_or_create_user("Asha Patel", "citizen@civiccare.local", "Citizen@123", UserRole.CITIZEN, "9876543210")

print(f"Admin login:   admin@civiccare.local / Admin@123")
print(f"Staff login:   staff@civiccare.local / Staff@123")
print(f"Citizen login: citizen@civiccare.local / Citizen@123")

# --- Demo complaints across categories, showing auto priority assignment ---
sample_complaints = [
    ("Frequent power outages in Sector 12", ComplaintCategory.ELECTRICITY,
     "Sector 12, Main Road", "Power has been cutting out every evening for a week."),
    ("No water supply since morning", ComplaintCategory.WATER_SUPPLY,
     "Green Park Colony", "Entire street has had no piped water supply since 6 AM."),
    ("Large pothole near school gate", ComplaintCategory.ROAD_POTHOLE,
     "St. Mary's School Road", "Pothole is causing accidents during peak hours."),
    ("Garbage not collected for 5 days", ComplaintCategory.GARBAGE_SANITATION,
     "Lakeview Apartments", "Overflowing bins are attracting pests."),
    ("Streetlight not working", ComplaintCategory.STREETLIGHT,
     "5th Cross, MG Road", "The light near the bus stop has been off for two weeks."),
    ("Loud construction noise at night", ComplaintCategory.NOISE_POLLUTION,
     "Near Central Mall", "Construction work continues past midnight."),
]

if db.query(Complaint).count() == 0:
    for title, category, location, description in sample_complaints:
        priority = get_priority_for_category(category)
        complaint = Complaint(
            title=title,
            description=description,
            category=category,
            priority=priority,
            location=location,
            status=ComplaintStatus.SUBMITTED,
            citizen_id=citizen.id,
        )
        db.add(complaint)
        db.commit()
        db.refresh(complaint)
        db.add(ComplaintHistory(complaint_id=complaint.id, status=ComplaintStatus.SUBMITTED, note="Complaint submitted by citizen"))
        db.commit()
    print(f"Seeded {len(sample_complaints)} demo complaints.")
else:
    print("Complaints already exist, skipping complaint seeding.")

db.close()
print("Seeding complete.")
