# OpenHire – Open Source Job Portal

## Project Overview

OpenHire is a beginner-friendly web-based job portal developed using Python and Flask. It connects job seekers with employment opportunities and allows users to explore jobs, create accounts, post vacancies, and submit applications.

## Technology Stack

- Python
- Flask
- SQLite
- HTML
- CSS

## Key Features

- User registration and login
- Password hashing and authentication
- Browse and search job listings
- Post job vacancies after login
- View detailed job information
- Apply for available jobs
- Track submitted applications
- SQLite database for storing users, jobs, and applications

## Implementation

The backend is developed using Python and Flask. SQLite handles database operations, while HTML and CSS provide the user interface. Flask routes manage authentication, job searching, job posting, and application processing.

## Project Objective

To simplify the job-search process by providing a centralized platform where job seekers and employers can interact efficiently.

## Requirements

- Python 3.9 or newer
- pip

## Run on Windows

Open a terminal in the project folder and execute:

```powershell
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
py app.py
```

Then open: http://127.0.0.1:5000

The SQLite database (`job_portal.db`) is created automatically when the application starts.

## Important

This is an educational demonstration, not a production-ready recruitment platform. Before production deployment, configure a secure secret key, disable Flask debug mode, add CSRF protection, and use appropriate production database and security settings.
