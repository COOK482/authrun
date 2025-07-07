import sys
from flask import Flask, render_template, request, jsonify
import subprocess
import threading
import time
import pyotp
import json
from datetime import datetime, timezone
from priv_sets import (
    SECRET_KEY,
    SCRIPT_PATH,
    DEBUG_SCRIPT_PATH,
    LOCKOUT_DURATION,
    DEBUG_LOCKOUT_DURATION,
    DEPLOY_HISTORY_FILE,
    DEBUG_DEPLOY_HISTORY_FILE,
    LOG_FILE,
)

# Determine if debug mode is enabled
debug_mode = "--debug" in sys.argv

# Select appropriate settings based on debug mode
selected_secret_key = SECRET_KEY
selected_script_path = DEBUG_SCRIPT_PATH if debug_mode else SCRIPT_PATH
selected_lockout_duration = (
    DEBUG_LOCKOUT_DURATION if debug_mode else LOCKOUT_DURATION
)
selected_history_file = (
    DEBUG_DEPLOY_HISTORY_FILE if debug_mode else DEPLOY_HISTORY_FILE
)

app = Flask(__name__)
totp = pyotp.TOTP(selected_secret_key)

last_deploy_time = 0
last_deploy_status = "Not deployed yet"
deploy_process = None


def save_deploy_history():
    try:
        with open(selected_history_file, "r") as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []

    history.append(
        {
            "time": (
                datetime.fromtimestamp(
                    last_deploy_time, tz=timezone.utc
                ).isoformat()
            ),
            "status": last_deploy_status,
        }
    )

    history = history[-5:]

    with open(selected_history_file, "w") as f:
        json.dump(history, f)


def update_deploy_status():
    global last_deploy_status, deploy_process
    if deploy_process:
        # Wait for the process to finish and capture output
        stdout, stderr = deploy_process.communicate()
        exit_code = deploy_process.returncode

        # Update the status based on the return code
        if exit_code == 0:
            last_deploy_status = "Deploy succeeded"
        else:
            last_deploy_status = "Deploy failed"

            # Write stdout and stderr to the log file on failure
            with open(LOG_FILE, "a") as log_file:
                log_file.write(
                    f"Deployment failed at {datetime.now(timezone.utc).isoformat()}\n"
                )
                log_file.write("STDOUT:\n" + stdout.decode("utf-8") + "\n")
                log_file.write("STDERR:\n" + stderr.decode("utf-8") + "\n\n")

        deploy_process = None
        save_deploy_history()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/verify", methods=["POST"])
def verify():
    global last_deploy_time, last_deploy_status, deploy_process
    current_time = time.time()
    if (
        current_time - last_deploy_time < selected_lockout_duration
        or deploy_process
    ):
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
            ["/bin/bash", selected_script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        threading.Thread(target=update_deploy_status).start()
        return jsonify(
            {
                "message": (
                    "Auth success. Deployment script is running. Please wait for ~2 mins."
                ),
                "success": True,
            }
        )
    else:
        return jsonify({"message": "Auth failed.", "success": False})


@app.route("/get_deploy_status", methods=["GET"])
def get_deploy_status():
    try:
        with open(selected_history_file, "r") as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []

    return jsonify({"history": history})


if __name__ == "__main__":
    app.run(debug=True)
