import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data_files")
LOG_DIR = os.path.join(BASE_DIR, "logs")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)