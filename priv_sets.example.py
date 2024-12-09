import pyotp

SECRET_KEY = ""  #  print(pyotp.random_base32())
SCRIPT_PATH = ""
DEBUG_SCRIPT_PATH = "./test_script.sh"
LOCKOUT_DURATION = 180
DEBUG_LOCKOUT_DURATION = 1
DEPLOY_HISTORY_FILE = "history.json"
DEBUG_DEPLOY_HISTORY_FILE = "histor_debug.json"
QR_CODE_DESCRIPTION = ""
QR_CODE_ISSUER = ""
LOG_FILE = "error.log"
