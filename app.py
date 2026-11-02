from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from pathlib import Path

app = Flask(__name__)
import os
app.secret_key = os.environ.get("SECRET_KEY", "dev-key-change-before-deployment")
DB_PATH = Path(__file__).with_name("job_portal.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT NOT NULL,
                job_type TEXT NOT NULL,
                description TEXT NOT NULL,
                posted_by INTEGER,
                FOREIGN KEY(posted_by) REFERENCES users(id)
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(job_id, user_id),
                FOREIGN KEY(job_id) REFERENCES jobs(id),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        count = db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
        if count == 0:
            sample_jobs = [
                ("Junior Python Developer", "TechNova", "Chennai", "Full-time",
                 "Work on Python applications, APIs, and database-backed features."),
                ("Frontend Developer Intern", "PixelWorks", "Coimbatore", "Internship",
                 "Build responsive interfaces using HTML, CSS, JavaScript, and Bootstrap."),
                ("Graduate Software Trainee", "OpenByte", "Remote", "Full-time",
                 "Assist the engineering team with testing, debugging, and development.")
            ]
            db.executemany(
                """INSERT INTO jobs (title, company, location, job_type, description)
                   VALUES (?, ?, ?, ?, ?)""", sample_jobs
            )


@app.route("/")
def index():
    keyword = request.args.get("q", "").strip()
    with get_db() as db:
        if keyword:
            pattern = f"%{keyword}%"
            jobs = db.execute("""
                SELECT * FROM jobs
                WHERE title LIKE ? OR company LIKE ? OR location LIKE ?
                ORDER BY id DESC
            """, (pattern, pattern, pattern)).fetchall()
        else:
            jobs = db.execute("SELECT * FROM jobs ORDER BY id DESC").fetchall()
    return render_template("index.html", jobs=jobs, keyword=keyword)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 6:
            flash("Enter your name, a valid email, and a password of at least 6 characters.")
            return redirect(url_for("register"))
        try:
            with get_db() as db:
                db.execute(
                    "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                    (name, email, generate_password_hash(password))
                )
            flash("Account created. Please log in.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("That email is already registered.")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        with get_db() as db:
            user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            flash(f"Welcome, {user['name']}!")
            return redirect(url_for("index"))
        flash("Invalid email or password.")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("index"))


@app.route("/jobs/new", methods=["GET", "POST"])
def new_job():
    if "user_id" not in session:
        flash("Please log in before posting a job.")
        return redirect(url_for("login"))
    if request.method == "POST":
        fields = [
            request.form.get("title", "").strip(),
            request.form.get("company", "").strip(),
            request.form.get("location", "").strip(),
            request.form.get("job_type", "").strip(),
            request.form.get("description", "").strip()
        ]
        if not all(fields):
            flash("Please complete every field.")
            return redirect(url_for("new_job"))
        with get_db() as db:
            db.execute("""
                INSERT INTO jobs (title, company, location, job_type, description, posted_by)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (*fields, session["user_id"]))
        flash("Job posted successfully.")
        return redirect(url_for("index"))
    return render_template("new_job.html")


@app.route("/jobs/<int:job_id>")
def job_detail(job_id):
    with get_db() as db:
        job = db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if not job:
        flash("Job not found.")
        return redirect(url_for("index"))
    return render_template("job_detail.html", job=job)


@app.route("/jobs/<int:job_id>/apply", methods=["POST"])
def apply(job_id):
    if "user_id" not in session:
        flash("Please log in to apply for a job.")
        return redirect(url_for("login"))
    message = request.form.get("message", "").strip()
    if not message:
        flash("Please add a short application message.")
        return redirect(url_for("job_detail", job_id=job_id))
    try:
        with get_db() as db:
            exists = db.execute("SELECT id FROM jobs WHERE id = ?", (job_id,)).fetchone()
            if not exists:
                flash("Job not found.")
                return redirect(url_for("index"))
            db.execute("""
                INSERT INTO applications (job_id, user_id, message)
                VALUES (?, ?, ?)
            """, (job_id, session["user_id"], message))
        flash("Your application has been submitted.")
    except sqlite3.IntegrityError:
        flash("You have already applied for this job.")
    return redirect(url_for("job_detail", job_id=job_id))


@app.route("/my-applications")
def my_applications():
    if "user_id" not in session:
        flash("Please log in to view your applications.")
        return redirect(url_for("login"))
    with get_db() as db:
        applications = db.execute("""
            SELECT applications.*, jobs.title, jobs.company, jobs.location
            FROM applications
            JOIN jobs ON jobs.id = applications.job_id
            WHERE applications.user_id = ?
            ORDER BY applications.applied_at DESC
        """, (session["user_id"],)).fetchall()
    return render_template("my_applications.html", applications=applications)


init_db()

if __name__ == "__main__":
    app.run(debug=True)
