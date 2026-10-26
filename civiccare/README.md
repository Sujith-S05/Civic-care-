# 🏛️ CivicCare — Smart Community Issue Reporting and Management System

### A web-based civic grievance portal for transparent, efficient, and trackable public issue resolution.

CivicCare is a full-stack web application that enables citizens to report civic problems such as potholes, water supply issues, electricity failures, garbage accumulation, drainage problems, and streetlight faults. Administrators can verify complaints, assign field staff, update statuses, and track resolutions through a centralized dashboard.

> 🎓 **Academic Project | Full-Stack Web Development | Tamil Nadu-Inspired UI**  
> **Note:** CivicCare is an independent academic project and is not affiliated with or endorsed by the Government of Tamil Nadu.

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Technology Stack](#-technology-stack)
- [System Architecture](#-system-architecture)
- [Complaint Workflow](#-complaint-workflow)
- [Project Structure](#-project-structure)
- [Installation and Setup](#-installation-and-setup)
- [Demo Credentials](#-demo-credentials)
- [API Documentation](#-api-documentation)
- [Security](#-security)
- [Future Enhancements](#-future-enhancements)
- [Author](#-author)
- [Contributing](#-contributing)
- [License](#-license)

---

## 📖 Overview

Traditional civic complaint systems may rely on phone calls, paper forms, or direct communication, making it difficult for citizens to track progress and for authorities to manage complaints efficiently.

CivicCare provides a centralized platform where citizens can submit complaints online, monitor their progress, and receive status notifications. Administrators can manage complaints according to their priority and coordinate resolution through assigned staff.

### 🎯 Project Objectives

- Simplify the civic complaint registration process.
- Improve transparency in complaint handling.
- Prioritize urgent public issues.
- Enable authorities to manage and assign complaints efficiently.
- Maintain a history of complaint status changes.
- Provide citizens with clear progress updates.

---

## ✨ Key Features

### 👤 Citizen Portal
- User registration and login.
- Submit complaints with category, location, description, and photo.
- Automatic priority assignment based on complaint category.
- Track complaint status and progress timeline.
- View complaint history and resolution updates.
- Receive SMS notifications when complaint statuses change.

### 🛡️ Admin Dashboard
- View total complaints and status statistics.
- Filter and search complaints.
- Review citizen details, contact numbers, locations, and uploaded photos.
- Verify submitted complaints.
- Override automatically assigned priorities.
- Assign complaints to field staff.
- Update complaint status and add resolution notes.
- View complaint history.

### 🧑‍🔧 Staff Workflow
- Receive assigned complaints.
- Update progress as work proceeds.
- Support the complaint resolution process.

### ⚡ Additional Features
- Role-based access control.
- JWT-based authentication.
- Password hashing.
- Priority-sorted complaint queue.
- Image upload and storage.
- SMS demo mode with optional Twilio integration.
- Responsive, Tamil Nadu-inspired red and gold interface.

---

## 🧰 Technology Stack

| Component | Technology |
|---|---|
| Frontend | HTML5, Tailwind CSS, Alpine.js |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Authentication | JWT, Passlib, bcrypt |
| Data Validation | Pydantic |
| File Uploads | Python Multipart |
| Notifications | Twilio SMS API (optional) |
| API Testing | FastAPI Swagger UI |
| Version Control | Git and GitHub |

---

## 🏗️ System Architecture

```text
          ┌─────────────────────┐
          │   Citizen / Admin   │
          │       / Staff       │
          └──────────┬──────────┘
                     │
                     ▼
          ┌─────────────────────┐
          │   Web Frontend      │
          │ HTML, Tailwind CSS  │
          │     Alpine.js       │
          └──────────┬──────────┘
                     │ HTTP / REST API
                     ▼
          ┌─────────────────────┐
          │   FastAPI Backend   │
          │ Auth and Complaint  │
          │ Management Routers  │
          └───────┬───────┬─────┘
                  │       │
                  ▼       ▼
          ┌────────────┐ ┌────────────┐
          │ PostgreSQL │ │ Image      │
          │ Database   │ │ Storage    │
          └────────────┘ └────────────┘
                  │
                  ▼
          ┌─────────────────────┐
          │ SMS Notifications   │
          │ Demo / Twilio       │
          └─────────────────────┘
```

---

## 🔄 Complaint Workflow

1. Citizen registers or logs in.
2. Citizen submits a complaint with the required details and optional photo.
3. The system assigns an initial priority based on the complaint category.
4. Admin verifies the complaint.
5. Admin assigns the complaint to a staff member.
6. Staff and admin update the complaint status.
7. The citizen receives status notifications.
8. Admin records the resolution, and the citizen can review the complaint history.

### Complaint Statuses

`Submitted → Verified → Assigned → In Progress → Resolved → Closed`

---

## 📊 Priority Management

| Complaint Category | Default Priority |
|---|---|
| Electricity | High |
| Water Supply | High |
| Public Safety | High |
| Road / Pothole | Medium |
| Garbage / Sanitation | Medium |
| Sewage / Drainage | Medium |
| Streetlight | Low |
| Noise Pollution | Low |
| Others | Low |

Administrators can override the default priority when necessary.

---

## 📁 Project Structure

```text
civiccare/
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   ├── notifications.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── uploads/
│   └── routers/
│       ├── auth_router.py
│       └── complaints_router.py
│
├── frontend/
│   ├── index.html
│   ├── citizen_dashboard.html
│   ├── admin_dashboard.html
│   ├── assets/
│   │   └── logo.svg
│   ├── css/
│   │   └── theme.css
│   └── js/
│       └── api.js
│
├── .gitignore
├── LICENSE
└── README.md
```

*The tree above illustrates the expected structure; adjust it to match the files actually present in your repository.*

---

## 🚀 Installation and Setup

### Prerequisites

Install the following before running the project:

- Python 3.10 or a compatible version required by your dependencies.
- PostgreSQL.
- Git.
- A modern web browser.

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd civiccare
```

Replace `YOUR_REPOSITORY_URL` with your actual GitHub repository URL.

### 2. Create the PostgreSQL database

Open pgAdmin or the PostgreSQL terminal and run:

```sql
CREATE DATABASE civiccare_db;
CREATE USER civiccare_user WITH PASSWORD 'civiccare_pass';
GRANT ALL PRIVILEGES ON DATABASE civiccare_db TO civiccare_user;
```

Ensure the configured database user has the required permissions.

### 3. Configure environment variables

Navigate to the backend directory:

```bash
cd backend
```

Create a `.env` file based on `.env.example` and configure your database URL and secret key.

Example configuration:

```env
DATABASE_URL=postgresql://civiccare_user:civiccare_pass@localhost:5432/civiccare_db
SECRET_KEY=replace_with_a_secure_random_secret
```

Configure Twilio credentials only if you want to enable real SMS delivery. Keep `.env` private.

### 4. Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python -m venv venv
source venv/bin/activate
```

### 5. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 6. Initialize demo data

```bash
python seed.py
```

This initializes the database tables and demo data according to the project's seed script.

### 7. Start the backend server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 8. Open the application

| Resource | URL |
|---|---|
| CivicCare application | http://localhost:8000 |
| API documentation | http://localhost:8000/docs |
| Alternative API docs | http://localhost:8000/redoc |

**Important:** Open the application through the running FastAPI server, not by opening `index.html` directly.

---

## 🔐 Demo Credentials

Use these accounts only after successfully initializing the demo database.

| Role | Email | Password |
|---|---|---|
| Admin | `admin@civiccare.local` | `Admin@123` |
| Staff | `staff@civiccare.local` | `Staff@123` |
| Citizen | `citizen@civiccare.local` | `Citizen@123` |

These are local demonstration credentials, not production accounts. Never use the demo passwords in a deployed application.

---

## 📡 API Documentation

CivicCare uses FastAPI to expose REST endpoints for authentication and complaint management.

Explore the available endpoints through Swagger UI:

**http://localhost:8000/docs**

The API includes functionality for:

- User registration and login.
- Retrieving the authenticated user's profile.
- Submitting and viewing complaints.
- Uploading complaint images.
- Administrative complaint verification and assignment.
- Updating complaint statuses.
- Tracking complaint history.

The exact endpoint methods and permissions are defined by the backend routers.

---

## 🔒 Security

Security-related features implemented in the project include:

- Password hashing instead of storing plaintext passwords.
- JWT-based authentication.
- Role-based access control for protected endpoints.
- Request validation using Pydantic.
- Restricted access to administrative operations.

**Before deployment:** Configure strong secrets, protect uploaded files, validate file types and sizes, restrict CORS origins, use HTTPS, and replace demo credentials. Review authentication and authorization logic before exposing the application publicly.

---

## 🛠️ Troubleshooting

| Problem | Suggested Solution |
|---|---|
| `ModuleNotFoundError` | Activate the virtual environment and install `requirements.txt`. |
| Database connection failed | Check PostgreSQL status, database credentials, port, and `.env`. |
| `Address already in use` | Run the application on another available port. |
| Login or registration fails | Check server logs, validation errors, and database configuration. |
| Frontend cannot reach backend | Start Uvicorn and open the server URL. |
| SMS is not delivered | Check demo mode or configure valid Twilio credentials. |

---

## 🚧 Future Enhancements

- Interactive map integration for complaint locations.
- Email and WhatsApp notifications.
- Multilingual support, including Tamil and English.
- Complaint analytics and monthly reports.
- Real-time notifications.
- Duplicate complaint detection.
- Department-wise performance tracking.
- Deployment with HTTPS and production-grade configuration.
- Automated testing and CI/CD integration.

---

## 👨‍💻 Author

**Sujith S**  
B.E. Computer Science and Engineering Student

- GitHub: [@Sujith-S05](https://github.com/Sujith-S05)
- LinkedIn: [Sujith S](https://www.linkedin.com/in/sujith14s/)

Interested in software development, web technologies, and building practical solutions to real-world problems.

---

## 🤝 Contributing

Contributions, suggestions, and bug reports are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Make your changes and test them.
4. Commit and push your changes.
5. Open a pull request describing your improvements.

---

## 📄 License

This project is intended for academic and demonstration purposes.

If you want others to reuse or modify the source code, choose an appropriate open-source license, such as the MIT License, and include its license file in the repository.

---

⭐ **If you find CivicCare useful, consider starring the repository!**

*Built as an academic project to explore full-stack development and improve civic complaint management.*
