import pandas as pd


LLM_RULES = [
("any_competitor_signal", 25, "Competitor evaluation"),
("any_budget_pressure", 15, "Budget pressure"),
("executive_involved", 10, "Executive escalation"),
("security_concern", 10, "Security/compliance concerns"),
("any_migration_concern", 15, "Migration risk"),
("any_product_dissatisfaction", 15, "Product dissatisfaction"),
("support_frustration", 10, "Support frustration"),
("silent_churn", 20, "Silent churn pattern"),
]


def calculate_risk_score(row):

    score = 0

    reasons = []

    # =================================================
    # Usage Signals
    # =================================================

    api_change = row.get( "api_change_pct", 0 )

    if api_change <= -50:

        score += 20

        reasons.append( "API usage declined >50%" )

    elif api_change <= -25:

        score += 10

        reasons.append( "API usage declined >25%" )

    # ---------------------------------------------

    active_users_change = row.get( "active_users_change_pct", 0 )

    if active_users_change <= -50:

        score += 15

        reasons.append( "Active users declined >50%" )

    elif active_users_change <= -25:

        score += 8

        reasons.append( "Active users declined >25%" )

    # ---------------------------------------------

    workflow_change = row.get( "workflow_change_pct", 0 )

    if workflow_change <= -50:

        score += 10

        reasons.append( "Workflow activity collapsed" )

    # =================================================
    # Support Signals
    # =================================================

    p1_count = row.get( "p1_ticket_count", 0 )

    if p1_count >= 3:

        score += 20

        reasons.append( "Multiple P1 incidents" )

    elif p1_count >= 1:

        score += 10

        reasons.append( "Recent P1 incidents" )

    # ---------------------------------------------

    if row.get( "open_ticket_count", 0 ) >= 3:

        score += 10

        reasons.append( "Several unresolved tickets" )

    # ---------------------------------------------

    if row.get( "avg_resolution_hours", 0 ) > 72:

        score += 5

        reasons.append( "Slow support resolution" )

    # =================================================
    # NPS Signals
    # =================================================

    latest_nps = row.get( "latest_nps", 10 )

    if latest_nps <= 4:

        score += 20

        reasons.append( "Very low NPS" )

    elif latest_nps <= 6:

        score += 12

        reasons.append( "Detractor NPS" )

    # ---------------------------------------------

    if row.get( "nps_comment_mismatch", False ):

        score += 10

        reasons.append( "NPS/comment mismatch" )

    # =================================================
    # LLM Signals
    # =================================================

    for ( column, points, reason ) in LLM_RULES:

        if row.get( column, False ):

            score += points

            reasons.append( reason )

    # =================================================
    # Product Risk
    # =================================================

    product_risk = row.get( "product_risk_score", 0 )

    score += product_risk

    if product_risk > 0:

        reasons.append( f"Product risk score: {product_risk}" )

    # =================================================
    # Positive Signals
    # =================================================

    if row.get( "expansion_opportunity", False ):

        score -= 20

        reasons.append( "Expansion opportunity" )

    if latest_nps >= 9:

        score -= 10

        reasons.append( "Promoter NPS" )

    # =================================================
    # Floor
    # =================================================

    score = max( score, 0 )

    return ( score, reasons )


def assign_risk_tier(score):

    if score >= 60:

        return "HIGH"

    if score >= 30:

        return "MEDIUM"

    return "LOW"


def score_accounts(master_df):

    df = master_df.copy()

    scores = []

    tiers = []

    reasons = []

    for _, row in df.iterrows():

        score, reason_list = ( calculate_risk_score( row ) )

        scores.append(score)

        tiers.append( assign_risk_tier( score ) )

        reasons.append( "; ".join( reason_list ) )

    df["risk_score"] = scores

    df["risk_tier"] = tiers

    df["risk_reasons"] = reasons

    return df


def get_upcoming_renewals( scored_df, renewal_column="renewal_date", days=90 ):

    today = pd.Timestamp.today()

    df = scored_df.copy()

    df[renewal_column] = pd.to_datetime( df[renewal_column], errors="coerce" )

    return df[ ( df[renewal_column] - today ) .dt.days .between( 0, days ) ]


def rank_accounts(df):

    return ( df.sort_values( [ "risk_score", "arr" ], ascending=[ False, False ] ) .reset_index( drop=True ) )



def build_risk_report( master_df, renewal_column="renewal_date" ):

    scored_df = ( score_accounts( master_df ) )

    renewals_df = ( get_upcoming_renewals( scored_df, renewal_column ) )

    return rank_accounts( renewals_df )

