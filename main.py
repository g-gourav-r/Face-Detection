from flask import Flask, render_template, redirect, url_for, request
import sqlite3
import hashlib
import os


app = Flask(__name__)

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
                        return render_template('admin_dashboard.html')
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


    with sqlite3.connect("your_database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO pictures (name, image) VALUES (?, ?)", (name, image_data))
        last_row_id = cursor.lastrowid

    return last_row_id 


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
    # Get the value of 'is_admin' from the form data
    is_admin = int(request.form['is_admin'])

    # Update the 'is_admin' value in the database
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

@app.route('/upload_picture', methods=['GET', 'POST'])
def upload_picture():
    if request.method == 'POST':
        name = request.form['name']
        file = request.files['file']

        if name and file:
            last_row_id = save_file_and_update_db(name, file)
            return render_template('add_person.html', entry_id=last_row_id, show_success=True)

    return render_template('add_person.html', show_success=False)

if __name__ == '__main__':
    app.run(debug=True)
