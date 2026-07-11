
from flask import Flask, render_template, request, send_file
import os, shutil, zipfile

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

FILE_TYPES = {
    "Images":    [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"],
    "Videos":    [".mp4", ".mov", ".avi", ".mkv"],
    "Documents": [".pdf", ".docx", ".txt", ".pptx", ".xlsx", ".csv"],
    "Music":     [".mp3", ".wav", ".aac", ".flac"],
    "Archives":  [".zip", ".rar", ".tar", ".gz"],
    "Code":      [".py", ".js", ".html", ".css", ".json"],
    "Others":    []
}

def get_category(extension):
    for category, exts in FILE_TYPES.items():
        if extension.lower() in exts:
            return category
    return "Others"

def organize_files(folder_path):
    moved = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isdir(file_path):
            continue
        _, ext = os.path.splitext(filename)
        category = get_category(ext)
        subfolder = os.path.join(folder_path, category)
        os.makedirs(subfolder, exist_ok=True)
        shutil.move(file_path, os.path.join(subfolder, filename))
        moved.append({"file": filename, "category": category})
    return moved

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["zipfile"]
        if file and file.filename.endswith(".zip"):
            zip_path = os.path.join(UPLOAD_FOLDER, "input.zip")
            extract_path = os.path.join(UPLOAD_FOLDER, "extracted")
            output_zip = os.path.join(UPLOAD_FOLDER, "organized.zip")

            # Clean previous uploads
            if os.path.exists(extract_path):
                shutil.rmtree(extract_path)

            file.save(zip_path)

            # Extract ZIP
            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(extract_path)

            # Organize
            moved = organize_files(extract_path)

            # Zip organized folder
            with zipfile.ZipFile(output_zip, "w") as z:
                for root, dirs, files in os.walk(extract_path):
                    for f in files:
                        filepath = os.path.join(root, f)
                        z.write(filepath, os.path.relpath(filepath, extract_path))

            return render_template("index.html", moved=moved, download=True)

    return render_template("index.html", moved=None, download=False)

@app.route("/download")
def download():
    return send_file("uploads/organized.zip", as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)