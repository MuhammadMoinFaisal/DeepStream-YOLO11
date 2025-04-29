import os
import sqlite3

# Set the path to your predictions folder
PREDICTIONS_FOLDER = 'predictions'  # Change this if your folder name is different

# 1. Connect to (or create) a SQLite database file
conn = sqlite3.connect('predictions.db')  # This file will be created in your current directory
cursor = conn.cursor()

# 2. Create a table if it does not exist already
cursor.execute('''
    CREATE TABLE IF NOT EXISTS detections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        frame_name TEXT,
        class_name TEXT,
        x1 REAL,
        y1 REAL,
        x2 REAL,
        y2 REAL,
        confidence REAL
    )
''')
conn.commit()

# 3. Loop through all .txt files inside the predictions folder
for filename in sorted(os.listdir(PREDICTIONS_FOLDER)):
    if filename.endswith('.txt'):
        frame_name = filename.replace('.txt', '')  # Remove ".txt" from the filename
        file_path = os.path.join(PREDICTIONS_FOLDER, filename)
       
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                parts = line.strip().split(' ')

                # Make sure there are enough parts in the line
                if len(parts) >= 16:
                    class_name = parts[0]
                    x1 = float(parts[4])
                    y1 = float(parts[5])
                    x2 = float(parts[6])
                    y2 = float(parts[7])
                    confidence = float(parts[-1])

                    # Insert into the database
                    cursor.execute('''
                        INSERT INTO detections (frame_name, class_name, x1, y1, x2, y2, confidence)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (frame_name, class_name, x1, y1, x2, y2, confidence))

# 4. Commit and close the database
conn.commit()
conn.close()

print('✅ All predictions have been saved successfully into predictions.db')
