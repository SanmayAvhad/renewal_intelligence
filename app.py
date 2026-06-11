import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config( page_title="Renewal Intelligence Engine", layout="wide" )

@st.cache_data
def load_data():

    risk_df = pd.read_csv( "output/risk_report.csv" )

    insights_df = pd.read_csv( "output/insights.csv" )

    try:

        final_df = pd.read_csv( "output/final_risk_report.csv" )

    except Exception:

        final_df = risk_df.copy()

    return ( risk_df, final_df, insights_df )


risk_df, final_df, insights_df = ( load_data() )

st.title( "Renewal Intelligence Engine" )

st.caption( "AI-powered renewal risk analysis" )

high_risk = len( risk_df[ risk_df["risk_tier"] == "HIGH" ] )

medium_risk = len( risk_df[ risk_df["risk_tier"] == "MEDIUM" ] )

low_risk = len( risk_df[ risk_df["risk_tier"] == "LOW" ])

col1, col2, col3, col4 = ( st.columns(4) )

col1.metric( "Accounts", len(risk_df) )

col2.metric( "High Risk", high_risk )

col3.metric( "Medium Risk", medium_risk )

col4.metric( "Low Risk", low_risk )

tab1, tab2, tab3 = st.tabs( [ "Executive Summary", "Accounts", "Insights" ] )


with tab1:


    st.subheader(
        "Risk Distribution"
    )

    fig = px.histogram(
        risk_df,
        x="risk_score"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader(
        "Risk Tier Breakdown"
    )

    tier_counts = (
        risk_df["risk_tier"]
        .value_counts()
        .reset_index()
    )

    tier_counts.columns = [
        "risk_tier",
        "count"
    ]

    pie = px.pie(
        tier_counts,
        names="risk_tier",
        values="count"
    )

    st.plotly_chart(
        pie,
        use_container_width=True
    )

    st.subheader(
        "Top Risk Accounts"
    )

    top_accounts = (
        risk_df
        .sort_values(
            "risk_score",
            ascending=False
        )
        .head(10)
    )

    st.dataframe(
        top_accounts,
        use_container_width=True
    )


# =====================================================

# Accounts

# =====================================================

with tab2:


    st.subheader(
        "Account Explorer"
    )

    if "risk_tier" in risk_df.columns:

        selected_tier = (
            st.selectbox(
                "Filter Risk Tier",
                [
                    "ALL",
                    "HIGH",
                    "MEDIUM",
                    "LOW"
                ]
            )
        )

        filtered_df = (
            risk_df.copy()
        )

        if selected_tier != "ALL":

            filtered_df = (
                filtered_df[
                    filtered_df[
                        "risk_tier"
                    ]
                    == selected_tier
                ]
            )

    else:

        filtered_df = risk_df.copy()

    st.dataframe(
        filtered_df,
        use_container_width=True
    )

    st.divider()

    account_col = None

    for candidate in [
        "account_name",
        "company_name",
        "name"
    ]:

        if candidate in filtered_df.columns:

            account_col = candidate

            break

    if account_col:

        selected_account = (
            st.selectbox(
                "Select Account",
                filtered_df[
                    account_col
                ]
            )
        )

        account = (
            filtered_df[
                filtered_df[
                    account_col
                ]
                == selected_account
            ]
            .iloc[0]
        )

        st.subheader(
            selected_account
        )

        c1, c2, c3 = (
            st.columns(3)
        )

        if "risk_score" in account:

            c1.metric(
                "Risk Score",
                account[
                    "risk_score"
                ]
            )

        if "risk_tier" in account:

            c2.metric(
                "Risk Tier",
                account[
                    "risk_tier"
                ]
            )

        if "latest_nps" in account:

            c3.metric(
                "NPS",
                account[
                    "latest_nps"
                ]
            )

        if (
            "risk_reasons"
            in account
        ):

            st.subheader(
                "Risk Reasons"
            )

            st.write(
                account[
                    "risk_reasons"
                ]
            )

        if (
            "explanation"
            in account
        ):

            st.subheader(
                "AI Explanation"
            )

            st.write(
                account[
                    "explanation"
                ]
            )


# =====================================================

# Insights

# =====================================================

with tab3:


    st.subheader(
        "Executive Insights"
    )

    for _, row in (
        insights_df.iterrows()
    ):

        with st.expander(
            row["title"]
        ):

            st.write(
                row["description"]
            )

            if (
                "summary"
                in row
            ):

                st.write(
                    row["summary"]
                )


# =====================================================

# Downloads

# =====================================================

st.divider()

try:


    with open(
        "output/final_risk_report.csv",
        "rb"
    ) as f:

        st.download_button(
            label=
            "Download Final Report",
            data=f,
            file_name=
            "final_risk_report.csv"
        )


except Exception:


    pass

