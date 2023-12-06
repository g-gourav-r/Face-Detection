import sqlite3
import base64

def insert_data_into_table(name, image_data):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO your_table (name, image) VALUES (?, ?)', (name, image_data))
        conn.commit()
        print("Data inserted successfully.")
    except Exception as e:
        print(f"Error inserting data: {e}")
        conn.rollback()
    finally:
        conn.close()

def main():
    name = input("Enter the name: ")

    image_path = input("Enter the path to the image file: ")
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()

    # Convert BLOB image data to Base64 encoding
    image_data_base64 = base64.b64encode(image_data).decode('utf-8')

    # Insert data into the table
    insert_data_into_table(name, image_data_base64)

if __name__ == '__main__':
    main()
