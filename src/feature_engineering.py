# feature_engineering.py

import pandas as pd

# =====================================================

# Usage Features

# =====================================================

def build_usage_features(usage_df):

    usage_df = usage_df.copy()

    usage_df["month"] = pd.to_datetime(
        usage_df["month"]
    )

    usage_df = usage_df.sort_values(
        ["account_id", "month"]
    )

    records = []

    for account_id, group in usage_df.groupby(
        "account_id"
    ):

        first = group.iloc[0]
        last = group.iloc[-1]

        records.append(
            {
                "account_id": account_id,

                "latest_sdk_version":
                    last["sdk_version"],

                "api_change_pct":
                    round(
                        (
                            (
                                last["api_calls"]
                                - first["api_calls"]
                            )
                            /
                            max(
                                first["api_calls"],
                                1
                            )
                        ) * 100,
                        2
                    ),

                "content_change_pct":
                    round(
                        (
                            (
                                last[
                                    "content_entries_created"
                                ]
                                -
                                first[
                                    "content_entries_created"
                                ]
                            )
                            /
                            max(
                                first[
                                    "content_entries_created"
                                ],
                                1
                            )
                        ) * 100,
                        2
                    ),

                "active_users_change_pct":
                    round(
                        (
                            (
                                last["active_users"]
                                -
                                first["active_users"]
                            )
                            /
                            max(
                                first["active_users"],
                                1
                            )
                        ) * 100,
                        2
                    ),

                "workflow_change_pct":
                    round(
                        (
                            (
                                last[
                                    "workflows_triggered"
                                ]
                                -
                                first[
                                    "workflows_triggered"
                                ]
                            )
                            /
                            max(
                                first[
                                    "workflows_triggered"
                                ],
                                1
                            )
                        ) * 100,
                        2
                    ),

                "latest_api_calls":
                    last["api_calls"],

                "latest_active_users":
                    last["active_users"],
            }
        )

    return pd.DataFrame(records)

# =====================================================

# Ticket Features

# =====================================================

def build_ticket_features(ticket_df):

    priority_map = {
        "P1": 10,
        "P2": 5,
        "P3": 2,
        "P4": 1,
    }

    ticket_df = ticket_df.copy()

    ticket_df["priority_score"] = (
        ticket_df["priority"]
        .map(priority_map)
        .fillna(0)
    )

    return (
        ticket_df
        .groupby("account_id")
        .agg(
            ticket_count=(
                "account_id",
                "size"
            ),

            p1_ticket_count=(
                "priority",
                lambda x:
                (x == "P1").sum()
            ),

            open_ticket_count=(
                "status",
                lambda x:
                (
                    x.str.lower()
                    == "open"
                ).sum()
            ),

            avg_resolution_hours=(
                "resolution_time_hours",
                "mean"
            ),

            priority_score_total=(
                "priority_score",
                "sum"
            ),
        )
        .reset_index()
    )

# =====================================================

# SDK Features

# =====================================================

def build_sdk_features(
usage_features_df
):

    sdk_df = usage_features_df.copy()

    sdk_df["using_v3_sdk"] = (
        sdk_df["latest_sdk_version"]
        .astype(str)
        .str.startswith("v3")
    )

    sdk_df["using_v4_0_sdk"] = (
        sdk_df["latest_sdk_version"]
        .astype(str)
        .str.startswith("v4.0")
    )

    return sdk_df[
        [
            "account_id",
            "using_v3_sdk",
            "using_v4_0_sdk",
        ]
    ]

# =====================================================

# Master Table

# =====================================================

def build_master_feature_table(
accounts_df,
usage_df,
ticket_df,
csm_features_df,
nps_features_df,
):

    usage_features = (
        build_usage_features(
            usage_df
        )
    )

    ticket_features = (
        build_ticket_features(
            ticket_df
        )
    )

    sdk_features = (
        build_sdk_features(
            usage_features
        )
    )

    # ---------------------------------------------
    # CSM Features
    # ---------------------------------------------

    csm_cols = [
        "account_id",
        "competitor_mentioned",
        "budget_pressure",
        "executive_involved",
        "security_concern",
        "migration_concern",
        "product_dissatisfaction",
        "support_frustration",
        "silent_churn",
        "expansion_opportunity",
        "renewal_sentiment",
        "risk_level",
        "notes",
    ]

    csm_features = (
        csm_features_df[
            [
                c
                for c in csm_cols
                if c in csm_features_df.columns
            ]
        ]
        .copy()
        .rename(
            columns={
                "notes":
                    "latest_csm_note",

                "risk_level":
                    "csm_risk_level",
            }
        )
    )

    # ---------------------------------------------
    # NPS Features
    # ---------------------------------------------

    nps_cols = [
        "account_id",
        "score",
        "verbatim_comment",
        "comment_sentiment_score",
        "competitor_mentioned",
        "budget_pressure",
        "product_dissatisfaction",
        "support_frustration",
        "migration_concern",
        "renewal_risk",
        "nps_comment_mismatch",
    ]

    nps_features = (
        nps_features_df[
            [
                c
                for c in nps_cols
                if c in nps_features_df.columns
            ]
        ]
        .copy()
        .rename(
            columns={
                "score":
                    "latest_nps",

                "verbatim_comment":
                    "latest_nps_comment",

                "competitor_mentioned":
                    "nps_competitor_mentioned",

                "budget_pressure":
                    "nps_budget_pressure",

                "product_dissatisfaction":
                    "nps_product_dissatisfaction",

                "support_frustration":
                    "nps_support_frustration",

                "migration_concern":
                    "nps_migration_concern",

                "renewal_risk":
                    "nps_renewal_risk",
            }
        )
    )

    # ---------------------------------------------
    # Merge Everything
    # ---------------------------------------------

    master_df = (
        accounts_df
        .merge(
            usage_features,
            on="account_id",
            how="left"
        )
        .merge(
            ticket_features,
            on="account_id",
            how="left"
        )
        .merge(
            sdk_features,
            on="account_id",
            how="left"
        )
        .merge(
            csm_features,
            on="account_id",
            how="left"
        )
        .merge(
            nps_features,
            on="account_id",
            how="left"
        )
    )

    # ---------------------------------------------
    # Combined Signals
    # ---------------------------------------------

    master_df["any_competitor_signal"] = (
        master_df[
            "competitor_mentioned"
        ].fillna(False)
        |
        master_df[
            "nps_competitor_mentioned"
        ].fillna(False)
    )

    master_df["any_budget_pressure"] = (
        master_df[
            "budget_pressure"
        ].fillna(False)
        |
        master_df[
            "nps_budget_pressure"
        ].fillna(False)
    )

    master_df["any_migration_concern"] = (
        master_df[
            "migration_concern"
        ].fillna(False)
        |
        master_df[
            "nps_migration_concern"
        ].fillna(False)
    )

    master_df[
        "any_product_dissatisfaction"
    ] = (
        master_df[
            "product_dissatisfaction"
        ].fillna(False)
        |
        master_df[
            "nps_product_dissatisfaction"
        ].fillna(False)
    )

    return master_df