import streamlit as st
import requests

API_BASE = "http://localhost:8000"


def render_copilot_chat():
    """Renders the RAG copilot chat interface."""

    st.markdown("### 🤖 Ask the Investigation Copilot")
    st.markdown("Ask any question about incidents, pipeline failures, or security events.")

    # Example questions
    with st.expander("💡 Example questions"):
        st.markdown("""
- Why did the orders pipeline fail?
- Was the warehouse export job failure security related?
- What happened with privilege escalation events?
- Which users were involved in suspicious activity?
- What does the pipeline failure playbook recommend?
        """)

    # Chat input
    question = st.text_input(
        "Your question:",
        placeholder="Why did the orders pipeline fail?",
        key="copilot_question"
    )

    if st.button("🔍 Ask Copilot", type="primary"):
        if not question:
            st.warning("Please enter a question.")
            return

        with st.spinner("Searching knowledge base and generating answer..."):
            try:
                response = requests.post(
                    f"{API_BASE}/copilot/ask",
                    json={"question": question},
                    timeout=30
                )
                data = response.json()

                st.markdown("### 📋 Answer")
                st.markdown(data.get("answer", "No answer returned."))

                sources = data.get("sources", [])
                if sources:
                    st.markdown("### 📁 Sources")
                    for source in sources:
                        st.markdown(f"- `{source}`")

                response_time = data.get("response_time_ms", 0)
                st.caption(f"Response time: {response_time}ms")

            except Exception as e:
                st.error(f"Error calling copilot: {e}")