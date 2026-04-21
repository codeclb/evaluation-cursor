from flask import Flask, render_template, request
import re


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2 MB upload limit


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    if request.method == "POST":
        uploaded_file = request.files.get("text_file")
        keyword = request.form.get("keyword", "").strip()

        if not uploaded_file or uploaded_file.filename == "":
            error = "Please upload a text file."
        elif not keyword:
            error = "Please enter a keyword."
        elif not uploaded_file.filename.lower().endswith(".txt"):
            error = "Only .txt files are supported."
        else:
            try:
                file_text = uploaded_file.read().decode("utf-8")
            except UnicodeDecodeError:
                error = "The file must be UTF-8 encoded text."
            else:
                # Count whole-word, case-insensitive matches.
                pattern = rf"\b{re.escape(keyword)}\b"
                matches = re.findall(pattern, file_text, flags=re.IGNORECASE)
                result = {
                    "filename": uploaded_file.filename,
                    "keyword": keyword,
                    "count": len(matches),
                }

    return render_template("index.html", result=result, error=error)


if __name__ == "__main__":
    app.run(debug=True)
