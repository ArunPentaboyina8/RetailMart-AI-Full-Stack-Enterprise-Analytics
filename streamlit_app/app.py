# =============================================================================
# RetailMart AI Analytics - Streamlit Demo App
# =============================================================================
"""
Quick standalone demo for the AI analytics agent.
Shows: Chat interface → Generated SQL → Raw results → AI interpretation.

Run: streamlit run streamlit_app/app.py
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import streamlit as st
import json
import time

st.set_page_config(
    page_title="RetailMart AI Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# Sidebar
# =============================================================================

with st.sidebar:
    st.title("🛒 RetailMart AI")
    st.caption("Enterprise Analytics Platform")
    st.divider()

    st.subheader("📊 KPI Catalog")
    st.markdown("""
    **Ask me about:**
    - 💰 **Sales**: Revenue, trends, growth, payments
    - 👥 **Customers**: CLV, RFM, churn, demographics
    - 📦 **Products**: Top sellers, ABC analysis, inventory
    - 🏪 **Stores**: Performance, profitability, regions
    - 🚚 **Operations**: Delivery SLA, couriers, returns
    - 📢 **Marketing**: Campaign ROI, channels
    - 🚨 **Alerts**: Stock, churn, anomalies
    """)

    st.divider()

    st.subheader("⚙️ Settings")
    show_sql = st.checkbox("Show generated SQL", value=True)
    show_data = st.checkbox("Show raw data", value=False)
    show_debug = st.checkbox("Show debug info", value=False)

    st.divider()

    # Example questions
    st.subheader("💡 Try these questions")
    examples = [
        "What was our total revenue last month?",
        "Who are our top 5 customers?",
        "Which categories have the highest return rates?",
        "How is our delivery SLA trending?",
        "Which store is most profitable?",
        "How many platinum customers are at risk of churning?",
        "Which marketing campaigns have the best ROI?",
        "What products should we reorder urgently?",
    ]
    for ex in examples:
        if st.button(f"📌 {ex}", key=f"ex_{ex[:20]}", use_container_width=True):
            st.session_state["prefill_question"] = ex

# =============================================================================
# Main Content
# =============================================================================

st.title("🛒 RetailMart AI Analytics Assistant")
st.markdown("Ask any question about your retail data in plain English.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message.get("sql") and show_sql:
            with st.expander("📝 Generated SQL"):
                st.code(message["sql"], language="sql")

        if message.get("data") and show_data:
            with st.expander(f"📊 Raw Data ({len(message['data'])} rows)"):
                st.json(message["data"][:10])

        if message.get("debug") and show_debug:
            with st.expander("🔧 Debug Info"):
                st.json(message["debug"])

# Handle prefilled questions from sidebar
prefill = st.session_state.pop("prefill_question", None)

# Chat input
prompt = st.chat_input("Ask about your data...") or prefill

if prompt:
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Analyzing your question..."):
            try:
                # Import and run the agent
                from ai.agent import ask_analytics
                import asyncio

                start_time = time.time()
                result = asyncio.run(ask_analytics(
                    question=prompt,
                    include_sql=True,
                    include_data=True,
                ))
                elapsed = time.time() - start_time

                # Display answer
                st.markdown(result["answer"])

                # Show SQL
                if result.get("sql_query") and show_sql:
                    with st.expander("📝 Generated SQL"):
                        st.code(result["sql_query"], language="sql")

                # Show data
                if result.get("data") and show_data:
                    with st.expander(f"📊 Raw Data ({len(result['data'])} rows)"):
                        st.dataframe(result["data"][:20])

                # Debug info
                debug_info = {
                    "model": result.get("model_used"),
                    "tokens": result.get("tokens_used"),
                    "latency_ms": result.get("latency_ms"),
                    "confidence": result.get("confidence"),
                    "sources": result.get("sources"),
                    "cached": result.get("cached"),
                }

                if show_debug:
                    with st.expander("🔧 Debug Info"):
                        st.json(debug_info)

                # Metrics bar
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Confidence", f"{result.get('confidence', 0):.0%}")
                col2.metric("Tokens", result.get("tokens_used", 0))
                col3.metric("Latency", f"{result.get('latency_ms', 0)}ms")
                col4.metric("Model", result.get("model_used", "N/A"))

                # Save to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "sql": result.get("sql_query"),
                    "data": result.get("data"),
                    "debug": debug_info,
                })

            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.info(
                    "Make sure your `.env` file is configured with a valid Gemini API key "
                    "and PostgreSQL is running with the RetailMart database."
                )
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                })

# Footer
st.divider()
st.caption(
    "RetailMart AI Analytics Platform | "
    "Built with Streamlit, LangChain, LangGraph, ChromaDB, PostgreSQL | "
    "AccioJob SQL Bootcamp"
)
