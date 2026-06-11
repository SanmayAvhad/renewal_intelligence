import pandas as pd
import numpy as np

def sdk_risk_insight(master_df):

    sdk_v3 = master_df[
        master_df["using_v3_sdk"] == 1
    ]

    sdk_v4 = master_df[
        master_df["using_v3_sdk"] == 0
    ]

    if len(sdk_v3) == 0 or len(sdk_v4) == 0:
        return None

    avg_v3 = round(
        sdk_v3["risk_score"].mean(),
        2
    )

    avg_v4 = round(
        sdk_v4["risk_score"].mean(),
        2
    )

    multiplier = round(
        avg_v3 / max(avg_v4, 1),
        2
    )

    return {
        "insight_type": "sdk_risk",
        "title": "SDK Deprecation Risk",
        "description":
            f"Customers on SDK v3 have "
            f"{multiplier}x higher average "
            f"renewal risk than customers "
            f"on newer SDK versions.",
        "metric_1": avg_v3,
        "metric_2": avg_v4
    }

def competitor_insight(master_df):

    comp_df = master_df[
        master_df["competitor_mentioned"] == 1
    ]

    non_comp_df = master_df[
        master_df["competitor_mentioned"] == 0
    ]

    if len(comp_df) == 0:
        return None

    avg_comp = round(
        comp_df["risk_score"].mean(),
        2
    )

    avg_non_comp = round(
        non_comp_df["risk_score"].mean(),
        2
    )

    return {
        "insight_type": "competitor_risk",
        "title": "Competitor Evaluation",
        "description":
            f"Accounts evaluating competitors "
            f"have an average risk score of "
            f"{avg_comp} vs {avg_non_comp}.",
        "metric_1": avg_comp,
        "metric_2": avg_non_comp
    }

def silent_churn_insight(master_df):

    silent_df = master_df[
        (
            master_df["latest_nps"] >= 8
        )
        &
        (
            master_df["api_change_pct"] <= -30
        )
    ]

    return {
        "insight_type": "silent_churn",
        "title": "Silent Churn Accounts",
        "description":
            f"{len(silent_df)} accounts "
            f"show positive NPS but declining "
            f"product usage.",
        "accounts":
            silent_df[
                "account_name"
            ].tolist()
    }

def executive_involvement_insight(
    master_df
):

    exec_df = master_df[
        master_df["executive_involved"] == 1
    ]

    non_exec_df = master_df[
        master_df["executive_involved"] == 0
    ]

    if len(exec_df) == 0:
        return None

    avg_exec = round(
        exec_df["risk_score"].mean(),
        2
    )

    avg_non_exec = round(
        non_exec_df["risk_score"].mean(),
        2
    )

    return {
        "insight_type":
            "executive_escalation",

        "title":
            "Executive Escalation",

        "description":
            f"Accounts involving executives "
            f"(CTO, CIO, VP, CISO) have an "
            f"average risk score of "
            f"{avg_exec} vs "
            f"{avg_non_exec}.",

        "metric_1":
            avg_exec,

        "metric_2":
            avg_non_exec
    }

def budget_pressure_insight(
    master_df
):

    budget_df = master_df[
        master_df["budget_pressure"] == 1
    ]

    if len(budget_df) == 0:
        return None

    avg_risk = round(
        budget_df["risk_score"].mean(),
        2
    )

    return {
        "insight_type":
            "budget_pressure",

        "title":
            "Budget Pressure",

        "description":
            f"{len(budget_df)} accounts "
            f"mentioned budget constraints "
            f"with an average risk score "
            f"of {avg_risk}.",

        "metric_1":
            avg_risk
    }

def risk_theme_summary(
    master_df
):

    themes = [
        "competitor_mentioned",
        "budget_pressure",
        "executive_involved",
        "security_concern",
        "migration_concern",
        "product_dissatisfaction",
        "support_frustration",
        "silent_churn",
    ]

    rows = []

    for theme in themes:

        count = (
            master_df[theme]
            .fillna(0)
            .sum()
        )

        rows.append(
            {
                "theme": theme,
                "count": int(count)
            }
        )

    return (
        pd.DataFrame(rows)
        .sort_values(
            "count",
            ascending=False
        )
    )

def generate_insights(
    master_df
):

    insights = []

    generators = [

        sdk_risk_insight,

        competitor_insight,

        silent_churn_insight,

        executive_involvement_insight,

        budget_pressure_insight,
    ]

    for fn in generators:

        result = fn(master_df)

        if result:

            insights.append(result)

    return pd.DataFrame(insights)

def save_insights(
    insights_df,
    output_path="output/insights.csv"
):

    insights_df.to_csv(
        output_path,
        index=False
    )

