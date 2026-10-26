# CivicCare — Tamil Nadu-style Civic Grievance Portal

Matches the flow: **Register/Login → Select Role (Citizen/Admin) → Citizen submits a
complaint (category, location, priority, photo, description) → FastAPI backend →
PostgreSQL → Admin verifies → assigns → updates status → resolves (SMS sent to
citizen) → Citizen tracks status**.

## ⚠️ Important — why buttons might look "broken"

This app has a real Python + PostgreSQL backend behind it. **It will not work if you
just open `index.html` by double-clicking it or opening it from a downloaded file /
Android file manager** (you'll see a URL like `content://...` or `file://...` in the
address bar, and every button will fail with an error like *"Can't reach the CivicCare
server"*). You must run the backend (`uvicorn main:app`) and open the app through the
URL it serves — e.g. `http://localhost:8000` on the same machine, or
`http://<your-computer's-LAN-IP>:8000` from your phone on the same Wi‑Fi. See **Setup**
below.

## What's new in this version

1. **Admin sees everything at a glance:** total complaint count, complaints by
   priority/status (dashboard stat cards), each citizen's **name, phone number, and
   location**, and a **photo of the issue** if one was uploaded.
2. **Photo upload:** citizens can attach a photo when submitting a complaint
   (`POST /api/complaints`, multipart form). Stored in `backend/uploads/` and served
   at `/uploads/<filename>`.
3. **SMS to the citizen:** whenever an admin/staff member changes a complaint's status
   (assigned, in progress, resolved, etc.), `backend/notifications.py` sends an SMS to
   the phone number the citizen registered with. It runs in **demo mode** by default
   (prints the message to the server console) so you don't need a paid account to
   demo it — fill in `TWILIO_ACCOUNT_SID` / `TWILIO_AUTH_TOKEN` / `TWILIO_FROM_NUMBER`
   in `.env` to send real SMS via Twilio.
4. **Tamil Nadu government styling:** deep red (#A31F22) and gold (#F2B705) theme,
   an original circular seal with a stylised temple gopuram (not the real State
   Emblem — see note below), bilingual "Government of Tamil Nadu / தமிழ்நாடு அரசு"
   header, and department-style labelling ("Municipal Administration & Water Supply
   Dept. · Civic Grievance Portal").
5. **Fixed a real CORS bug** (`allow_credentials=True` + `allow_origins=["*"]` is
   rejected by browsers) and a **bcrypt/passlib version mismatch** that broke
   register/login — both are why "login/register weren't working" previously.

### Why not the real Tamil Nadu government emblem?

The State Emblem and official government logos are legally protected symbols, and
using them on an unofficial app would make it look like an actual government service
(which isn't appropriate for a demo/academic project). I designed an original seal in
the same visual language (red/gold, circular seal, temple architecture) instead, and
added a disclaimer footer on the login page. Swap `frontend/assets/logo.svg` for your
own artwork if your institution provides an approved logo to use.

## Priority logic

| Category | Priority |
|---|---|
| Electricity | **High** |
| Water Supply | **High** |
| Public Safety | **High** |
| Road / Pothole | Medium |
| Garbage / Sanitation | Medium |
| Sewage / Drainage | M edium |
| Streetlight | Low |
| Noise Pollution | Low |
| Others | Low |

Auto-assigned on submission; admins can override it at verification time. The admin
queue is always sorted High → Medium → Low.

## Tech stack

- **Backend:** Python, FastAPI, SQLAlchemy ORM, PostgreSQL, JWT auth (python-jose),
  bcrypt password hashing (passlib), file uploads (python-multipart), SMS (Twilio, optional)
- **Frontend:** Plain HTML + Tailwind CSS (CDN) + Alpine.js (CDN) — no build step needed
- **Roles:** Citizen, Admin, Staff (field staff complaints get assigned to)

## Project structure

```
civiccare/
├── backend/
│   ├── main.py                 # FastAPI app entrypoint, serves frontend + API + uploads
│   ├── config.py                # env-based settings (DB, JWT, Twilio, uploads)
│   ├── database.py              # SQLAlchemy engine/session
│   ├── models.py                # User, Complaint (+ image_path), ComplaintHistory, priority map
│   ├── schemas.py                # Pydantic request/response models
│   ├── auth.py                    # JWT + password hashing + role guards
│   ├── notifications.py           # SMS on status change / resolve (Twilio, with demo-mode fallback)
│   ├── seed.py                     # creates demo admin/staff/citizen + sample complaints
│   ├── requirements.txt
│   ├── .env.example
│   ├── uploads/                    # citizen-submitted complaint photos land here
│   └── routers/
│       ├── auth_router.py         # /api/auth/register, /login, /me
│       └── complaints_router.py   # citizen + admin complaint endpoints, image upload, SMS triggers
└── frontend/
    ├── index.html                 # login / register (role select)
    ├── citizen_dashboard.html     # submit complaint (+ photo) + track status timeline
    ├── admin_dashboard.html       # priority-sorted queue: phone/location/photo, verify/assign/resolve
    ├── assets/logo.svg            # original Tamil Nadu-style civic seal
    └── js/api.js                  # shared fetch wrapper (JSON + multipart), auth storage, badges
```

## Setup

### 1. Create the PostgreSQL database

```sql
CREATE DATABASE civiccare_db;
CREATE USER civiccare_user WITH PASSWORD 'civiccare_pass';
GRANT ALL PRIVILEGES ON DATABASE civiccare_db TO civiccare_user;
```

### 2. Configure environment

```bash
cd backend
cp .env.example .env
# edit .env if your DATABASE_URL / SECRET_KEY differ, and optionally add Twilio creds
```

### 3. Install dependencies

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Seed demo data (creates tables + demo accounts + sample complaints)

```bash
python seed.py
```

This prints three demo logins:
- **Admin:** admin@civiccare.local / Admin@123
- **Staff:** staff@civiccare.local / Staff@123
- **Citizen:** citizen@civiccare.local / Citizen@123

### 5. Run the server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- On the same computer: open **http://localhost:8000**
- On your phone (same Wi‑Fi as the computer running the server): find the computer's
  LAN IP (e.g. `192.168.1.23` via `ipconfig` / `ifconfig`) and open
  **http://192.168.1.23:8000** in the phone's browser — do **not** open the HTML file
  itself.
- Interactive API docs: **http://localhost:8000/docs**

## Demo walkthrough

1. Open the app URL → log in as the **citizen** demo account.
2. Click **+ New Complaint** → pick "Electricity" (auto-tagged High priority) → attach
   a photo → submit.
3. Log out, log back in as **admin**. The stat cards show total/high-priority/in-progress/
   resolved counts. The queue shows the complaint at the top with the citizen's name,
   phone number, location, and photo thumbnail.
4. Click it → **Verify** → **Assign** to the demo staff member → **Mark In Progress** →
   **Resolve** with notes. Check the server console/log — you'll see `[SMS DEMO MODE]`
   lines showing exactly what would have been texted to the citizen at each step.
5. Log back in as the citizen → open the complaint → the timeline shows every status
   change with timestamps.

## Notes for your viva / presentation

- `Base.metadata.create_all()` auto-creates tables for this academic project; use
  Alembic migrations in a production system.
- Passwords are hashed with bcrypt, never stored in plain text.
- JWT tokens carry `sub` (user id) and `role`; `require_role()` in `auth.py` is the
  RBAC guard used on every protected endpoint.
- `ComplaintHistory` is the audit trail powering "Citizen Tracks Complaint → View
  Status" from the flowchart, and is what each SMS message is built from.
- SMS is abstracted behind `notifications.py` so you can demo the whole flow without
  a paid account, then flip it to live mode by filling in three environment variables.


---

## Latest UI + bug-fix release

**Bug fixes**
- Login showed `[object Object]`: FastAPI sends validation errors as a list of objects and the UI printed them raw.
  `frontend/js/api.js → errorMessageFrom()` now turns any error shape into readable text.
- Root cause of that login failure: `EmailStr` rejected the demo `.local` addresses. `schemas.py` now uses a plain
  email-shape check (`EmailField`), and the `pydantic[email]` extra is no longer required.
- A wrong password (HTTP 401 on login) used to trigger the "session expired" redirect. It now shows inline;
  only 401s on *protected* calls send you back to the login page.

**Interface improvements** (all in `frontend/`, shared styles in `css/theme.css`)
- Radio-style choices everywhere: register role cards, complaint-list filter, admin status filter, admin priority override.
- Down-arrow dropdowns that reveal details: category picker (each option expands to "typical issues"), admin staff picker
  (name + email), admin category filter, priority explainer on the login page, collapsible History and Citizen & location sections.
- Citizen progress tracker (Submitted → Verified → Assigned → In Progress → Resolved), toast confirmations,
  admin search box, show/hide password, keyboard-accessible controls (real radio inputs stay in the DOM).

## How to run (quick)

```bash
# 1. PostgreSQL: create db + user (see Setup above)
cd backend
cp .env.example .env
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python seed.py                                       # tables + demo accounts + sample complaints
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# 2. open http://localhost:8000  (never the .html file directly)
```
Logins: admin@civiccare.local / Admin@123 · staff@civiccare.local / Staff@123 · citizen@civiccare.local / Citizen@123
