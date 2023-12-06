from flask import Flask, render_template
import sqlite3
import base64

app = Flask(__name__)

@app.route('/your_route')
def your_route():
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    # Assuming 'image' is the BLOB column in your table
    cursor.execute('SELECT name, image FROM your_table LIMIT 5')  # Adjust your query as needed
    data = cursor.fetchall()

    conn.close()

    # Convert BLOB image data to Base64 encoding
    for row in data:
        if row[1] is not None:
            row[1] = f"data:image/png;base64,{base64.b64encode(row[1]).decode('utf-8')}"

    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
