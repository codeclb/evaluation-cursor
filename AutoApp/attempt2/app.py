from __future__ import annotations

import json
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
RESULTS_DIR = BASE_DIR / "results"
DB_PATH = BASE_DIR / "word_frequency.db"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB limit


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS uploads (
                id TEXT PRIMARY KEY,
                original_filename TEXT NOT NULL,
                stored_raw_path TEXT NOT NULL,
                stored_result_path TEXT NOT NULL,
                target_word TEXT NOT NULL,
                target_word_frequency INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        connection.commit()


def normalize_tokens(text: str) -> list[str]:
    return re.findall(r"\b\w+\b", text.lower())


def store_upload_record(
    upload_id: str,
    original_filename: str,
    raw_path: Path,
    result_path: Path,
    target_word: str,
    frequency: int,
) -> None:
    created_at = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            INSERT INTO uploads (
                id,
                original_filename,
                stored_raw_path,
                stored_result_path,
                target_word,
                target_word_frequency,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (
                upload_id,
                original_filename,
                str(raw_path),
                str(result_path),
                target_word,
                frequency,
                created_at,
            ),
        )
        connection.commit()


init_db()


@app.route("/", methods=["GET", "POST"])
def index():
    error_message = None
    result = None

    if request.method == "POST":
        file = request.files.get("text_file")
        target_word = (request.form.get("target_word") or "").strip().lower()

        if not file or file.filename == "":
            error_message = "Please choose a text file to upload."
        elif not target_word:
            error_message = "Please enter a target word."
        else:
            upload_id = uuid.uuid4().hex
            safe_name = secure_filename(file.filename) or f"{upload_id}.txt"
            raw_path = UPLOAD_DIR / f"{upload_id}_{safe_name}"
            file.save(raw_path)

            text = raw_path.read_text(encoding="utf-8", errors="ignore")
            tokens = normalize_tokens(text)

            frequencies: dict[str, int] = {}
            for token in tokens:
                frequencies[token] = frequencies.get(token, 0) + 1

            frequency = frequencies.get(target_word, 0)
            result_path = RESULTS_DIR / f"{upload_id}_frequencies.json"
            result_path.write_text(
                json.dumps(
                    {
                        "target_word": target_word,
                        "target_word_frequency": frequency,
                        "word_frequencies": frequencies,
                    },
                    indent=2,
                    sort_keys=True,
                ),
                encoding="utf-8",
            )

            store_upload_record(
                upload_id=upload_id,
                original_filename=file.filename,
                raw_path=raw_path,
                result_path=result_path,
                target_word=target_word,
                frequency=frequency,
            )

            result = {
                "upload_id": upload_id,
                "filename": file.filename,
                "target_word": target_word,
                "frequency": frequency,
                "raw_file_path": raw_path.relative_to(BASE_DIR),
                "result_file_path": result_path.relative_to(BASE_DIR),
            }

    return render_template("index.html", error_message=error_message, result=result)


if __name__ == "__main__":
    app.run(debug=True)
