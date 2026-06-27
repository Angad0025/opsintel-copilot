# =============================================================
# OpsIntel Copilot — Page 3: Security Intelligence
# =============================================================

import streamlit as st
import requests
import pandas as pd

API_BASE = "http://44.221.58.68:8000"

st.set_page_config(page_title="Security Intelligence — OpsIntel", page_icon="🛡️", layout="wide")
st.title("🛡️ Security Intelligence")
st.markdown("Security alerts detected by the OpsIntel security detection engine.")
st.markdown("---")

try:
    data = requests.get(f"{API_BASE}/security-alerts?limit=1000", timeout=10).json()
    alerts = data.get("alerts", [])

    if not alerts:
        st.info("No security alerts found.")
        st.stop()

    df = pd.DataFrame(alerts)

    # Summary metrics
    st.markdown("### 📊 Alert Summary")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Alerts", len(df))
    col2.metric("🔴 Brute Force",        int(df["is_brute_force"].sum()))
    col3.metric("🟠 Escalations",         int(df["is_escalation"].sum()))
    col4.metric("🟡 Impossible Travel",   int(df["is_impossible_travel"].sum()))
    col5.metric("📤 Large Exports",       int(df["is_large_export"].sum()))

    st.markdown("---")

    # Alert type breakdown
    st.markdown("### 📈 Alert Types")
    if "event_type" in df.columns:
        type_counts = df["event_type"].value_counts().reset_index()
        type_counts.columns = ["Event Type", "Count"]
        st.bar_chart(type_counts.set_index("Event Type"))

    st.markdown("---")

    # Region breakdown
    st.markdown("### 🌍 Alerts by Region")
    if "region" in df.columns:
        region_counts = df["region"].value_counts().reset_index()
        region_counts.columns = ["Region", "Count"]
        st.bar_chart(region_counts.set_index("Region"))

    st.markdown("---")

    # Filter
    st.markdown("### 🔍 Filter Alerts")
    event_types = ["all"] + sorted(df["event_type"].unique().tolist())
    selected_type = st.selectbox("Filter by event type:", event_types)

    if selected_type != "all":
        filtered = df[df["event_type"] == selected_type]
    else:
        filtered = df

    # Format for display
    display_cols = ["event_id", "event_type", "user_email", "region", "event_time", "source_ip"]
    display_cols = [c for c in display_cols if c in filtered.columns]

    if "event_time" in filtered.columns:
        filtered = filtered.copy()
        filtered["event_time"] = pd.to_datetime(filtered["event_time"]).dt.strftime("%Y-%m-%d %H:%M")

    st.dataframe(filtered[display_cols], use_container_width=True)
    st.caption(f"Showing {len(filtered)} alerts")

except Exception as e:
    st.error(f"Error loading security alerts: {e}")