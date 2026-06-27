import streamlit as st
import pandas as pd


def render_incident_table(incidents: list):
    """Renders a formatted incident summary table."""
    if not incidents:
        st.info("No incidents found.")
        return

    df = pd.DataFrame(incidents)

    # Format columns if they exist
    if "incident_hour" in df.columns:
        df["incident_hour"] = pd.to_datetime(df["incident_hour"]).dt.strftime("%Y-%m-%d %H:%M")
    if "total_events" in df.columns:
        df = df.sort_values("total_events", ascending=False)

    st.dataframe(df, use_container_width=True)


def render_alerts_table(alerts: list):
    """Renders a formatted security alerts table."""
    if not alerts:
        st.info("No alerts found.")
        return

    df = pd.DataFrame(alerts)

    if "event_time" in df.columns:
        df["event_time"] = pd.to_datetime(df["event_time"]).dt.strftime("%Y-%m-%d %H:%M")

    # Highlight alert types
    if "event_type" in df.columns:
        df["event_type"] = df["event_type"].str.replace("_", " ").str.title()

    st.dataframe(df, use_container_width=True)