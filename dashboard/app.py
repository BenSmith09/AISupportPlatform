
import sys
from pathlib import Path

import streamlit as st

# Allow Streamlit to import files from src/
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from agent_tools import (
    get_dashboard_metrics,
    get_ticket_counts_by_product,
    get_ticket_breakdown,
    get_ticket_monthly_trends
)

from support_agent import ask_agent

st.set_page_config(
    page_title="AI Support Intelligence",
    page_icon="📊",
    layout="wide"
)


with st.sidebar:
    st.title("🛡️ Support Intelligence")

    st.caption("AI-powered security support analytics")

    st.divider()

    st.markdown("### Dashboard Sections")
    st.markdown("📊 **Overview**")

    st.divider()

    st.markdown("### Technology Stack")
    st.markdown(
        """
        - **Python** — Data processing
        - **Snowflake** — Data warehouse
        - **Claude** — AI analysis
        - **Streamlit** — Dashboard
        """
    )

    st.divider()

    st.caption("Portfolio demonstration project")



st.title("🛡️ AI Support Intelligence")

st.markdown(
    "Monitor support activity, investigate recurring issues "
    "and explore ticket data using Claude AI."
)

st.caption(
    "Security Support Analytics | Snowflake + Claude + Python"
)


st.divider()


if st.button("🔄 Refresh Dashboard"):
    st.cache_data.clear()
    st.rerun()

# Cache results for 5 minutes to reduce Snowflake queries
@st.cache_data(ttl=300)
def load_metrics():
    return get_dashboard_metrics()


@st.cache_data(ttl=300)
def load_product_counts():
    return get_ticket_counts_by_product()


# Load metrics
try:
    metrics = load_metrics()
    products = load_product_counts()

except Exception as error:
    st.error(f"Unable to load Snowflake data: {error}")
    st.stop()


# Display metrics
col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Tickets",
    metrics["total_tickets"]
)

col2.metric(
    "Open Tickets",
    metrics["open_tickets"]
)

col3.metric(
    "AI Classified",
    metrics["ai_classified"]
)

st.divider()

# Product chart
st.subheader("Support Tickets by Product")

import pandas as pd

df = pd.DataFrame(products)

if not df.empty:
    st.bar_chart(
        df,
        x="product",
        y="ticket_count"
    )
else:
    st.info("No support ticket data available.")



st.divider()
st.subheader("Explore Support Tickets")


@st.cache_data(ttl=300)
def load_ticket_breakdown():
    return get_ticket_breakdown()


try:
    breakdown = pd.DataFrame(load_ticket_breakdown())

except Exception:
    st.error("Unable to load ticket breakdown.")
    st.stop()


if not breakdown.empty:

    # Filter options
    product_options = sorted(
        breakdown["product"].dropna().unique().tolist()
    )

    priority_options = sorted(
        breakdown["priority"].dropna().unique().tolist()
    )

    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:
        selected_product = st.selectbox(
            "Filter by product",
            ["All Products"] + product_options
        )

    with filter_col2:
        selected_priority = st.selectbox(
            "Filter by priority",
            ["All Priorities"] + priority_options
        )

    filtered = breakdown.copy()

    if selected_product != "All Products":
        filtered = filtered[
            filtered["product"] == selected_product
        ]

    if selected_priority != "All Priorities":
        filtered = filtered[
            filtered["priority"] == selected_priority
        ]

    # Summary metrics
    total_filtered = int(
        filtered["ticket_count"].sum()
    )

    unresolved = int(
        filtered.loc[
            ~filtered["status"].fillna("").str.upper().isin(
                ["CLOSED", "RESOLVED"]
            ),
            "ticket_count"
        ].sum()
    )

    metric1, metric2 = st.columns(2)

    metric1.metric(
        "Filtered Tickets",
        total_filtered
    )

    metric2.metric(
        "Unresolved Tickets",
        unresolved
    )

    # Grouped chart data
    status_counts = (
        filtered.groupby("status", dropna=False)[
            "ticket_count"
        ]
        .sum()
        .reset_index()
    )

    priority_counts = (
        filtered.groupby("priority", dropna=False)[
            "ticket_count"
        ]
        .sum()
        .reset_index()
    )

    chart1, chart2 = st.columns(2)

    with chart1:
        st.markdown("**Tickets by Status**")

        st.bar_chart(
            status_counts,
            x="status",
            y="ticket_count"
        )

    with chart2:
        st.markdown("**Tickets by Priority**")

        st.bar_chart(
            priority_counts,
            x="priority",
            y="ticket_count"
        )

    
    st.divider()

    st.markdown("**Export Filtered Data**")

    csv_data = filtered.to_csv(index=False)

    st.download_button(
        label="Download CSV Report",
        data=csv_data,
        file_name="support_ticket_report.csv",
        mime="text/csv",
        icon=":material/download:"
    )


else:
    st.info("No ticket breakdown data available.")


st.divider()
st.subheader("Monthly Ticket Trends")


@st.cache_data(ttl=300)
def load_monthly_trends():
    return get_ticket_monthly_trends()


try:
    trends = pd.DataFrame(load_monthly_trends())

except Exception:
    st.error("Unable to load monthly ticket trends.")
    trends = pd.DataFrame()


if not trends.empty:
    trends["month"] = pd.to_datetime(trends["month"])

    min_date = trends["month"].min().date()
    max_date = trends["month"].max().date()

    selected_dates = st.date_input(
        "Select date range (by month)",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if len(selected_dates) == 2:
        start_date, end_date = selected_dates

        if start_date > end_date:
            st.warning("Start date must be before end date.")
        else:
            filtered_trends = trends[
                (trends["month"].dt.date >= start_date)
                & (trends["month"].dt.date <= end_date)
            ].copy()

            # Apply the existing product and priority filters
            if selected_product != "All Products":
                filtered_trends = filtered_trends[
                    filtered_trends["product"] == selected_product
                ]

            if selected_priority != "All Priorities":
                filtered_trends = filtered_trends[
                    filtered_trends["priority"] == selected_priority
                ]

            monthly_counts = (
                filtered_trends.groupby("month")["ticket_count"]
                .sum()
                .reset_index()
            )

            if not monthly_counts.empty:
                st.line_chart(
                    monthly_counts,
                    x="month",
                    y="ticket_count",
                )
            else:
                st.info("No tickets match the selected date range.")
    else:
        st.info("Select both a start and end date.")

else:
    st.info("No monthly trend data available.")



st.divider()

st.subheader("Ask the AI Support Analyst")

if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()

st.caption(
    "Ask questions about your support ticket data. "
    "Claude uses read-only Snowflake reporting tools."
)

# Store chat messages during Streamlit reruns
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept a new question
question = st.chat_input(
    "Ask about support tickets..."
)

if question:
    # Display and save the user's question
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    # Ask Claude and display its response
    with st.chat_message("assistant"):
        with st.spinner("Analysing Snowflake data..."):
            try:
                answer = ask_agent(question)

            except Exception:
                answer = (
                    "Sorry, I couldn't complete that request. "
                    "Please try again."
                )

        st.markdown(answer)

    # Save the answer in chat history
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })


st.divider()

st.caption(
    "AI Support Intelligence Platform | "
    "Built with Python, Snowflake, Claude AI and Streamlit"
)

st.caption(
    "Demo project using fictional support ticket data. "
    "AI-generated recommendations should be reviewed "
    "before being used for real technical support."
)
