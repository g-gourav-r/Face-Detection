from flask import Flask, render_template, redirect, url_for, request, Response
import sqlite3
import hashlib
import os
from PIL import Image
import sqlite3
from io import BytesIO
import base64
import cv2
from datetime import datetime

app = Flask(__name__)
video_capture = cv2.VideoCapture(0)  # 0 corresponds to the default camera

def generate_frames():
    while True:
        success, frame = video_capture.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/admin_dashboard')
def admin_dashboard():
    data = show_data()
    return render_template('admin_dashboard.html', targets=data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

        conn = sqlite3.connect('your_database.db')
        c = conn.cursor()
        print(conn)
        try:
            c.execute('SELECT * FROM user WHERE username=?', (username,))
            user = c.fetchone()
            print(user)
            if user is None:
                error = 'User does not exist.'
            else:
                if user[4] == hashed_password and user[3] == username:
                    if user[5] == 0 :
                        return render_template('user_dashboard.html')
                    else:
                        return redirect(url_for('admin_dashboard'))

                else:
                    error = 'Wrong Password'
        except Exception as e:
            print(f"An error occurred: {e}")
            error = 'An wow error occurred. Please try again.'
        finally:
            conn.close()

    return render_template('login.html', error=error)



def save_file_and_update_db(name, file):
    upload_folder = "missing person"
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    file_extension = file.filename.split(".")[-1].lower()
    if file_extension != "jpg":
        return None

    new_filename = f"{name}.{file_extension}"
    file_path = os.path.join(upload_folder, new_filename)


    file.save(file_path)


    with open(file_path, 'rb') as image_file:
        image_data = image_file.read()
        current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


    with sqlite3.connect("your_database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO missingPerson (name, image, status,location,location_image,time,to_be_tracked,uploadtime) VALUES (?, ?,0,NULL,NULL,NULL,1,CURRENT_TIMESTAMP)", (name, image_data))
        last_row_id = cursor.lastrowid

    return last_row_id 

def show_data():
    connection = sqlite3.connect("your_database.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM missingPerson")
    targets = cursor.fetchall()

    decoded_targets = []
    for target in targets:
        target_id, name, image, status,location,location_image,time,to_be_tracked,uploadtime = target
        try:
            decoded_image = base64.b64encode(image).decode('utf-8')
        except Exception as e:
            print(f"Error decoding image: {e}")
            decoded_image = None
        decoded_targets.append({
            'target_id': target_id,
            'name': name,
            'decoded_image': decoded_image,
            'status': status,
            'last location': location,
            'time': time,
            'decoded_location_image': base64.b64encode(location_image).decode('utf-8') if location_image else None,
            'to_be_tracked':to_be_tracked,
            'uploadTime':uploadtime
        })

    connection.close()

    return decoded_targets
@app.route('/logs')
def logs():
    data = show_data()
    return render_template('logs.html',  data=data)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    error = None
    status = None
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        password = request.form['password']
        is_admin = 1 if 'is_admin' in request.form else 0

        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

        conn = sqlite3.connect('your_database.db')
        c = conn.cursor()

        try:
            # Check if the username already exists
            c.execute('SELECT * FROM User WHERE username=?', (username,))
            existing_user = c.fetchone()

            if existing_user:
                error = 'Username already exists. Please choose another username.'
            elif len(password) < 6:
                error = 'Password should be at least 6 characters long.'
            elif password != request.form['confirm_password']:
                error = 'Passwords do not match.'
            else:
                # Insert the new user into the database
                c.execute('INSERT INTO User (first_name, last_name, username, password, is_admin) VALUES (?, ?, ?, ?, ?)',
                          (first_name, last_name, username, hashed_password, is_admin))
                conn.commit()
                status = f'{username} added as {"User" if is_admin == 0 else "Admin"}'
        except Exception as e:
            print(f"An error occurred: {e}")
            error = 'An error occurred. Please try again.'
        finally:
            conn.close()

    return render_template('add_user.html', error=error, status=status)

@app.route('/manage_user')
def manage_user():
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM User')
        users = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        users = []
    conn.close()
    return render_template('manage_user.html', users=users)

@app.route('/toggle_admin/<int:user_id>', methods=['POST'])
def toggle_admin(user_id):
    is_admin = int(request.form['is_admin'])
    conn = sqlite3.connect('your_database.db')
    try:
        with conn:
            conn.execute("UPDATE User SET is_admin = ? WHERE user_id = ?", (is_admin, user_id))
    except Exception as e:
        print(f"An error occurred while updating is_admin: {e}")
    finally:
        conn.close()
    return redirect(url_for('manage_user'))

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    # Delete the user entry from the database
    conn = sqlite3.connect('your_database.db')
    try:
        with conn:
            conn.execute("DELETE FROM User WHERE user_id = ?", (user_id,))
    except Exception as e:
        print(f"An error occurred while deleting user: {e}")
    finally:
        conn.close()

    return redirect(url_for('manage_user'))

@app.route('/toggle_search/<int:id>', methods=['POST'])
def toggle_search(id):
    to_be_tracked = int(request.form['to_be_tracked'])
    print(id,to_be_tracked)
    conn = sqlite3.connect('your_database.db')
    try:
        with conn:
            conn.execute("UPDATE missingPerson SET to_be_tracked = ? WHERE id = ?", (to_be_tracked, id))
    except Exception as e:
        print(f"An error occurred while updating to_be_tracked: {e}")
    finally:
        conn.close()
    return redirect(url_for('logs'))


@app.route('/upload_picture', methods=['GET', 'POST'])
def upload_picture():
    if request.method == 'POST':
        name = request.form['name']
        file = request.files['file']

        if name and file:
            last_row_id = save_file_and_update_db(name, file)
            return render_template('add_person.html', entry_id=last_row_id, show_success=True)

    return render_template('add_person.html', show_success=False)


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)