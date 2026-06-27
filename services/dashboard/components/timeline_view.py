import streamlit as st
import pandas as pd


def render_timeline(events: list):
    """Renders a chronological timeline of events."""
    if not events:
        st.info("No timeline events found.")
        return

    for event in events:
        event_type = event.get("event_type", "unknown")
        user = event.get("user_email", event.get("involved_user", "unknown"))
        region = event.get("region", "")
        time = event.get("event_time", event.get("security_event_at", ""))

        # Pick icon based on event type
        if "brute" in event_type:
            icon = "🔴"
        elif "escalation" in event_type or "privilege" in event_type:
            icon = "🟠"
        elif "export" in event_type:
            icon = "🟡"
        elif "token" in event_type:
            icon = "🔵"
        elif "config" in event_type:
            icon = "⚙️"
        else:
            icon = "⚪"

        st.markdown(f"{icon} **{time}** — `{event_type}` by **{user}** in `{region}`")
        st.markdown("---")