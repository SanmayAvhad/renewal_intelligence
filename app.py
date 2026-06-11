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

tab1, tab2, tab3 = st.tabs( [ "Accounts", "Portfolio Analytics", "Insights" ] )

with tab1:

    st.subheader(
        "Accounts Ranked By Renewal Risk"
    )

    working_df = (
        final_df
        .sort_values(
            "risk_score",
            ascending=False
        )
        .reset_index(drop=True)
    )

    selected_tier = st.selectbox(
        "Risk Tier",
        [
            "ALL",
            "HIGH",
            "MEDIUM",
            "LOW"
        ]
    )

    if selected_tier != "ALL":

        working_df = (
            working_df[
                working_df["risk_tier"]
                == selected_tier
            ]
        )

    st.dataframe(
        working_df,
        use_container_width=True,
        height=500
    )

    st.divider()

    account_col = None

    for candidate in [
        "account_name",
        "company_name",
        "name"
    ]:

        if candidate in working_df.columns:

            account_col = candidate
            break

    if account_col:

        selected_account = st.selectbox(
            "Select Account",
            working_df[
                account_col
            ].tolist()
        )

        account = (
            working_df[
                working_df[
                    account_col
                ] == selected_account
            ]
            .iloc[0]
        )

        st.header(
            selected_account
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Risk Score",
            account.get(
                "risk_score",
                "N/A"
            )
        )

        c2.metric(
            "Risk Tier",
            account.get(
                "risk_tier",
                "N/A"
            )
        )

        c3.metric(
            "NPS",
            account.get(
                "latest_nps",
                "N/A"
            )
        )

        c4.metric(
            "ARR",
            account.get(
                "arr",
                "N/A"
            )
        )

        with st.expander(
            "Risk Factors",
            expanded=True
        ):

            st.write(
                account.get(
                    "risk_reasons",
                    "No risk factors available"
                )
            )

        with st.expander(
            "AI Summary",
            expanded=True
        ):

            st.write(
                account.get(
                    "summary",
                    "No summary available"
                )
            )

        with st.expander(
            "Recommended Actions",
            expanded=True
        ):

            actions = account.get(
                "recommended_actions",
                ""
            )

            st.write(actions)

        with st.expander(
            "Raw Signals"
        ):

            cols_to_show = [
                c
                for c in account.index
                if any(
                    keyword in c.lower()
                    for keyword in [
                        "nps",
                        "ticket",
                        "usage",
                        "migration",
                        "budget",
                        "competitor",
                        "security",
                    ]
                )
            ]

            st.json(
                account[
                    cols_to_show
                ].to_dict()
            )

# =====================================================

# Accounts

# =====================================================

with tab2:

    st.subheader(
        "Risk Score Distribution"
    )

    fig = px.histogram(
        risk_df,
        x="risk_score",
        nbins=20
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

    fig = px.bar(
        tier_counts,
        x="risk_tier",
        y="count"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader(
        "Top 10 Risk Accounts"
    )

    st.dataframe(
        risk_df
        .sort_values(
            "risk_score",
            ascending=False
        )
        .head(10),
        use_container_width=True
    )

# =====================================================

# Insights

# =====================================================

with tab3:

    st.subheader(
        "Executive Insights"
    )

    for _, row in insights_df.iterrows():

        with st.expander(
            row["title"]
        ):

            st.markdown(
                f"**Description**\n\n"
                f"{row['description']}"
            )

            if "summary" in row:

                st.markdown(
                    f"**Summary**\n\n"
                    f"{row['summary']}"
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

