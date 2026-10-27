import os
import sqlite3
from datetime import datetime, timezone
from uuid import uuid4

from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "local-demo-only-change-before-deployment",
)

DATABASE = os.environ.get("DATABASE_PATH", "firmware.db")

FIELDS = [
    "project_name",
    "firmware_version",
    "git_branch",
    "commit_id",
    "platform",
    "signing_profile",
]


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS firmware_requests (
                id TEXT PRIMARY KEY,
                project_name TEXT NOT NULL,
                firmware_version TEXT NOT NULL,
                git_branch TEXT NOT NULL,
                commit_id TEXT NOT NULL,
                platform TEXT NOT NULL,
                signing_profile TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


def get_requests():
    with get_db() as db:
        rows = db.execute("""
            SELECT * FROM firmware_requests
            ORDER BY created_at DESC
        """).fetchall()
        return [dict(row) for row in rows]


def create_request(values):
    request_id = str(uuid4())[:8].upper()
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    with get_db() as db:
        db.execute("""
            INSERT INTO firmware_requests (
                id, project_name, firmware_version, git_branch,
                commit_id, platform, signing_profile, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            request_id,
            values["project_name"],
            values["firmware_version"],
            values["git_branch"],
            values["commit_id"],
            values["platform"],
            values["signing_profile"],
            "PENDING_APPROVAL",
            created_at,
        ))

    return request_id


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        values = {
            field: request.form.get(field, "").strip()
            for field in FIELDS
        }

        if not all(values.values()):
            flash("Please complete all fields.")
            return redirect(url_for("index"))

        request_id = create_request(values)
        flash(f"Request {request_id} submitted for approval.")
        return redirect(url_for("index"))

    return render_template("index.html", requests=get_requests())


@app.route("/approver")
def approver():
    return render_template("approver.html", requests=get_requests())


@app.route("/approver/<request_id>/<decision>", methods=["POST"])
def decide(request_id, decision):
    if decision not in ("approve", "reject"):
        flash("Invalid decision.")
        return redirect(url_for("approver"))

    new_status = "APPROVED" if decision == "approve" else "REJECTED"

    with get_db() as db:
        cursor = db.execute("""
            UPDATE firmware_requests
            SET status = ?
            WHERE id = ? AND status = 'PENDING_APPROVAL'
        """, (new_status, request_id))

    if cursor.rowcount == 1:
        flash(f"Request {request_id}: {new_status}.")
    else:
        flash("Request not found or already processed.")

    return redirect(url_for("approver"))


init_db()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
