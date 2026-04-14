# ================= BACKEND (FLASK + JWT) =================

from flask import Flask,request,jsonify
import sqlite3, jwt, datetime
from werkzeug.utils import secure_filename
import os

app=Flask(__name__)
app.config['SECRET_KEY']='secret123'

UPLOAD_FOLDER='uploads'
os.makedirs(UPLOAD_FOLDER,exist_ok=True)


def db(): return sqlite3.connect('jobs.db')

@app.route('/signup',methods=['POST'])
def signup():
 d=request.json
 conn=db();cur=conn.cursor()
 cur.execute("INSERT INTO users(name,email,password) VALUES(?,?,?)",(d['name'],d['email'],d['password']))
 conn.commit();return jsonify({'msg':'done'})

@app.route('/login',methods=['POST'])
def login():
 d=request.json
 conn=db();cur=conn.cursor()
 cur.execute("SELECT * FROM users WHERE email=? AND password=?",(d['email'],d['password']))
 u=cur.fetchone()
 if u:
  token=jwt.encode({'user':d['email'],'exp':datetime.datetime.utcnow()+datetime.timedelta(hours=2)},app.config['SECRET_KEY'],algorithm='HS256')
  return jsonify({'token':token})
 return jsonify({'msg':'fail'})

@app.route('/jobs',methods=['GET'])
def jobs():
 cur=db().cursor();cur.execute("SELECT * FROM jobs")
 return jsonify([{'id':j[0],'title':j[1],'company':j[2],'salary':j[3]} for j in cur.fetchall()])

@app.route('/jobs',methods=['POST'])
def add():
 d=request.json
 conn=db();cur=conn.cursor()
 cur.execute("INSERT INTO jobs(title,company,salary) VALUES(?,?,?)",(d['title'],d['company'],d['salary']))
 conn.commit();return jsonify({'msg':'ok'})

@app.route('/save',methods=['POST'])
def save():
 d=request.json
 conn=db();cur=conn.cursor()
 cur.execute("INSERT INTO saved(job_id) VALUES(?)",(d['job_id'],))
 conn.commit();return jsonify({'msg':'saved'})

@app.route('/upload',methods=['POST'])
def upload():
 f=request.files['file']
 path=os.path.join(UPLOAD_FOLDER,secure_filename(f.filename))
 f.save(path)
 return jsonify({'msg':'uploaded'})

if __name__=='__main__':
 conn=sqlite3.connect('jobs.db')
 cur=conn.cursor()
 cur.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,name TEXT,email TEXT,password TEXT)")
 cur.execute("CREATE TABLE IF NOT EXISTS jobs(id INTEGER PRIMARY KEY,title TEXT,company TEXT,salary TEXT)")
 cur.execute("CREATE TABLE IF NOT EXISTS saved(id INTEGER PRIMARY KEY,job_id INTEGER)")
 conn.commit();conn.close()
 app.run(debug=True)



