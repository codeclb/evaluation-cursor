import os
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename


BASE_DIR = Path(__file__).resolve().parent
UPLOADS_DIR = BASE_DIR / "uploads"
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "word_frequency.db"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".txt"}

app = Flask(__name__)


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_filename TEXT NOT NULL,
                stored_filename TEXT NOT NULL,
                raw_text TEXT NOT NULL,
                uploaded_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS word_frequencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                upload_id INTEGER NOT NULL,
                target_word TEXT NOT NULL,
                frequency INTEGER NOT NULL,
                analyzed_at TEXT NOT NULL,
                FOREIGN KEY(upload_id) REFERENCES uploads(id)
            )
            """
        )


def allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def count_word_frequency(text: str, target_word: str) -> int:
    pattern = re.compile(rf"\b{re.escape(target_word)}\b", flags=re.IGNORECASE)
    return len(pattern.findall(text))


init_db()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze_text():
    if "text_file" not in request.files:
        return jsonify({"error": "Missing text file."}), 400

    uploaded_file = request.files["text_file"]
    target_word = request.form.get("target_word", "").strip()

    if not uploaded_file.filename:
        return jsonify({"error": "Please select a file."}), 400

    if not allowed_file(uploaded_file.filename):
        return jsonify({"error": "Only .txt files are supported."}), 400

    if not target_word:
        return jsonify({"error": "Target word is required."}), 400

    safe_name = secure_filename(uploaded_file.filename)
    stored_filename = f"{uuid4().hex}_{safe_name}"
    stored_path = UPLOADS_DIR / stored_filename
    uploaded_file.save(stored_path)

    try:
        raw_text = stored_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raw_text = stored_path.read_text(encoding="utf-8", errors="ignore")

    frequency = count_word_frequency(raw_text, target_word)
    timestamp = datetime.utcnow().isoformat(timespec="seconds") + "Z"

    with get_db() as conn:
        upload_cursor = conn.execute(
            """
            INSERT INTO uploads (original_filename, stored_filename, raw_text, uploaded_at)
            VALUES (?, ?, ?, ?)
            """,
            (uploaded_file.filename, stored_filename, raw_text, timestamp),
        )
        upload_id = upload_cursor.lastrowid

        conn.execute(
            """
            INSERT INTO word_frequencies (upload_id, target_word, frequency, analyzed_at)
            VALUES (?, ?, ?, ?)
            """,
            (upload_id, target_word, frequency, timestamp),
        )

    return jsonify(
        {
            "upload_id": upload_id,
            "filename": uploaded_file.filename,
            "target_word": target_word,
            "frequency": frequency,
            "analyzed_at": timestamp,
        }
    )


@app.route("/api/history", methods=["GET"])
def analysis_history():
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT
                wf.id,
                u.original_filename,
                wf.target_word,
                wf.frequency,
                wf.analyzed_at
            FROM word_frequencies wf
            JOIN uploads u ON wf.upload_id = u.id
            ORDER BY wf.id DESC
            LIMIT 25
            """
        ).fetchall()

    return jsonify([dict(row) for row in rows])


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
