# Local Tailor Connect (🧵 TailorConnect)

Modernizing the traditional tailoring and alteration experience with smart technology.

---

## 🌟 Features

- **Artisan Discovery & Intelligent Matching**: Discover neighborhood master tailors based on garment specialization, city/area, customer reviews, verified artisan status, and price ranges.
- **Digital Measurement Vault**: Save and manage reusable measurement profiles (chest, waist, hip, shoulder, sleeve, neck, inseam, height, and fit preferences) to place orders without repeating physical measurement sessions.
- **Structured Order Lifecycle Tracking**: Follow each garment through real-time stages:
  1. `pending` (Awaiting tailor quotation)
  2. `quoted` (Digital price quote and target completion date provided)
  3. `confirmed` (Customer accepted quotation and measurements verified)
  4. `cutting` (Fabric cutting in progress)
  5. `stitching` (Tailoring & assembly)
  6. `alteration` (Fitting adjustments)
  7. `quality_check` (Inspection)
  8. `ready` (Ready for workshop pickup or home delivery)
  9. `delivered` (Completed & customer feedback enabled)
- **Digital Quotations & Direct Messaging**: Transparent pricing breakdown and built-in chat for fabric queries and customization details.
- **Ratings & Reviews System**: Verified customer reviews update tailor ratings in real time.
- **Dedicated Multi-Role Portals**:
  - **Customer Portal**: Search tailors, create orders, manage digital measurements, track lifecycle progress, chat with tailors, write reviews.
  - **Tailor Studio Portal**: Production order queue, stage advancement updater, quotation manager, studio profile customizer, review metrics.
  - **Admin Console**: User directory, studio verification badge manager, platform order oversight, review moderation.

---

## 🛠 Tech Stack

- **Backend**: Python 3.10+, Flask 3.1, Flask-SQLAlchemy 3.1, Flask-Login 0.6
- **Database**: MySQL 8.0+ (via PyMySQL) / SQLite for local development
- **Frontend**: Semantic HTML5, Vanilla CSS Design System with dark glassmorphism aesthetic, Vanilla JavaScript (no external runtime dependencies)
- **Typography**: Google Fonts (Outfit & Plus Jakarta Sans)

---

## 🚀 Quick Setup & Installation

### 1. Clone & Navigate
```bash
cd local-tailor-connect
```

### 2. Activate Virtual Environment
On Windows:
```bash
.\venv\Scripts\activate
```

On Linux/macOS:
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Check `.env` and set your preferred database URL:
```env
# For MySQL:
DATABASE_URL=mysql+pymysql://root:password@localhost/local_tailor_connect

# For SQLite (instant zero-config local run):
# DATABASE_URL=sqlite:///local_tailor_connect.db
```

### 5. Initialize Database
If using MySQL:
```bash
mysql -u root -p < database.sql
```

Or allow SQLAlchemy to auto-create tables on launch:
```bash
python app.py
```

---

## 🔐 Default Demo Accounts

If initializing using `database.sql`:
- **Admin**: `admin@tailor.com` / `password123`
- **Customer**: `arjun@example.com` / `password123`
- **Tailor**: `ravi@tailor.com` / `password123`

You can also register new customer and tailor accounts immediately through `/auth/register`.

---

## 📁 Project Structure

```
local-tailor-connect/
│
├── app.py                     # Flask application factory & route registration
├── config.py                  # Environment and database configuration
├── requirements.txt           # Python package requirements
├── .env                       # Environment variables
├── database.sql               # MySQL DDL schema and initial seed data
├── README.md                  # Documentation and setup instructions
│
├── models/                    # SQLAlchemy database models
│   ├── __init__.py            # db initialization
│   ├── user.py                # User account model (Customer, Tailor, Admin)
│   ├── tailor.py              # Tailor studio profile & rating recalculator
│   ├── measurement.py         # Reusable digital measurement profile
│   ├── order.py               # Order lifecycle model & stage pipeline
│   ├── message.py             # In-app customer-tailor chat messages
│   └── review.py              # Customer ratings and comments
│
├── routes/                    # Modular Blueprint controllers
│   ├── __init__.py
│   ├── auth.py                # Login, register, logout & role redirect
│   ├── customer.py            # Customer dashboard, tailor discovery, messaging
│   ├── tailor.py              # Studio dashboard, production queue, quotations
│   ├── admin.py               # System metrics, user control, studio verification
│   ├── orders.py              # Order submission, quotation acceptance, stage updater
│   ├── measurements.py        # Measurement profiles CRUD & JSON API
│   └── reviews.py             # Review submission & rating refresh
│
├── utils/                     # Helper modules
│   ├── __init__.py
│   ├── decorators.py          # Role enforcement (@customer_required, etc.)
│   ├── helpers.py             # Intelligent tailor matcher, formatters
│   ├── validators.py          # Input validation for measurements and auth
│   └── file_upload.py         # Secure photo and reference image handling
│
├── templates/                 # Jinja2 templates
│   ├── base.html              # Sticky navbar, alerts, footer layout
│   ├── index.html             # Landing page with hero & discovery highlights
│   ├── login.html             # Sign in card
│   ├── register.html          # Registration with dynamic role switcher
│   ├── 404.html / 500.html    # Error handler pages
│   ├── customer/              # Customer portal views (12 templates)
│   ├── tailor/                # Tailor studio views (8 templates)
│   └── admin/                 # Admin console views (8 templates)
│
├── scripts/                   # Automation and data ingestion scripts
│   └── import_tamilnadu_locations.py  # LGD Tamil Nadu location importer
│
├── tests/                     # Automated test suites
│   └── test_tn_locations.py   # Test suite for location APIs & discovery
│
├── static/                    # Frontend assets
│   ├── css/                   # Design system, auth, dashboard & responsive styles
│   ├── js/                    # Cascading dropdowns (location_cascade.js), auth & UI
│   └── uploads/               # Profile and reference image uploads
```

---

## 🏛️ Official Tamil Nadu Administrative Location Dataset

The platform integrates the complete, official administrative location hierarchy for **Tamil Nadu (State Code: 33)** sourced directly from the **Government of India Local Government Directory (LGD)** ([https://lgdirectory.gov.in](https://lgdirectory.gov.in)).

### Hierarchy Structure
```
Tamil Nadu (State Code: 33)
  └── Districts (All 38 Districts)
        └── Taluks / Sub-districts (313 Taluks)
              ├── Cities (Municipal Corporations & Large Urban Local Bodies)
              └── Towns (Municipalities & Town Panchayats)
                    └── Revenue Villages (18,482 Official LGD Villages)
```

### Imported Record Counts
| Administrative Level | Table Name | Total Records | Notes |
| :--- | :--- | :--- | :--- |
| **State** | `states` | 1 (Tamil Nadu) | LGD Code `33` |
| **Districts** | `districts` | 38 | Complete coverage across TN |
| **Taluks** | `taluks` | 313 | All revenue sub-districts |
| **Cities** | `cities` | 742 | City corporations & urban centers |
| **Towns** | `towns` | 624 | Municipalities & Town Panchayats |
| **Revenue Villages** | `villages` | 18,482 | Full official revenue villages |

### Running the Import Script
The import script is standalone, fully cached, and 100% idempotent:
```bash
python scripts/import_tamilnadu_locations.py
```
- Automatically downloads and caches official LGD datasets to `data/lgd_tamil_nadu/`.
- Preserves relational foreign key parent-child integrity (`state_id` → `district_id` → `taluk_id` → `town_id`/`village_id`).
- Can be safely re-executed anytime without duplicating records or disrupting live data.

### Location REST API Endpoints
| HTTP Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/locations/states` | List all states (Tamil Nadu prioritized) |
| `GET` | `/api/locations/districts/<state_id>` | List all 38 districts in state |
| `GET` | `/api/locations/taluks/<district_id>` | List all sub-districts / taluks in district |
| `GET` | `/api/locations/cities/<taluk_id>` | List cities in taluk or district (`?district_id=`) |
| `GET` | `/api/locations/towns/<city_id>` | List towns in city or taluk (`?taluk_id=`) |
| `GET` | `/api/locations/villages/<town_id>` | List villages (`?taluk_id=` supported) |
| `GET` | `/api/locations/villages-by-taluk/<taluk_id>` | List all villages under a specific taluk |
| `GET` | `/api/locations/search?q=<query>` | Fast autocomplete search across administrative units |

### Tailor Registration & Customer Search Integration
- **Cascading Dropdowns**: Dynamic JavaScript dropdown selection powered by `static/js/location_cascade.js` (State → District → Taluk → City/Town → Village).
- **GPS Coordinates**: One-click "📍 Detect Current Location" button saves precise `latitude` and `longitude`.
- **Active Artisan Filtering**: Search only displays registered active tailors (`is_active == True`).
- **Empty State**: When no tailors are registered in a selected location, the page displays:
  `"No registered tailors found in this location."`

### Running the Test Suite
```bash
python tests/test_tn_locations.py
```
All 4 test suites validate:
1. Complete Tamil Nadu hierarchy counts and district presence.
2. All 6 REST API endpoints.
3. Tailor registration with location foreign keys and coordinates.
4. Customer discovery search and empty state message.

