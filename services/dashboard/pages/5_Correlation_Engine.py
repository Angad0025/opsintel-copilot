# =============================================================
# OpsIntel Copilot — Page 5: Correlation Engine
# =============================================================

import streamlit as st
import requests
import pandas as pd

API_BASE = "http://44.221.58.68:8000"

st.set_page_config(page_title="Correlation Engine — OpsIntel", page_icon="🔗", layout="wide")
st.title("🔗 Correlation Engine")
st.markdown("Cross-domain correlations linking pipeline failures to security events.")
st.markdown("---")

try:
    data = requests.get(f"{API_BASE}/correlations?limit=1000", timeout=10).json()
    correlations = data.get("correlations", [])

    if not correlations:
        st.info("No correlations found.")
        st.stop()

    df = pd.DataFrame(correlations)

    # Summary metrics
    st.markdown("### 📊 Correlation Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Correlations", len(df))

    if "confidence_score" in df.columns:
        col2.metric("Avg Confidence", f"{df['confidence_score'].mean():.2f}")
        col3.metric("High Confidence (≥0.9)", int((df["confidence_score"] >= 0.9).sum()))

    if "correlation_type" in df.columns:
        lateral = int((df["correlation_type"] == "lateral_movement").sum())
        col4.metric("Lateral Movement", lateral)

    st.markdown("---")

    # Correlation type breakdown
    if "correlation_type" in df.columns:
        st.markdown("### 📈 Correlation Types")
        type_counts = df["correlation_type"].value_counts().reset_index()
        type_counts.columns = ["Type", "Count"]
        st.bar_chart(type_counts.set_index("Type"))

    st.markdown("---")

    # Filter
    st.markdown("### 🔍 Filter Correlations")
    col1, col2 = st.columns(2)

    with col1:
        corr_types = ["all"] + sorted(df["correlation_type"].unique().tolist())
        selected_type = st.selectbox("Correlation type:", corr_types)

    with col2:
        min_confidence = st.slider("Minimum confidence score:", 0.0, 1.0, 0.8, 0.1)

    filtered = df.copy()
    if selected_type != "all":
        filtered = filtered[filtered["correlation_type"] == selected_type]
    filtered = filtered[filtered["confidence_score"] >= min_confidence]

    st.markdown(f"**{len(filtered)} correlations match your filters**")

    # Display columns
    display_cols = [
        "correlation_id", "correlation_type", "pipeline_name",
        "error_message", "security_event_type", "involved_user",
        "time_diff_minutes", "confidence_score", "recommendation"
    ]
    display_cols = [c for c in display_cols if c in filtered.columns]

    st.dataframe(filtered[display_cols], use_container_width=True)

    st.markdown("---")

    # Show a sample recommendation
    if len(filtered) > 0:
        st.markdown("### 💡 Sample Recommendation")
        sample = filtered.iloc[0]
        st.info(sample.get("recommendation", "No recommendation available."))

except Exception as e:
    st.error(f"Error loading correlations: {e}")