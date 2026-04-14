# ================= BACKEND (FLASK + JWT + CORS FIX) =================

from flask import Flask, request, jsonify
from flask_cors import CORS   # ✅ NEW
import sqlite3, jwt, datetime
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
CORS(app)   # ✅ IMPORTANT (fixes frontend connection)

app.config['SECRET_KEY'] = 'secret123'

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def db():
    return sqlite3.connect('jobs.db')


# ================= SIGNUP =================
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    conn = db()
    cur = conn.cursor()
    cur.execute("INSERT INTO users(name,email,password) VALUES(?,?,?)",
                (data['name'], data['email'], data['password']))
    conn.commit()
    conn.close()
    return jsonify({'msg': 'Signup success'})


# ================= LOGIN =================
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email=? AND password=?",
                (data['email'], data['password']))
    user = cur.fetchone()
    conn.close()

    if user:
        token = jwt.encode({
            'user': data['email'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({'token': token})

    return jsonify({'msg': 'Invalid login'})


# ================= GET JOBS =================
@app.route('/jobs', methods=['GET'])
def get_jobs():
    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM jobs")
    jobs = cur.fetchall()
    conn.close()

    return jsonify([
        {'id': j[0], 'title': j[1], 'company': j[2], 'salary': j[3]}
        for j in jobs
    ])


# ================= ADD JOB =================
@app.route('/jobs', methods=['POST'])
def add_job():
    data = request.json
    conn = db()
    cur = conn.cursor()
    cur.execute("INSERT INTO jobs(title,company,salary) VALUES(?,?,?)",
                (data['title'], data['company'], data['salary']))
    conn.commit()
    conn.close()
    return jsonify({'msg': 'Job added'})


# ================= SAVE JOB =================
@app.route('/save', methods=['POST'])
def save_job():
    data = request.json
    conn = db()
    cur = conn.cursor()
    cur.execute("INSERT INTO saved(job_id) VALUES(?)", (data['job_id'],))
    conn.commit()
    conn.close()
    return jsonify({'msg': 'Saved'})


# ================= UPLOAD RESUME =================
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)
    return jsonify({'msg': 'Uploaded'})


# ================= MAIN =================
import os

if __name__ == '__main__':
    conn = sqlite3.connect('jobs.db')
    cur = conn.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,name TEXT,email TEXT,password TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS jobs(id INTEGER PRIMARY KEY,title TEXT,company TEXT,salary TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS saved(id INTEGER PRIMARY KEY,job_id INTEGER)")

    conn.commit()
    conn.close()

    port = int(os.environ.get("PORT", 5000))   # ✅ IMPORTANT
    app.run(host="0.0.0.0", port=port)         # ✅ IMPORTANT
