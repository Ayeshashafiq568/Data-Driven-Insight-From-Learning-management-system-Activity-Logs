# LMS Insights — Django Project Documentation

## 🎓 Project Overview

**LMS Insights** is a premium Django web application for Learning Management System (LMS) log analytics, student risk prediction, and academic advisor interventions. It features:
- **Role-Based Access Control (RBAC)** with three roles: Admin, Instructor, Advisor
- **Machine Learning Pipeline** using scikit-learn Random Forest Classifier for risk prediction
- **Dynamic Dashboard** with Chart.js visualizations
- **Report Export** to PDF and Excel
- **Cyprus & Sand** design theme (premium UI)

### Key Technologies
- **Framework**: Django 4.2–5.0
- **Database**: SQLite (default), PostgreSQL (production-ready)
- **ML**: scikit-learn (Random Forest), pandas, numpy
- **Frontend**: HTML5, CSS3, Chart.js
- **Deployment**: Gunicorn + WhiteNoise (Render/Railway/Azure compatible)

---

## 📁 Project Structure

```
new/                           # Project root
├── manage.py                  # Django CLI
├── requirements.txt           # Python dependencies
├── Procfile                   # Render/Heroku deployment config
├── runtime.txt                # Python version (3.11.9)
├── .gitignore                 # Git ignore rules
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI/CD pipeline
├── analytics/                 # Main Django app
│   ├── models.py              # User (RBAC), Course, Student, ActivityLog, Prediction
│   ├── views.py               # All view controllers + report exports
│   ├── forms.py               # Registration, UserEdit, CSV Upload forms
│   ├── machine_learning.py    # Random Forest pipeline + scoring
│   ├── urls.py                # App-level URL routing
│   ├── admin.py               # Django admin customization
│   ├── tests.py               # 4 automated tests
│   ├── migrations/            # Database migrations
│   ├── static/css/
│   │   └── style.css          # Cyprus & Sand theme
│   └── templates/analytics/   # 12 HTML templates
├── lms_insights/              # Django project config
│   ├── settings.py            # Production-ready settings
│   ├── urls.py                # Root URL router
│   ├── wsgi.py                # WSGI application (Gunicorn)
│   └── asgi.py                # ASGI application
├── seed_db.py                 # Create default users (admin, instructor, advisor)
├── generate_sample_csv.py     # Generate 300 mock LMS activity logs
├── populate_mock_data.py      # Import CSV + train ML model
└── db.sqlite3                 # SQLite database (created on first run)
```

---

## 🚀 Local Development Setup

### Prerequisites
- Python 3.10+ installed and in PATH
- Git (configured with GitHub credentials)

### Quick Start (Windows PowerShell)

```powershell
cd "C:\Users\hp\Downloads\new (2) (1)\new\new"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --no-cache-dir -r requirements.txt
python manage.py migrate
python seed_db.py
python generate_sample_csv.py
python populate_mock_data.py
python manage.py runserver
```

Then open **http://127.0.0.1:8000/** in your browser.

### Or Use the Automated Batch File
```powershell
cd "C:\Users\hp\Downloads\new (2) (1)\new\new"
.\run_project.bat
```

---

## 🔐 Default Credentials

| Role | Username | Password | Email |
|---|---|---|---|
| Admin | `admin` | `admin123` | `admin@iub.edu.pk` |
| Instructor | `instructor` | `instructor123` | `instructor@iub.edu.pk` |
| Advisor | `advisor` | `advisor123` | `advisor@iub.edu.pk` |

---

## 🧪 Run Tests

```bash
python manage.py test --verbosity=2
```

Tests cover:
1. RBAC role permissions
2. ML pipeline execution
3. PDF/Excel report exports
4. Advisor alert filtering system

All tests pass in <15 seconds.

---

## 📊 ML Pipeline Summary

**Input**: `ActivityLog` records from the database

**Features**:
- `total_activities` — total LMS interactions
- `total_duration` — cumulative time spent (minutes)
- `quiz_submissions` — number of quizzes taken
- `forum_posts` — discussion board participation
- `resource_views` — course material accesses

**Engagement Score**: Weighted normalization (0–100%)

**Classifier**: RandomForestClassifier (scikit-learn with pure-Python fallback)

**Risk Buckets**:
- `< 35%` → High Risk
- `35–70%` → Medium Risk
- `≥ 70%` → Low Risk

**Output**: Auto-generated intervention recommendations per student–course pair

---

## 🌐 Production Deployment (Render)

### 1. Prepare Environment
```bash
# All files already committed and pushed to GitHub
git push origin main
```

### 2. Create Render Account
Visit **https://render.com** → Sign up with GitHub

### 3. Deploy to Render
1. Click **New** → **Web Service**
2. Select your GitHub repo: `Data-Driven-Insight-From-Learning-management-system-Activity-Logs`
3. Configure:
   - **Name**: `lms-insights`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Start Command**: Leave empty (Procfile auto-detected)
   - **Plan**: Free tier (sufficient for testing)

### 4. Set Environment Variables (Critical!)
In Render dashboard → **Environment**:
```
DEBUG = False
ALLOWED_HOSTS = lms-insights.onrender.com
SECRET_KEY = (generate via: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
```

### 5. Verify Deployment
- Render provides a live URL after ~5 min (e.g., `https://lms-insights.onrender.com`)
- Login with credentials above
- Check Actions tab on GitHub for CI/CD logs

---

## 🔄 GitHub Actions CI/CD

**Workflow file**: `.github/workflows/ci.yml`

**Triggers**: On push or pull request to `main` branch

**Steps**:
1. Checkout code
2. Set up Python 3.10 & 3.11 (matrix build)
3. Install dependencies (`pip install -r new/requirements.txt`)
4. Run migrations (`python manage.py migrate --noinput`)
5. Run tests (`python manage.py test --verbosity=2`)

**Status**: Check [GitHub Actions tab](https://github.com/Ayeshashafiq568/Data-Driven-Insight-From-Learning-management-system-Activity-Logs/actions)

---

## 🐛 Troubleshooting

### "No space left on device" during pip install
```powershell
pip install --no-cache-dir -r requirements.txt
# or
pip install --no-cache-dir -r requirements.txt --force-reinstall
```

### Git not found in PowerShell
```powershell
$env:Path += ';C:\Program Files\Git\cmd'
setx PATH "$($env:Path)"
# Then restart terminal
```

### Django migrations fail
```bash
python manage.py migrate --fake-initial
python manage.py migrate
```

### Static files not loading in production
```bash
python manage.py collectstatic --noinput
# Render auto-runs this in build command
```

---

## 📦 Dependencies

See `requirements.txt`:
- **django** ≥4.2, <5.1
- **pandas**, **numpy** — Data processing
- **scikit-learn** — ML classifier
- **openpyxl** — Excel export
- **reportlab** — PDF export
- **gunicorn** — Production WSGI server
- **whitenoise** — Static file serving
- **python-dotenv** — Environment variables

---

## 🔗 GitHub Repository

**URL**: https://github.com/Ayeshashafiq568/Data-Driven-Insight-From-Learning-management-system-Activity-Logs

**Branch**: `main` (default)

**Protected**: Yes (CI must pass before merge)

---

## 📝 Common Tasks

### Add a new view
1. Create function in `analytics/views.py`
2. Add route in `analytics/urls.py`
3. Create template in `analytics/templates/analytics/`
4. Add test in `analytics/tests.py`

### Modify ML pipeline
Edit `analytics/machine_learning.py` and re-run:
```bash
python populate_mock_data.py
```

### Export a student report
Use admin dashboard → Student Directory → Select student → "Export PDF" or "Export Excel"

### Reset database
```bash
rm db.sqlite3
python manage.py migrate
python seed_db.py
```

---

## 📞 Support

For issues, check:
- GitHub Issues: https://github.com/Ayeshashafiq568/Data-Driven-Insight-From-Learning-management-system-Activity-Logs/issues
- Django Docs: https://docs.djangoproject.com
- scikit-learn Docs: https://scikit-learn.org

---

**Last Updated**: 2026-06-04
**Project Status**: ✅ Ready for Production
