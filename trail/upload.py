import cv2
import face_recognition
import numpy as np
import sqlite3
import pickle
from flask import Flask, render_template, request

app = Flask(__name__)

# Function to connect to the SQLite database
def connect_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL,
                 encoding BLOB NOT NULL)''')
    conn.commit()
    return conn, c

# Connect to the database
db_conn, db_cursor = connect_db()

# Function to insert a new user into the database
def insert_user(name, encoding):
    db_cursor.execute('INSERT INTO users (name, encoding) VALUES (?, ?)', (name, encoding))
    db_conn.commit()

@app.route('/')
def home():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file part"
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    
    if file and allowed_file(file.filename):
        name = request.form['name']
        image = cv2.imdecode(np.fromstring(file.read(), np.uint8), cv2.IMREAD_COLOR)
        encoding = face_recognition.face_encodings(image)[0]

        # Insert the new user into the database
        insert_user(name, pickle.dumps(encoding))
        
        return f'Successfully uploaded and encoded {name}'
    else:
        return "Invalid file type"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg'}

if __name__ == '__main__':
    app.run(debug=True)
