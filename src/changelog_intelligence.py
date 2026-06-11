import pandas as pd


# =====================================================
# Product Risk Scoring
# =====================================================

def calculate_product_risk(row):

    score = 0

    # -----------------------------------------
    # Deprecated SDK
    # -----------------------------------------

    if row.get("using_v3_sdk", False):

        score += 20

    # -----------------------------------------
    # Deprecated SDK + migration pain
    # -----------------------------------------

    if (
        row.get("using_v3_sdk", False)
        and row.get("any_migration_concern", False)
    ):

        score += 15

    # -----------------------------------------
    # Security concerns
    # -----------------------------------------

    if row.get("security_concern", False):

        score += 10

    # -----------------------------------------
    # Product dissatisfaction
    # -----------------------------------------

    if row.get(
        "any_product_dissatisfaction",
        False
    ):

        score += 10

    return score


# =====================================================
# Upgrade Recommendation
# =====================================================

def build_recommendation(row):

    recommendations = []

    # -----------------------------------------
    # SDK Migration
    # -----------------------------------------

    if row.get("using_v3_sdk", False):

        recommendations.append(
            "Prioritize SDK v4 migration"
        )

    # -----------------------------------------
    # Security Review
    # -----------------------------------------

    if row.get(
        "security_concern",
        False
    ):

        recommendations.append(
            "Review security roadmap"
        )

    # -----------------------------------------
    # Product Dissatisfaction
    # -----------------------------------------

    if row.get(
        "any_product_dissatisfaction",
        False
    ):

        recommendations.append(
            "Schedule product feedback session"
        )

    # -----------------------------------------
    # Competitor Mention
    # -----------------------------------------

    if row.get(
        "any_competitor_signal",
        False
    ):

        recommendations.append(
            "Run competitive positioning review"
        )

    # -----------------------------------------
    # Migration Concern
    # -----------------------------------------

    if row.get(
        "any_migration_concern",
        False
    ):

        recommendations.append(
            "Assign migration specialist"
        )

    return recommendations


# =====================================================
# Changelog Intelligence
# =====================================================

def build_changelog_features(master_df):

    df = master_df.copy()

    # -----------------------------------------
    # Product Risk Score
    # -----------------------------------------

    df["product_risk_score"] = (
        df.apply(
            calculate_product_risk,
            axis=1
        )
    )

    # -----------------------------------------
    # Product Recommendations
    # -----------------------------------------

    df["product_recommendations"] = (
        df.apply(
            build_recommendation,
            axis=1
        )
    )

    return df