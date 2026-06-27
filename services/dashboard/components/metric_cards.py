import streamlit as st


def render_metric_row(metrics: list):
    """
    Renders a row of metric cards.
    metrics = [{"label": "Total Alerts", "value": 55, "delta": None}, ...]
    """
    cols = st.columns(len(metrics))
    for i, metric in enumerate(metrics):
        with cols[i]:
            st.metric(
                label=metric["label"],
                value=metric["value"],
                delta=metric.get("delta")
            )


def render_status_badge(status: str) -> str:
    """Returns a colored emoji badge for a status string."""
    status_map = {
        "healthy":  "🟢 Healthy",
        "warning":  "🟡 Warning",
        "critical": "🔴 Critical",
        "unknown":  "⚪ Unknown",
        "active":   "🟢 Active",
        "resolved": "✅ Resolved",
    }
    return status_map.get(status.lower(), f"⚪ {status}")