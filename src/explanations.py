import json
import re
import pandas as pd
from ollama import chat

import logging
from loggerfile import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

def build_batch_explanation_prompt(
    accounts
):

    account_text = []

    for idx, account in enumerate(accounts):

        account_text.append(
            f"""
ACCOUNT_INDEX: {idx}

Account:
{account.get("account_name")}

Risk Score:
{account.get("risk_score")}

Risk Tier:
{account.get("risk_tier")}

ARR:
{account.get("arr")}

Risk Reasons:
{account.get("risk_reasons")}

API Change:
{account.get("api_change_pct")}

Active User Change:
{account.get("active_users_change_pct")}

NPS:
{account.get("latest_nps")}

Competitor Mentioned:
{account.get("competitor_mentioned")}

Budget Pressure:
{account.get("budget_pressure")}

Executive Involved:
{account.get("executive_involved")}

Migration Concern:
{account.get("migration_concern")}

Security Concern:
{account.get("security_concern")}
"""
        )

    accounts_text = "\n\n====================\n\n".join(
        account_text
    )

    return f"""
You are a Senior Customer Success strategist.

For each account generate:

1. Executive summary
2. Key risk factors
3. Recommended actions

Return ONLY valid JSON.

Schema:

[
  {{
    "index": integer,
    "summary": "...",
    "key_risk_factors": [
        "...",
        "..."
    ],
    "recommended_actions": [
        "...",
        "..."
    ]
  }}
]

Accounts:

{accounts_text}
"""

def generate_explanations_batch( accounts ):
    prompt = build_batch_explanation_prompt( accounts )
    response = chat(
        model="qwen3:8b",
        think=False,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    text = ( response["message"]["content"] .strip() )
    text = re.sub( r"^```json\s*", "", text )
    text = re.sub( r"^```\s*", "", text )
    text = re.sub( r"\s*```$", "", text )
    match = re.search( r"\[.*\]", text, flags=re.DOTALL )
    if not match:
        raise ValueError( f"No JSON array found:\n{text}" )
    return json.loads( match.group(0) )

def build_explanation_report( risk_report_df, batch_size=10 ):

    explanation_rows = []

    total = len(risk_report_df)

    for start in range(
        0,
        total,
        batch_size
    ):

        end = start + batch_size

        batch_df = (
            risk_report_df.iloc[start:end]
        )

        accounts = (
            batch_df.to_dict(
                orient="records"
            )
        )

        results = (
            generate_explanations_batch(
                accounts
            )
        )

        explanation_rows.extend(
            results
        )

    explanation_df = pd.DataFrame(
        explanation_rows
    )

    explanation_df = (
        explanation_df
        .sort_values("index")
        .reset_index(drop=True)
    )

    explanation_df = explanation_df.drop(
        columns=["index"],
        errors="ignore"
    )

    final_report = pd.concat(
        [
            risk_report_df.reset_index(
                drop=True
            ),
            explanation_df
        ],
        axis=1
    )

    return final_report

def save_final_report(
    report_df,
    output_path="outputs/final_risk_report.csv"
):

    report_df.to_csv(
        output_path,
        index=False
    )

    logger.info(
        f"Saved report to {output_path}"
    )

