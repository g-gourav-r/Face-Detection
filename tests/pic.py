import sqlite3
from datetime import datetime
import hashlib
import os

# Replace 'your_database.db' with the actual path to your SQLite database file
DATABASE = '../your_database.db'

def init_db():
    try:
        db = sqlite3.connect(DATABASE)
        cursor = db.cursor()
        # Add a dummy entry with is_admin set to 1
        name = input("Enter the name : ")
        status = int(input("1 or 0 : "))
        image_path = input("Enter the path to the image file: ")

        # Check if the file path is valid
        if os.path.isfile(image_path):
            with open(image_path, 'rb') as image_file:
                # Read the image file content
                image_data = image_file.read()

        cursor.execute('''
            INSERT INTO Target (name, image, status)
            VALUES (?, ?, ?)
        ''', (name, image_data, status))

        # Commit the changes and close the connection
        db.commit()
        db.close()

        print("Database initialization complete.")

    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == '__main__':
    init_db()
