# =============================================================
# OpsIntel Copilot — Page 6: Investigation Copilot
# =============================================================

import streamlit as st
import requests

API_BASE = "http://44.221.58.68:8000"

st.set_page_config(page_title="Investigation Copilot — OpsIntel", page_icon="🤖", layout="wide")
st.title("🤖 Investigation Copilot")
st.markdown("Ask natural language questions about incidents, pipeline failures, and security events.")
st.markdown("Powered by **Amazon Bedrock** + **RAG** over your actual incident data.")
st.markdown("---")

# Example questions
with st.expander("💡 Example questions to try"):
    st.markdown("""
- Why did the orders pipeline fail?
- Was the warehouse export job failure security related?
- What happened with privilege escalation events?
- Which users were involved in suspicious activity?
- What does the pipeline failure playbook recommend?
- Were there any lateral movement correlations?
    """)

st.markdown("---")

# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about your incidents..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get copilot response
    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base..."):
            try:
                response = requests.post(
                    f"{API_BASE}/copilot/ask",
                    json={"question": prompt},
                    timeout=30
                )
                data = response.json()
                answer = data.get("answer", "No answer returned.")
                sources = data.get("sources", [])
                response_time = data.get("response_time_ms", 0)

                st.markdown(answer)

                if sources:
                    st.markdown("**Sources:**")
                    for source in sources:
                        filename = source.split("/")[-1]
                        st.markdown(f"- 📄 `{filename}`")

                st.caption(f"⏱️ Response time: {response_time}ms")

                # Save to chat history
                full_response = answer
                if sources:
                    full_response += f"\n\n*Sources: {', '.join([s.split('/')[-1] for s in sources])}*"
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                error_msg = f"Error calling copilot: {e}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

st.markdown("---")

# Copilot history from RDS
with st.expander("📜 Previous Questions (from RDS)"):
    try:
        history_data = requests.get(f"{API_BASE}/copilot/history", timeout=10).json()
        history = history_data.get("history", [])
        if history:
            for item in history:
                st.markdown(f"**Q:** {item.get('question', '')}")
                st.markdown(f"**A:** {item.get('answer', '')[:200]}...")
                st.divider()
        else:
            st.info("No previous questions found.")
    except Exception as e:
        st.error(f"Error loading history: {e}")