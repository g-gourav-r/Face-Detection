import sqlite3
from datetime import datetime
import hashlib

# Replace 'your_database.db' with the actual path to your SQLite database file
DATABASE = '../your_database.db'

def init_db():
    try:
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()

        # Create the User table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS User (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                username TEXT UNIQUE,
                password TEXT,
                is_admin BOOLEAN
            )
        ''')

        # Add a dummy entry with is_admin set to 1
        usr_name = input("Enter the usr_name : ")
        password = input("Enter the password : ")
        is_admin = int(input("1 or 0 : "))
        first_name = input("Enter the fname : ")
        last_name = input("Enter the lname : ")

        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        cursor.execute('''
            INSERT INTO User (first_name, last_name, username, password, is_admin)
            VALUES (?, ?, ?, ?, ?)
        ''', (first_name, last_name, usr_name, hashed_password, is_admin))

        # Commit the changes and close the connection
        db.commit()
        db.close()

        print("Database initialization complete.")

    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == '__main__':
    init_db()
