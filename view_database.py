import sqlite3

conn = sqlite3.connect('predictions.db')
cursor = conn.cursor()

for row in cursor.execute('SELECT * FROM detections LIMIT 10'):
    print(row)

conn.close()

