from flask import Flask, request, jsonify
import subprocess
import os
import shutil
import signal

app = Flask(__name__)
deepstream_process = None
config_file = "dynamic_config.txt"
template_file = "deepstream_app_config.txt"


def create_dynamic_config(rtsp_url):
    """
    Creates a DeepStream config file with the provided RTSP URL.
    """
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
        return jsonify({"message": "DeepStream stopped."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "DeepStream Flask API is running."})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
