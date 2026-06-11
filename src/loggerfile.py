import logging
import os
from config import LOG_DIR

os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "app.log")

def setup_logging():
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s | %(name)s | %(levelname)s | %(message)s", handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()])

    for noisy_logger in [
        "httpx",
        "httpcore",
        "httpcore.http11",
        "httpcore.connection",
        "google_genai",
        "google_genai.models",
    ]:
        logging.getLogger(noisy_logger).setLevel(logging.ERROR)