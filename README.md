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
└── static/                    # Frontend assets
    ├── css/                   # Design system, auth, dashboard & responsive styles
    ├── js/                    # Core interactivity, AJAX preview & form handlers
    └── uploads/               # Profile and reference image uploads
```
