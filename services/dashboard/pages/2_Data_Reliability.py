# =============================================================
# OpsIntel Copilot — Page 2: Data Reliability
# =============================================================

import streamlit as st
import requests
import pandas as pd

API_BASE = "http://44.221.58.68:8000"

st.set_page_config(page_title="Data Reliability — OpsIntel", page_icon="🔬", layout="wide")
st.title("🔬 Data Reliability")
st.markdown("Data quality results from dbt tests and PySpark reliability checks.")
st.markdown("---")

try:
    dq_data = requests.get(f"{API_BASE}/data-quality?limit=1000", timeout=10).json()
    results = dq_data.get("results", [])
    total = dq_data.get("count", 0)

    if not results:
        st.info("No data quality results found.")
        st.stop()

    df = pd.DataFrame(results)

    st.markdown("### 📊 Quality Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Records Checked", total)

    if "quality_flag" in df.columns:
        ok_count   = len(df[df["quality_flag"] == "ok"])
        susp_count = len(df[df["quality_flag"] == "suspicious_amount"])
        neg_count  = len(df[df["quality_flag"] == "negative_amount"])

        col2.metric("✅ Clean Records", ok_count)
        col3.metric("⚠️ Suspicious Amount", susp_count)
        col4.metric("❌ Negative Amount", neg_count)

        st.markdown("---")

        st.markdown("### 📈 Flag Distribution")
        flag_counts = df["quality_flag"].value_counts().reset_index()
        flag_counts.columns = ["Flag", "Count"]
        st.bar_chart(flag_counts.set_index("Flag"))

        st.markdown("---")

        st.markdown("### 🔍 Filter Records")
        flag_filter = st.selectbox(
            "Filter by quality flag:",
            ["all", "ok", "suspicious_amount", "negative_amount"]
        )

        filtered = df if flag_filter == "all" else df[df["quality_flag"] == flag_filter]

        st.dataframe(filtered.head(100), use_container_width=True)
        st.caption(f"Showing {min(100, len(filtered))} of {len(filtered)} records")

except Exception as e:
    st.error(f"Error loading data quality results: {e}")