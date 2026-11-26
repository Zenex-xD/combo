# language: Python 3.11 — config.py (corrected)
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ["BOT_TOKEN"]
WORKERS = int(os.getenv("WORKERS", "25"))
RATE = float(os.getenv("RATE", "0.05"))
DB_PATH = os.getenv("DB_PATH", "hits.db")
PROXY_FILE = os.getenv("PROXY_FILE", "proxies.txt")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

SERVICE_NAMES = ["amazon", "prime", "steam", "epic"]
STATUSES = ["HIT", "2FA", "LOCKED", "INVALID", "ERROR"]
