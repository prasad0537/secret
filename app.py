from flask import Flask, render_template, request, redirect, send_from_directory, session, url_for
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt', 'zip', 'mp4', 'mp3', 'docx', 'xlsx', 'pptx', 'csv', 'json', 'xml', 'html', 'css', 'js', 'svg', 'woff', 'woff2', 'ttf', 'eot', 'otf', 'ico', 'bmp', 'webp', 'avif', 'mkv', 'mov', 'avi', 'flv', 'wmv', 'mpg', 'mpeg', '3gp', '3g2', 'm4v', 'ts', 'm2ts', 'mts', 'asf', 'divx', 'xvid', 'rmvb', 'rm', 'dat', 'vob', 'ogv', 'ogg', 'opus', 'wav', 'flac', 'aac', 'm4a', 'wma', 'aiff', 'au', 'snd', 'cda', 'mid', 'midi', 'kar', 'sf2', 'sfz', 'dls', 'sflist', 'synth', 'vst', 'vsti', 'dll', 'exe', 'apk', 'ipa', 'appx', 'msi', 'bat', 'sh', 'pl', 'py', 'rb', 'php', 'jsp', 'asp', 'html5', 'css3', 'js3', 'json5', 'xml2', 'yaml', 'yml', 'toml', 'ini', 'cfg', 'properties', 'log', 'txt2', 'csv2', 'tsv', 'xlsx2', 'docx2', 'pptx2', 'odt', 'ods', 'odp', 'dotx', 'dotm', 'docm', 'xlsm', 'xlsb', 'pptm', 'potx', 'potm', 'ppsx', 'ppsm', 'ppsx2', 'pptx3', 'docx3', 'xlsx3', 'csv3', 'json3', 'xml3', 'html4', 'css4', 'js4', 'svg2', 'woff3', 'woff2', 'ttf2', 'eot2', 'otf2', 'ico2', 'bmp2', 'webp2', 'avif2'}   

USERNAME = 'sjup'
PASSWORD = 'password'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return redirect('/storage')

@app.route('/storage')
def storage():
    if not is_logged_in():
        return redirect('/login')
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('storage.html', files=files)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    if not is_logged_in():
        return redirect('/login')
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
