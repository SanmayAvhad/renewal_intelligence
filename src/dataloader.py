import pandas as pd
import logging
from config import DATA_DIR
from loggerfile import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

def load_data():
    accounts = pd.read_csv(f"{DATA_DIR}/accounts.csv")

    usage_metrics = pd.read_csv(f"{DATA_DIR}/usage_metrics.csv")

    support_tickets = pd.read_csv(f"{DATA_DIR}/support_tickets.csv")

    nps_responses = pd.read_csv(f"{DATA_DIR}/nps_responses.csv")

    with open(f"{DATA_DIR}/csm_notes.txt", "r", encoding="utf-8") as f:
        csm_notes = f.read()

    with open(f"{DATA_DIR}/changelog.md", "r", encoding="utf-8") as f:
        changelog = f.read()

    return {"accounts": accounts, "usage": usage_metrics, "tickets": support_tickets, "nps": nps_responses, "csm_notes": csm_notes, "changelog": changelog}


if __name__ == "__main__":
    data = load_data()

    for k, v in data.items():
        logger.debug(f"\n==== {k.upper()} ====")

        if isinstance(v, pd.DataFrame):
            logger.debug(v.head())
        else:
            logger.debug(v[:500])
