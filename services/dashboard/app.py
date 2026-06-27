# =============================================================
# OpsIntel Copilot — Streamlit Dashboard
# Main entry point
# =============================================================

import streamlit as st

st.set_page_config(
    page_title="OpsIntel Copilot",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.title("🔍 OpsIntel Copilot")
st.sidebar.markdown("AI-powered data reliability & security investigation platform")
st.sidebar.markdown("---")

st.title("Welcome to OpsIntel Copilot")
st.markdown("""
### AWS-Native AI Investigation Platform

Use the sidebar to navigate between modules:

| Page | Description |
|------|-------------|
| 📊 Overview | System health and pipeline status |
| 🔬 Data Reliability | Quality results and schema drift |
| 🛡️ Security Intelligence | Alerts and suspicious activity |
| 📅 Incident Timeline | Chronological event view |
| 🔗 Correlation Engine | Cross-domain incident correlations |
| 🤖 Investigation Copilot | Ask AI questions about incidents |
""")

st.sidebar.markdown("---")
st.sidebar.markdown("**Stack:** AWS · Databricks · dbt · Bedrock RAG")
st.sidebar.markdown("**GitHub:** [opsintel-copilot](https://github.com/Angad0025/opsintel-copilot)")