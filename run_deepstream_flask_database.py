from flask import Flask, request, jsonify
import subprocess
import os
import shutil
import signal
import sqlite3

app = Flask(__name__)
deepstream_process = None
config_file = "dynamic_config.txt"
template_file = "deepstream_app_config.txt"
predictions_dir = "predictions"
db_file = "predictions.db"

def create_dynamic_config(rtsp_url):
    if not os.path.exists(template_file):
        raise FileNotFoundError(f"Base config file not found: {template_file}")
    shutil.copy(template_file, config_file)
    with open(config_file, 'r') as file:
        lines = file.readlines()
    with open(config_file, 'w') as file:
        for line in lines:
            if line.strip().startswith("uri="):
                file.write(f'uri={rtsp_url}\n')
            else:
                file.write(line)
    return config_file

def save_predictions_to_db():
    if not os.path.exists(predictions_dir):
        return

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            frame_name TEXT,
            class_name TEXT,
            left REAL,
            top REAL,
            right REAL,
            bottom REAL,
            confidence REAL
        )
    ''')

    for file_name in os.listdir(predictions_dir):
        if file_name.endswith('.txt'):
            frame_name = os.path.splitext(file_name)[0]
            file_path = os.path.join(predictions_dir, file_name)

            with open(file_path, 'r') as file:
                lines = file.readlines()

            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 16:
                    class_name = parts[0]
                    left = float(parts[4])
                    top = float(parts[5])
                    right = float(parts[6])
                    bottom = float(parts[7])
                    confidence = float(parts[-1])

                    cursor.execute('''
                        INSERT INTO predictions (frame_name, class_name, left, top, right, bottom, confidence)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (frame_name, class_name, left, top, right, bottom, confidence))

    conn.commit()
    conn.close()

    # Delete all .txt files
    for file_name in os.listdir(predictions_dir):
        if file_name.endswith('.txt'):
            os.remove(os.path.join(predictions_dir, file_name))

@app.route("/start-stream", methods=["POST"])
def start_stream():
    global deepstream_process

    if deepstream_process is not None:
        return jsonify({"error": "A stream is already running."}), 400

    data = request.get_json()
    rtsp_url = data.get("rtsp_url")

    if not rtsp_url:
        return jsonify({"error": "Missing 'rtsp_url' in request."}), 400

    try:
        config_path = create_dynamic_config(rtsp_url)
        deepstream_process = subprocess.Popen(["deepstream-app", "-c", config_path])
        return jsonify({"message": "DeepStream started.", "pid": deepstream_process.pid}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/stop-stream", methods=["POST"])
def stop_stream():
    global deepstream_process

    if deepstream_process is None:
        return jsonify({"error": "No stream is currently running."}), 400

    try:
        os.kill(deepstream_process.pid, signal.SIGINT)
        deepstream_process.wait()
        deepstream_process = None

        # Save predictions to SQLite DB
        save_predictions_to_db()

        return jsonify({"message": "DeepStream stopped."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "DeepStream Flask API is running."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
