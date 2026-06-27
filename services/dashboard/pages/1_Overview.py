# =============================================================
# OpsIntel Copilot — Page 1: Overview
# =============================================================

import streamlit as st
import requests
import pandas as pd

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="Overview — OpsIntel", page_icon="📊", layout="wide")
st.title("📊 System Overview")
st.markdown("Live system health and pipeline status from RDS PostgreSQL.")
st.markdown("---")

# Health check
try:
    health = requests.get(f"{API_BASE}/health", timeout=5).json()
    status = health.get("status", "unknown")
    if status == "healthy":
        st.success("✅ API is healthy and connected to RDS")
    else:
        st.error("❌ API health check failed")
except Exception as e:
    st.error(f"❌ Cannot reach FastAPI: {e}")
    st.stop()

st.markdown("---")

# Load data
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🔔 Security Alerts")
    try:
        alerts_data = requests.get(f"{API_BASE}/security-alerts?limit=1000", timeout=10).json()
        alerts = alerts_data.get("alerts", [])
        total_alerts = alerts_data.get("count", 0)

        brute_force = sum(1 for a in alerts if a.get("is_brute_force"))
        escalation  = sum(1 for a in alerts if a.get("is_escalation"))
        impossible  = sum(1 for a in alerts if a.get("is_impossible_travel"))
        large_exp   = sum(1 for a in alerts if a.get("is_large_export"))
        token_rot   = sum(1 for a in alerts if a.get("is_token_rotation"))

        st.metric("Total Alerts", total_alerts)
        c1, c2, c3 = st.columns(3)
        c1.metric("Brute Force", brute_force)
        c2.metric("Escalations", escalation)
        c3.metric("Impossible Travel", impossible)
        c1.metric("Large Exports", large_exp)
        c2.metric("Token Rotations", token_rot)

    except Exception as e:
        st.error(f"Error loading alerts: {e}")

with col2:
    st.markdown("### 🔗 Correlations")
    try:
        corr_data = requests.get(f"{API_BASE}/correlations?limit=1000", timeout=10).json()
        correlations = corr_data.get("correlations", [])
        total_corr = corr_data.get("count", 0)

        high_conf = sum(1 for c in correlations if c.get("confidence_score", 0) >= 0.9)
        sec_to_pipe = sum(1 for c in correlations if c.get("correlation_type") == "security_to_pipeline")
        lateral = sum(1 for c in correlations if c.get("correlation_type") == "lateral_movement")

        st.metric("Total Correlations", total_corr)
        c1, c2, c3 = st.columns(3)
        c1.metric("High Confidence", high_conf)
        c2.metric("Security→Pipeline", sec_to_pipe)
        c3.metric("Lateral Movement", lateral)

    except Exception as e:
        st.error(f"Error loading correlations: {e}")

st.markdown("---")
st.markdown("### 📅 Recent Incidents")

try:
    inc_data = requests.get(f"{API_BASE}/incidents?limit=10", timeout=10).json()
    incidents = inc_data.get("incidents", [])

    if incidents:
        df = pd.DataFrame(incidents)
        if "incident_hour" in df.columns:
            df["incident_hour"] = pd.to_datetime(df["incident_hour"]).dt.strftime("%Y-%m-%d %H:%M")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No incidents found.")
except Exception as e:
    st.error(f"Error loading incidents: {e}")