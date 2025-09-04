from flask import Flask, render_template, request, redirect, session
import os
from supabase import create_client, Client
from werkzeug.utils import secure_filename
import time

# Flask setup
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Supabase setup
url = "https://lxthnwowybpoxfaybrc.supabase.co"  # your project URL
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx4bHRuaHdvd3lwYm94ZmF5YnJjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTY5MTcyMTUsImV4cCI6MjA3MjQ5MzIxNX0.8PU4czvXQ4FhwUrBBelXXPSi7D_LaZLxwk0Fps7i26k"
supabase: Client = create_client(url, key)

# Dummy login
USERNAME = 'sjup'
PASSWORD = 'password'

def is_logged_in():
    return session.get('logged_in')

@app.route('/')
def home():
    if not is_logged_in():
        return redirect('/login')
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect('/')
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/login')

@app.route('/upload', methods=['POST'])
def upload():
    if not is_logged_in():
        return redirect('/login')
    if 'file' not in request.files:
        return redirect('/')
    
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)

        # Add timestamp to avoid overwriting old files
        unique_filename = f"{int(time.time())}_{filename}"

        # Upload file to Supabase bucket "uploads"
        supabase.storage.from_("uploads").upload(
            path=unique_filename,
            file=file.read()
        )

    return redirect('/storage')

@app.route('/storage')
def storage():
    if not is_logged_in():
        return redirect('/login')

    # List files in Supabase bucket
    files = supabase.storage.from_("uploads").list()
    return render_template('storage.html', files=files)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

