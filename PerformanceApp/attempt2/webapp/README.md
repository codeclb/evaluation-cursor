# Word Frequency Web App

This app provides:

1. A web UI to upload a `.txt` file, enter a target word, and compute its frequency.
2. Raw uploaded text file storage on disk (`uploads/`).
3. Persistent storage of analysis results in SQLite (`data/word_frequency.db`).

## Run locally

```bash
cd webapp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open [http://127.0.0.1:5000](http://127.0.0.1:5000).

## API

- `POST /api/analyze` with multipart form data:
  - `text_file` (required, `.txt`)
  - `target_word` (required)
- `GET /api/history` returns latest saved analyses.
