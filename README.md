# OpenHire – Open Source Job Portal

A beginner-friendly Python Flask project that demonstrates a simple job portal.

## Features
- User registration and login
- Password hashing
- Browse and search job listings
- Post a job after login
- View job details
- Apply for jobs
- View your submitted applications
- SQLite database with sample jobs

## Requirements
- Python 3.9 or newer
- pip

## Run on Windows

Open a terminal in this project folder and run:

```powershell
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
py app.py
```

Then open: http://127.0.0.1:5000

The SQLite database (`job_portal.db`) is created automatically when the app starts.

## Important
This is an educational demonstration, not a production-ready recruitment platform.
Before deployment, replace `app.secret_key`, turn off Flask debug mode, add CSRF protection,
email verification, stronger validation, and production database/security settings.
