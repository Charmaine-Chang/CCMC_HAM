# CCMC_HAM Church Management System

**Hamilton Chinese Methodist Church (漢美頓懷恩堂) Church Management System**

Project codename **CCMC_HAM** is a church management platform built on Flask + MySQL. It includes core mechanisms such as **authentication, role-based access control (RBAC), fellowships, dashboards, announcements, and a resource library**, plus church-specific features such as a **video homepage, calendar, event promotion, visitor registration, prayer requests, attendance records, ministry rosters, and statistical reports**.

> This repository contains only the CCMC_HAM church management system; all content unrelated to the original conservation project has been removed.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.13, Flask 3.1 |
| Database | MySQL 8.0, PyMySQL |
| Frontend | Jinja2, Bootstrap 5, Vanilla JS, Chart.js (reports) |
| Authentication | Flask-BCrypt, custom RBAC decorators |
| Email | smtplib (visitor welcome emails, configurable SMTP) |

---

## Features

### Public Portal (no login required)
- **Video homepage**: full-screen video hero in the style of ccmc.nz (supports MP4 / YouTube links; changeable under "Church Settings" in the admin panel)
- Church info, Sunday services (times and locations of two services), fellowship life, ministry activities
- Upcoming public event calendar, church announcements, public prayer wall
- **Visitor registration**: online form + on-site QR code page; automatically sends a welcome email (including church info, fellowship introductions, and contacts) after registration
- Contact us

### Roles & Permissions (after login)
| Role | Permissions |
|---|---|
| System Admin | Full access: member & role management, church settings, fellowship/ministry management, events, announcements, visitors, attendance, rosters, reports |
| Deacon / Coordinator | Publish and edit events, announcements, and resources; follow up visitors; record attendance and view reports; manage ministry rosters; manage fellowships; update prayer statuses |
| Service Staff | Record attendance, view/confirm their own roster duties, view calendar and announcements, submit prayer requests |
| Member | View calendar/announcements/prayers/resources/fellowships, join fellowships, view their own roster duties, maintain their profile |

### Management Modules
- **Calendar**: month view + event list + event detail; supports categories (Sunday Service / Prayer Meeting / Fellowship / Outreach / Ministry / Special Service)
- **Event Promotion**: publish church announcements and event promotions, grouped by fellowship
- **Prayer Requests**: submit, public/private, status tracking (Pending / In Progress / Answered)
- **Visitor Management**: registration list, status tracking (New / Contacted / Joined), notes, CSV export
- **Attendance Records**: batch entry by date/event (ushers can paste name lists directly), attendance reports
- **Ministry Rosters**: schedule by date/event/ministry team (usher, pianist, scripture reader, sound/AV, etc.); service staff can confirm their duties
- **Fellowships & Ministries**: fellowship info management, member/leader management, join/leave fellowships
- **Resource Library**: publish and search hymns, scriptures, testimonies, and materials
- **Statistical Reports**: visitor statistics by month/status, attendance trend charts, fellowship size distribution
- **System Administration**: member accounts with roles/status, church info / homepage video / SMTP settings

---

## Quick Start

### Requirements
- Python 3.13+
- MySQL 8.0 (local)

### 1. Install Dependencies

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 2. Configure MySQL

Edit `CCMC_HAM/connect_local.py` and fill in your local MySQL username and password:

```python
dbuser = "root"
dbpass = "your password"
dbhost = "127.0.0.1"
dbport = 3306
dbname = "ccmc_ham"
```

Create the database and import the schema and seed data (skip if already imported):

```bash
mysql -u root -p -e "CREATE DATABASE ccmc_ham CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p --default-character-set=utf8mb4 ccmc_ham < sql/ccmc_create_database.sql
mysql -u root -p --default-character-set=utf8mb4 ccmc_ham < sql/ccmc_populate_database.sql
```

### 3. Run

```bash
flask run          # or python app.py
```

Open http://127.0.0.1:5005

### Demo Accounts (password for all accounts: `Password123!`)

| Username | Role |
|---|---|
| `admin` | System Admin |
| `coord_chen` | Deacon / Coordinator |
| `op_lin` | Service Staff |
| `member_wang` | Member |

---

## Verification

```bash
python scripts/smoke_test.py    # Smoke test: public pages + role permissions + CRUD flows
```

Data created during the test can be cleaned up with `scripts/cleanup_smoke.sql`, or you can simply re-import the seed data to restore the initial state.

---

## Directory Structure

```
CCMC_HAM/                 # Church management system (main project package)
  auth/                   # Login / registration / profile
  main/                   # Public portal (video homepage, visitor registration, QR code)
  dashboard/              # Role-based dashboards
  events/                 # Calendar
  announcements/          # Event promotion / announcements
  prayer/                 # Prayer requests
  visitors/               # Visitor management
  attendance/             # Attendance records
  rosters/                # Ministry rosters
  fellowships/            # Fellowships & ministries
  resources/              # Hymns / scriptures / testimonies / materials
  reports/                # Statistical reports
  admin/                  # Member permissions & church settings
  shared/                 # RBAC decorators, etc.
  templates/ static/      # Templates and frontend assets
sql/ccmc_*.sql            # Database schema and seed data
scripts/                  # Smoke test and cleanup scripts
```