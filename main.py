from flask import Flask, render_template, redirect, url_for, request
import sqlite3
import hashlib

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
        try:
            c.execute('SELECT * FROM user WHERE username=?', (username,))
            user = c.fetchone()
            if user is None:
                error = 'User does not exist.'
            else:
                if user[4] == hashed_password and user[3] == username:
                    if user[5] == 0 :
                        return "Welcome User"
                    else:
                        return "Welcome Admin"
                else:
                    error = 'Wrong Password'
        except Exception as e:
            print(f"An error occurred: {e}")
            error = 'An wow error occurred. Please try again.'
        finally:
            conn.close()

    return render_template('login.html', error=error)

if __name__ == '__main__':
    app.run(debug=True)
