import cv2
import face_recognition
import numpy as np
import sqlite3
import pickle

# Function to connect to the SQLite database
def connect_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    return conn, c

# Connect to the database
db_conn, db_cursor = connect_db()

# Load existing encodings from the database
db_cursor.execute('SELECT name, encoding FROM users')
rows = db_cursor.fetchall()
encoded_face_train = [(row[0], pickle.loads(row[1])) for row in rows]

cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
    faces_in_frame = face_recognition.face_locations(imgS)
    encoded_faces = face_recognition.face_encodings(imgS, faces_in_frame)

    for encode_face, faceloc in zip(encoded_faces, faces_in_frame):
        matches = face_recognition.compare_faces([enc for _, enc in encoded_face_train], encode_face)
        faceDist = face_recognition.face_distance([enc for _, enc in encoded_face_train], encode_face)
        matchIndex = np.argmin(faceDist)

        if matches[matchIndex]:
            name = encoded_face_train[matchIndex][0].upper().lower()
            y1, x2, y2, x1 = faceloc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 5), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow('webcam', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Close the database connection
db_conn.close()
cv2.destroyAllWindows()
