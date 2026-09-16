"""
Flask frontend for the Resume Screening Platform.

Stage: UI + PDF upload only (matching/scoring stages plug in later).

Install:
    pip install flask pdfplumber

Run:
    python app.py
Then open http://127.0.0.1:5000
"""

import os
import uuid

from flask import Flask, render_template, request, jsonify
import pdfplumber

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXTENSIONS = {"pdf"}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_pdf_text(filepath: str) -> dict:
    text_parts = []
    with pdfplumber.open(filepath) as pdf:
        num_pages = len(pdf.pages)
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    full_text = "\n".join(text_parts).strip()
    word_count = len(full_text.split())
    preview = full_text[:600] + ("..." if len(full_text) > 600 else "")
    return {"num_pages": num_pages, "word_count": word_count, "preview": preview}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "resume" not in request.files:
        return jsonify({"error": "No file part in the request."}), 400

    file = request.files["resume"]

    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are accepted."}), 400

    safe_name = f"{uuid.uuid4().hex}.pdf"
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)
    file.save(save_path)

    try:
        details = extract_pdf_text(save_path)
    except Exception as exc:  # pdfplumber can choke on malformed/scanned PDFs
        return jsonify({"error": f"Couldn't read that PDF: {exc}"}), 422

    return jsonify({
        "original_filename": file.filename,
        "num_pages": details["num_pages"],
        "word_count": details["word_count"],
        "preview": details["preview"],
    })


if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
