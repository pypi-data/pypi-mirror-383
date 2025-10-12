import datetime
import sys

COLORS = {
    "INFO": "\033[94m",     # Blue
    "WARNING": "\033[93m",  # Yellow
    "ERROR": "\033[91m",    # Red
    "SUCCESS": "\033[92m",  # Green
    "RESET": "\033[0m"
}

def log(level, message):
    color = COLORS.get(level, "")
    reset = COLORS["RESET"]
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sys.stdout.write(f"{color}[{timestamp}] [{level}] {message}{reset}\n")

def info(msg): log("INFO", msg)
def warn(msg): log("WARNING", msg)
def error(msg): log("ERROR", msg)
def success(msg): log("SUCCESS", msg)
