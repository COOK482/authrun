from flask import Flask, render_template, request, jsonify
import subprocess
import threading
import time
import pyotp
import json
from datetime import datetime, timezone
from priv_sets import SECRET_KEY, SCRIPT_PATH

app = Flask(__name__)
totp = pyotp.TOTP(SECRET_KEY)

last_deploy_time = 0
last_deploy_status = "Not deployed yet"
LOCKOUT_DURATION = 180
DEPLOY_HISTORY_FILE = "history.json"
deploy_process = None


def save_deploy_history():
    try:
        with open(DEPLOY_HISTORY_FILE, "r") as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []

    history.append(
        {
            "time": datetime.fromtimestamp(
                last_deploy_time, tz=timezone.utc
            ).isoformat(),
            "status": last_deploy_status,
        }
    )

    history = history[-5:]

    with open(DEPLOY_HISTORY_FILE, "w") as f:
        json.dump(history, f)


def update_deploy_status():
    global last_deploy_status, deploy_process
    if deploy_process:
        deploy_process.wait()
        exit_code = deploy_process.returncode
        last_deploy_status = (
            "Deploy succeeded" if exit_code == 0 else "Deploy failed"
        )
        deploy_process = None
        save_deploy_history()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/verify", methods=["POST"])
def verify():
    global last_deploy_time, last_deploy_status, deploy_process
    current_time = time.time()
    if current_time - last_deploy_time < LOCKOUT_DURATION or deploy_process:
        return jsonify(
            {
                "message": "Backend is deploying or cooling down, please wait.",
                "success": False,
            }
        )

    code = request.form["code"]
    if totp.verify(code):
        last_deploy_time = current_time
        last_deploy_status = "Deploying"
        deploy_process = subprocess.Popen(
            ["/bin/zsh", SCRIPT_PATH],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        threading.Thread(target=update_deploy_status).start()
        return jsonify(
            {
                "message": "Auth success. Deployment script is running. Please wait for ~2 mins.",
                "success": True,
            }
        )
    else:
        return jsonify({"message": "Auth failed.", "success": False})


@app.route("/get_deploy_status", methods=["GET"])
def get_deploy_status():
    try:
        with open(DEPLOY_HISTORY_FILE, "r") as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []

    return jsonify({"history": history})


if __name__ == "__main__":
    app.run(debug=True)
