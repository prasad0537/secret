import os
import time
from flask import Flask, render_template, request, redirect, session
from supabase import create_client, Client
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecretkey123"

SUPABASE_URL = "https://lxthnwowybpoxfaybrc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx4bHRuaHdvd3lwYm94ZmF5YnJjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5MTcyMTUsImV4cCI6MjA3MjQ5MzIxNX0.8PU4czvXQ4FhwUrBBelXXPSi7D_LaZLxwk0Fps7i26k"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

USERNAME = "admin"
PASSWORD = "password"

CATEGORIES = {
    "pdf": ["pdf"],
    "images": ["jpg", "jpeg", "png", "gif", "bmp", "svg", "webp"],
    "videos": ["mp4", "mkv", "avi", "mov", "flv", "wmv"],
    "audio": ["mp3", "wav", "aac", "ogg", "flac"],
    "docs": ["doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "csv", "md", "rtf"],
    "archives": ["zip", "rar", "7z", "tar", "gz"],
    "code": ["py", "c", "cpp", "js", "html", "css", "java", "php", "rb", "go", "ts", "sql"]
}

def is_logged_in():
    return session.get("logged_in")

def get_category(filename):
    ext = filename.rsplit(".", 1)[-1].lower()
    for cat, exts in CATEGORIES.items():
        if ext in exts:
            return cat
    return "others"

@app.route("/")
def home():
    if not is_logged_in():
        return redirect("/login")
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == USERNAME and password == PASSWORD:
            session["logged_in"] = True
            return redirect("/")
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect("/login")

@app.route("/upload", methods=["POST"])
def upload():
    if not is_logged_in():
        return redirect("/login")

    file = request.files.get("file")
    if not file:
        return redirect("/")

    original_name = secure_filename(file.filename)
    unique_name = f"{int(time.time())}_{original_name}"
    category = get_category(original_name)
    path = f"{category}/{unique_name}"

    try:
        # Upload to Supabase Storage
        upload_response = supabase.storage.from_("uploads").upload(path, file.stream, {
            "content-type": file.content_type
        })
        print("📤 Supabase upload response:", upload_response)

        # Save metadata to Supabase Database
        db_response = supabase.table("files").insert({
            "original_name": original_name,
            "storage_name": unique_name,
            "category": category,
            "path": path,
            "content_type": file.content_type,
            "uploaded_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }).execute()
        print("🗂️ Supabase DB insert response:", db_response)

    except Exception as e:
        print("❌ Upload error:", e)

    return redirect("/storage")

@app.route("/storage")
def storage():
    if not is_logged_in():
        return redirect("/login")

    files = {}
    try:
        response = supabase.table("files").select("*").execute()
        print("📦 Supabase DB fetch:", response)
        data = response.data if response.data else []

        for cat in list(CATEGORIES.keys()) + ["others"]:
            files[cat] = [f for f in data if f.get("category") == cat]

    except Exception as e:
        print("❌ Storage error:", e)
        return f"<h1>Internal Error</h1><p>{e}</p>"

    return render_template("storage.html", files=files)

@app.route("/delete/<category>/<filename>", methods=["POST"])
def delete(category, filename):
    if not is_logged_in():
        return redirect("/login")

    try:
        supabase.storage.from_("uploads").remove([f"{category}/{filename}"])
        supabase.table("files").delete().match({
            "storage_name": filename,
            "category": category
        }).execute()
        print(f"✅ Deleted: {filename}")

    except Exception as e:
        print("❌ Delete error:", e)

    return redirect("/storage")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)