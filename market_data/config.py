"""Configuration module for market data downloader."""
import os
from pathlib import Path
from dotenv import load_dotenv

# --- Environment Setup ---

# 1. Locate the .env file relative to this config file.
# This ensures the library works from anywhere (Strategies, Desktop, etc.)
# Structure: DATA_ENGINE/market_data/config.py -> we go up 2 levels to find DATA_ENGINE/.env
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
ENV_PATH = PROJECT_ROOT / '.env'

# 2. Load environment variables
# We explicitly specify the path to avoid looking in the current working directory
load_dotenv(dotenv_path=ENV_PATH)

# --- API Configuration ---

EODHD_API_KEY = os.getenv('EODHD_API_KEY')
if not EODHD_API_KEY:
    raise ValueError(
        f"EODHD_API_KEY not found in environment variables.\n"
        f"Tried loading .env from: {ENV_PATH}\n"
        "Create a .env file in the DATA_ENGINE root with: EODHD_API_KEY=your_api_key"
    )

EODHD_BASE_URL = "https://eodhd.com/api"

# --- Data Source Policy ---
# switching doesn't change anything yet, but we let the option open for future sources and incoming changes
PRIMARY_SOURCE = "EODHD"  # Single source for consistency
ALLOW_FALLBACK = False    # No fallback to ensure data integrity

# --- OS Specifics ---

# Windows reserved filenames that cannot be created
WINDOWS_RESERVED = [
    'CON', 'PRN', 'AUX', 'NUL',
    'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
    'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
]

# --- Directory Structure ---


# We use the PROJECT_ROOT defined at the top of the file
DATA_DIR = PROJECT_ROOT / 'database/raw_data'
SPLIT_DIR = PROJECT_ROOT / 'database/split'
DIVIDEND_DIR = PROJECT_ROOT / 'database/dividend'
LOG_DIR = PROJECT_ROOT / 'logs'

# --- Default Settings ---

DEFAULT_THREADS = 30       # Number of concurrent downloads
REQUEST_TIMEOUT = 10        # Seconds before giving up on a request
MAX_RETRIES = 3             # Number of retries for transient errors (5xx, 429)
RETRY_DELAY = 2             # Base delay in seconds between retries