# llm_features.py

import json
import math
import re
import pandas as pd
from ollama import chat
from llm_utils import clean_llm_response, extract_json_array
import logging
from loggerfile import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

def csm_fallback(index):

    return {
        "index": index,
        "competitor_mentioned": False,
        "competitors": [],
        "budget_pressure": False,
        "executive_involved": False,
        "security_concern": False,
        "migration_concern": False,
        "product_dissatisfaction": False,
        "support_frustration": False,
        "silent_churn": False,
        "expansion_opportunity": False,
        "renewal_sentiment": "neutral",
        "risk_level": "medium",
    }

def nps_fallback(index):

    return {
        "index": index,
        "comment_sentiment_score": 5,
        "competitor_mentioned": False,
        "competitors": [],
        "budget_pressure": False,
        "product_dissatisfaction": False,
        "support_frustration": False,
        "migration_concern": False,
        "renewal_risk": "medium",
    }

# =====================================================
# Prompt Construction
# =====================================================

def build_batch_prompt(notes):

    formatted_notes = []

    for idx, note in enumerate(notes):

        formatted_notes.append(
            f"""
NOTE_INDEX: {idx}

{note}
"""
        )

    notes_text = "\n\n====================\n\n".join(
        formatted_notes
    )

    prompt = f"""
You are a senior Customer Success analyst.

Your task is to extract structured renewal-risk signals
from customer success notes.

Return ONLY a valid JSON array.

Schema:

[
  {{
    "index": integer,

    "competitor_mentioned": boolean,

    "competitors": [string],

    "budget_pressure": boolean,

    "executive_involved": boolean,

    "security_concern": boolean,

    "migration_concern": boolean,

    "product_dissatisfaction": boolean,

    "support_frustration": boolean,

    "silent_churn": boolean,

    "expansion_opportunity": boolean,

    "renewal_sentiment":
        "positive" |
        "neutral" |
        "negative",

    "risk_level":
        "low" |
        "medium" |
        "high"
  }}
]

Definitions:

competitor_mentioned:
    Competitor products mentioned.

budget_pressure:
    Budget cuts, discount requests,
    procurement pressure, cost concerns.

executive_involved:
    CTO, CIO, VP, CISO, CRO,
    Executive Sponsor involved.

security_concern:
    Security, compliance,
    audit, SOC2, GDPR concerns.

migration_concern:
    SDK migration,
    deprecations,
    platform migration issues.

product_dissatisfaction:
    Complaints about product quality,
    performance, missing features.

support_frustration:
    Complaints about support,
    unresolved tickets,
    slow responses.

silent_churn:
    Positive sentiment but evidence
    customer is leaving or reducing usage.

expansion_opportunity:
    Upsell, seat expansion,
    plan upgrade opportunities.

Analyze these notes:

{notes_text}
"""

    return prompt


# =====================================================
# NPS Prompt Construction
# =====================================================

def build_nps_batch_prompt(comments):

    formatted_comments = []

    for idx, comment in enumerate(comments):

        formatted_comments.append(
            f"""
COMMENT_INDEX: {idx}

{comment}
"""
        )

    comments_text = (
        "\n\n====================\n\n"
        .join(formatted_comments)
    )

    prompt = f"""
You are a senior Customer Success analyst.

The comments may be written in ANY language.

Analyze the meaning of the comment regardless
of language.

Do NOT translate the comment.

Return ONLY a valid JSON array.

Schema:

[
  {{
    "index": integer,

    "comment_sentiment_score": integer,

    "competitor_mentioned": boolean,

    "competitors": [string],

    "budget_pressure": boolean,

    "product_dissatisfaction": boolean,

    "support_frustration": boolean,

    "migration_concern": boolean,

    "renewal_risk":
        "low" |
        "medium" |
        "high"
  }}
]

Definitions:

comment_sentiment_score:

1 =
Extremely negative

5 =
Neutral

10 =
Extremely positive

competitor_mentioned:
Customer references competitor products.

budget_pressure:
Pricing complaints,
discount requests,
cost concerns.

product_dissatisfaction:
Complaints about product quality,
performance,
usability,
missing features.

support_frustration:
Complaints about support,
ticket handling,
response time.

migration_concern:
Migration efforts,
platform replacement,
SDK concerns,
deprecation concerns.

Analyze these comments:

{comments_text}
"""

    return prompt


def extract_batch(prompt):
    response = chat(
        model="qwen3:8b",
        think=False,
        messages=[{"role": "user", "content": prompt}],
        options={
            "temperature": 0,
            "num_predict": 4096,
            "num_ctx": 8192
        }
    )
    text = clean_llm_response(response["message"]["content"])
    return extract_json_array(text)


def safe_extract( items, prompt_builder, fallback_rows ):

    try:
        prompt = prompt_builder(items)

        return extract_batch( prompt=prompt )

    except Exception as e:

        logger.warning(
            f"Extraction failed: {e}"
        )

        return [
            fallback_rows(i)
            for i in range(len(items))
        ]

def build_feature_table(
    source_df,
    text_column,
    prompt_builder,
    fallback_fn,
    batch_size=10
):

    all_rows = []

    texts = (
        source_df[text_column]
        .fillna("")
        .astype(str)
        .tolist()
    )

    num_batches = math.ceil(
        len(texts) / batch_size
    )

    for batch_num in range(num_batches):

        start = batch_num * batch_size
        end = start + batch_size

        batch_texts = texts[start:end]

        results = safe_extract(
            items=batch_texts,
            prompt_builder=prompt_builder,
            fallback_rows=fallback_fn
        )

        for row in results:

            row["_global_index"] = (
                start + row["index"]
            )

        all_rows.extend(results)

    signal_df = (
        pd.DataFrame(all_rows)
        .sort_values("_global_index")
        .reset_index(drop=True)
    )

    signal_df.drop(
        columns=[
            "index",
            "_global_index"
        ],
        inplace=True,
        errors="ignore"
    )

    return pd.concat(
        [
            source_df.reset_index(drop=True),
            signal_df
        ],
        axis=1
    )

def build_csm_feature_table(
    csm_df,
    batch_size=10
):

    return build_feature_table(
        source_df=csm_df,
        text_column="notes",
        prompt_builder=build_batch_prompt,
        fallback_fn=csm_fallback,
        batch_size=batch_size
    )

def build_nps_feature_table(
    nps_df,
    batch_size=5
):

    result = build_feature_table(
        source_df=nps_df,
        text_column="verbatim_comment",
        prompt_builder=build_nps_batch_prompt,
        fallback_fn=nps_fallback,
        batch_size=batch_size
    )

    result["nps_comment_mismatch"] = (
        (
            result["score"] >= 8
        )
        &
        (
            result["comment_sentiment_score"] <= 4
        )
    ).astype(int)

    return result