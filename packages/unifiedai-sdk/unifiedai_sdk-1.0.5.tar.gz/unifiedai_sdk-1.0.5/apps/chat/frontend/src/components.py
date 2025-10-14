import streamlit as st
import json
import pandas as pd


def display_response_block(provider_name: str, response: dict):
    """
    Displays a chat response and expandable metrics panel.
    """
    st.subheader(provider_name)
    st.markdown(f"**Model:** {response['model']}")
    st.write(response["choices"][0]["message"]["content"])

    with st.expander("ℹ️ View Metrics"):
        st.json(response["metrics"])

def display_comparison_chart(cerebras_metrics: dict, bedrock_metrics: dict):
    """
    Renders a simple bar chart comparing latency and TTFB
    between Cerebras and Bedrock mock responses.
    """
    # Convert to DataFrame for Streamlit's chart function
    data = {
        "Provider": ["Cerebras", "Bedrock"],
        "Latency (ms)": [cerebras_metrics["latency_ms"], bedrock_metrics["latency_ms"]],
        "TTFB (ms)": [cerebras_metrics["ttfb_ms"], bedrock_metrics["ttfb_ms"]],
    }

    df = pd.DataFrame(data)
    st.subheader("📊 Performance Comparison")
    st.bar_chart(df.set_index("Provider"))