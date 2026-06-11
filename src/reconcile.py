import re
import pandas as pd
from datetime import datetime
from rapidfuzz import process, fuzz
from llm import llm_extract_headers
import logging
from loggerfile import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def normalize_name(name):
    return (str(name).lower().replace(".", "").replace(",", "").strip())


def build_account_lookup(accounts_df):
    return {
        normalize_name(name): acc_id
        for acc_id, name in zip(
            accounts_df["account_id"],
            accounts_df["account_name"]
        )
    }


def fuzzy_match_account(raw_name, lookup, threshold=75):
    raw_name = normalize_name(raw_name)

    match = process.extractOne(
        raw_name,
        list(lookup.keys()),
        scorer=fuzz.token_sort_ratio
    )

    if match is None:
        return None, None

    matched_name, score, _ = match

    if score >= threshold:
        return matched_name, lookup[matched_name]

    return None, None


def parse_csm_notes(notes_text, accounts_df):
    name_to_id = build_account_lookup(accounts_df)

    id_to_name = dict(zip(accounts_df["account_id"], accounts_df["account_name"]))

    blocks = [
        block.strip()
        for block in re.split(
            r"\n\s*---\s*\n",
            notes_text
        )
        if block.strip()
    ]

    headers = [
        block.split("\n")[0]
        for block in blocks
    ]

    extracted_rows = llm_extract_headers(headers)

    records = []

    for block, extracted in zip(blocks, extracted_rows):
        date = extracted.get("date")
        account_id = extracted.get("account_id")
        raw_company_name = extracted.get("company_name")

        company_name = raw_company_name
        if not date and not account_id and not raw_company_name:
            continue

        if account_id and not raw_company_name:
            company_name = id_to_name.get(account_id)

        elif raw_company_name and not account_id:
            company_name, account_id = fuzzy_match_account(raw_company_name, name_to_id)

        elif raw_company_name and account_id:
            company_name, matched_id = fuzzy_match_account(raw_company_name, name_to_id)

            if (matched_id and matched_id != account_id):
                logger.info(f"Mismatch detected: account_id={account_id}, company={company_name}, fuzzy_match={matched_id}")

        records.append({"date": date, "account_id": account_id, "company_name": company_name, "notes": block})
        logger.debug(f"CSM notes: {records}")

    return pd.DataFrame(records)