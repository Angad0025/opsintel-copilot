# =============================================================
# OpsIntel Copilot — Page 4: Incident Timeline
# =============================================================

import streamlit as st
import requests
import pandas as pd

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="Incident Timeline — OpsIntel", page_icon="📅", layout="wide")
st.title("📅 Incident Timeline")
st.markdown("Chronological view of security events and correlations ordered by time.")
st.markdown("---")

try:
    data = requests.get(f"{API_BASE}/timeline?limit=100", timeout=10).json()

    # Handle both "events" and "timeline" keys
    events = data.get("timeline", data.get("events", []))

    if not events:
        st.info("No timeline events found.")
        st.stop()

    df = pd.DataFrame(events)

    st.markdown(f"### 📋 {len(events)} Events Found")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Events", len(events))
    if "event_type" in df.columns:
        col2.metric("Unique Event Types", df["event_type"].nunique())
    if "severity" in df.columns:
        high = len(df[df["severity"] == "high"])
        col3.metric("High Severity", high)

    st.markdown("---")
    st.markdown("### 🕐 Event Timeline")

    for _, event in df.iterrows():
        event_type = event.get("event_type", "unknown")
        description = event.get("description", "")
        severity = event.get("severity", "medium")
        time = str(event.get("event_time", ""))[:16]
        source = event.get("source", "")

        if severity == "high":
            icon = "🔴"
        elif event_type == "correlation":
            icon = "🔗"
        else:
            icon = "🟡"

        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown(f"**{time}**")
        with col2:
            st.markdown(f"{icon} `{event_type}` — {description}")
            st.caption(f"Source: {source} | Severity: {severity}")
        st.divider()

except Exception as e:
    st.error(f"Error loading timeline: {e}")