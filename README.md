# AuthRun: 2FA Script Execution System

This project provides a Flask-based web interface for securely running scripts with two-factor authentication (2FA) and displaying script execution status. It's designed to manage secure, authenticated access to any backend script, enforcing a cooldown period between executions and showing the latest status update.

While this system is designed to serve as the deploy admin for simplified deployment in COOK482, it can be adapted for various other applications requiring secure script execution with 2FA and execution tracking.

### Project Structure

- **`app.py`**: Main Flask application file with an optional debug mode
- **`history.json`**: Logs script execution history
- **`env/`**: Virtual environment folder
- **`priv_sets.example.py`**: Example configuration file for private settings
- **`priv_sets.py`**: Contains `SECRET_KEY`, `SCRIPT_PATH`, and other private settings
- **`qrcode_gen.py`**: Generates a QR code for 2FA setup
- **`qrcode.png`**: Generated QR code image for 2FA setup
- **`README.md`**: Project documentation
- **`requirements.txt`**: List of required dependencies
- **`templates/`**: Directory for HTML templates
- **`test_script_output.txt`**: Sample output from the test script
- **`test_script.sh`**: Example script for testing execution

### Requirements

Install necessary dependencies with:

```
pip install -r requirements.txt
```

### Configuration

1. 2FA Setup: copy `priv_sets.example.py` to `priv_sets.py`
   - Generate a `SECRET_KEY` using `pyotp.random_base32()`.
   - Set `SCRIPT_PATH` to the path of the script you want to execute.
   - Optionally set `QR_CODE_DESCRIPTION` and `QR_CODE_ISSUER` if you want to generate QR Code with description and issuer.
2. **Generate QR Code**: Run `qrcode_gen.py` to create a `qrcode.png` image, which can be scanned with an authenticator app for 2FA setup.

### Debug Mode

To use alternative settings for testing, you can run the application in debug mode. This mode uses shorter lockout durations and different script paths:

```
python app.py --debug
```

In debug mode, the following settings will apply:

- **`DEBUG_SCRIPT_PATH`**: Path for testing scripts (e.g., `test_script.sh`).
- **`DEBUG_LOCKOUT_DURATION`**: Cooldown duration for debug mode.
- **`DEBUG_DEPLOY_HISTORY_FILE`**: History file for debugging purposes (e.g., `history_debug.json`).

### Usage

1. **Run the Application**:

   ```
   python app.py
   ```

2. **Access the Interface**: Open `http://127.0.0.1:5000` in your browser.

3. **Execute Script with 2FA**: Enter the 2FA code to authorize script execution. Once authorized, the script will execute, and the system will display the status updates.

4. **Check Execution Status**: Use the `/get_deploy_status` endpoint to view the latest execution status.

### Cooldown Period

A lockout period is enforced after each execution to prevent multiple runs in quick succession. The duration is 3 minutes in normal mode and 1 second in debug mode.

### Example Endpoint Usage

- **Verify 2FA and Trigger Script Execution**: `POST /verify` with form data including `code`.
- **Get Execution Status**: `GET /get_deploy_status`

### Notes

- Keep `priv_sets.py` secure to protect sensitive information.
- Customize `index.html` within the `templates` directory to modify the web interface.
- Use `--debug` for testing purposes without affecting production data.

This system can securely run various scripts, not limited to deployments, with 2FA authorization and status monitoring.
