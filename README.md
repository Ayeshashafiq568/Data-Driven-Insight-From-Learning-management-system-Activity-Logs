# 🎓 LMS Insights — Student Risk Analytics & Intervention System

A premium, fully functional Django web application for LMS log analytics, predictive student risk classification, and academic advisor interventions — powered by a **Random Forest Classifier** from `scikit-learn`.

The platform enforces **Role-Based Access Control (RBAC)** across three roles (Admin, Instructor, Advisor) and features a rich, responsive **Cyprus & Sand** design theme with dynamic Chart.js visualizations.

---

## ⚡ Quick Start — Run on Any PC in 60 Seconds

**Prerequisites:** Python 3.10+ installed and accessible via `python` in your terminal.

### 🪟 Windows (PowerShell / CMD)

Open PowerShell inside the project folder and paste this **one-liner**:

```powershell
pip install --no-cache-dir -r requirements.txt; python manage.py migrate; python seed_db.py; python generate_sample_csv.py; python populate_mock_data.py; python manage.py runserver
```

> If installation fails with `No space left on device`, free disk space or use the `--no-cache-dir` flag to reduce temporary disk usage.

### 🍎 macOS / Linux (Bash / Zsh)

Open a terminal inside the project folder and paste this **one-liner**:

```bash
pip install -r requirements.txt && python manage.py migrate && python seed_db.py && python generate_sample_csv.py && python populate_mock_data.py && python manage.py runserver
```

Then open **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in your browser. ✅

---

## 📋 Step-by-Step Breakdown

If the one-liner fails at any point, run each step individually:

```bash
# Step 1: Install all Python dependencies
pip install -r requirements.txt

# Step 2: Apply database schema migrations (creates db.sqlite3)
python manage.py migrate

# Step 3: Create default Admin, Instructor & Advisor login accounts
python seed_db.py

# Step 4: Generate 300 mock LMS activity log records
python generate_sample_csv.py

# Step 5: Import logs into the database & train the ML risk classifier
python populate_mock_data.py

# Step 6: Start the development server
python manage.py runserver
```

---

## 🔑 Login Credentials

| Role | Username | Password | Email |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | `admin@iub.edu.pk` |
| **Instructor** | `instructor` | `instructor123` | `instructor@iub.edu.pk` |
| **Advisor** | `advisor` | `advisor123` | `advisor@iub.edu.pk` |

All generated student profiles use authentic Pakistani names with `@iub.edu.pk` email addresses.

## Push this project to GitHub

To publish this project to the GitHub repository `https://github.com/Ayeshashafiq568/Data-Driven-Insight-From-Learning-management-system-Activity-Logs` from your local copy, run the following commands from the project root (the folder that contains `manage.py`):

```bash
git init
git add .
git commit -m "Initial import of LMS Insights project"
git remote add origin https://github.com/Ayeshashafiq568/Data-Driven-Insight-From-Learning-management-system-Activity-Logs.git
git branch -M main
git push -u origin main
```

If the remote already exists or you prefer SSH, replace the `git remote add` URL with your SSH remote. Authenticate when prompted (PAT or SSH key) and ensure you have sufficient disk space on the target machine when running CI.

## GitHub Actions CI

A GitHub Actions workflow was added at `.github/workflows/ci.yml` to run migrations and tests on pushes and pull requests. Check the Actions tab after pushing to see CI results.


---

## 🧪 Run Automated Tests

```bash
python manage.py test
```

Runs 4 tests covering: RBAC role permissions, ML pipeline execution, PDF/Excel report exports, and the dynamic advisor alert filtering system. All tests pass in under 15 seconds.

---

## 🗂️ Project Structure

```
├── analytics/
│   ├── machine_learning.py   # Random Forest pipeline + engagement scoring
│   ├── models.py             # User (RBAC), Course, Student, ActivityLog, Prediction
│   ├── views.py              # All view controllers + report exports
│   ├── urls.py               # URL routing
│   ├── forms.py              # Registration, UserEdit, CSV Upload forms
│   ├── tests.py              # Full automated test suite (4 tests)
│   ├── static/css/style.css  # Cyprus & Sand premium design system
│   └── templates/analytics/  # 12 HTML templates (dashboard, alerts, reports...)
├── lms_insights/
│   ├── settings.py           # Django project settings
│   └── urls.py               # Root URL configuration
├── generate_sample_csv.py    # Generates 300 mock LMS activity log records
├── populate_mock_data.py     # Imports CSV + runs ML pipeline
├── seed_db.py                # Creates pre-configured login accounts
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

---

## 🎨 Design System (Cyprus & Sand)

| Token | Hex | Usage |
| :--- | :--- | :--- |
| **Cyprus** | `#004643` | Sidebar, headers, primary buttons |
| **Sand** | `#F0EDE5` | Page background, cards, sand tones |
| **Amber Accent** | `#E0A96D` | Highlights, icons, filter labels |
| **High Risk** | `#8A1F1F` | Critical alert indicators |
| **Medium Risk** | `#9E7611` | Moderate alert indicators |

---

## 🔐 Role-Based Feature Matrix

| Feature | Admin | Instructor | Advisor |
| :--- | :---: | :---: | :---: |
| CSV Log Upload | ✅ | ❌ | ❌ |
| User Management | ✅ | ❌ | ❌ |
| Main Dashboard | ✅ | ✅ | ✅ |
| Course Analytics | ✅ | ✅ | ✅ |
| Student Directory | ✅ | ✅ | ✅ |
| Risk Alerts (Filtered) | ✅ | ❌ | ✅ |
| PDF / Excel Export | ✅ | ✅ | ✅ |

---

## 🤖 ML Pipeline Summary

- **Input**: Raw `ActivityLog` records from the database
- **Features**: `total_activities`, `total_duration`, `quiz_submissions`, `forum_posts`, `resource_views`
- **Engagement Score**: Weighted normalization index (0–100%)
- **Classifier**: `RandomForestClassifier` (scikit-learn), with pure-Python fallback
- **Risk Buckets**: `< 35%` → High Risk · `35–70%` → Medium Risk · `≥ 70%` → Low Risk
- **Recommendations**: Auto-generated intervention advice per student-course pair
