import sqlite3

def Insert():
    conn = sqlite3.connect('database.db')

    cursor = conn.cursor()

    # Example: Inserting an image into the Target table
    image_path = 'me.jpg'
    target_name = input("Enter the name of the target: ")
    # Read the image data
    with open(image_path, 'rb') as f:
        image_data = f.read()

    # Insert the image data into the Target table
    cursor.execute('''
        INSERT INTO Target (name, image) VALUES (?, ?)
    ''', (target_name, image_data))

    conn.commit()
    conn.close()

import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('database.db')

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

# Example: Retrieving an image from the Target table
target_name_to_retrieve = input("Enter the name of the target to retrieve: ")

# Execute the query to retrieve the image data
cursor.execute('''
    SELECT image FROM Target WHERE name = ?
''', (target_name_to_retrieve,))

# Fetch the result
result = cursor.fetchone()

# Check if the result is not empty
if result:
    image_data = result[0]

    # Specify the path to save the retrieved image
    output_image_path = 'retrieved_image.jpg'

    # Write the image data to a file
    with open(output_image_path, 'wb') as f:
        f.write(image_data)

    print(f"Image retrieved and saved to {output_image_path}")
else:
    print(f"No image found for target with name: {target_name_to_retrieve}")

# Close the connection
conn.close()
