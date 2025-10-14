import streamlit as st
import time
import requests
import json
from src.mock_data import MOCK_RESPONSE_CEREBRAS, MOCK_RESPONSE_BEDROCK
from src.components import display_response_block, display_comparison_chart

# Configuration
BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Cerebras ↔ Bedrock Inference UI",
    layout="wide",
)

st.title("🧠 Cerebras ↔ Bedrock Inference Comparison")

st.markdown(
    """
    <style>
    .small-font {
        font-size:14px !important;
        color: #666666;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<p class="small-font">Proof of Concept: Unified SDK for Cerebras + AWS Bedrock</p>', unsafe_allow_html=True)

# Backend connection toggle
use_backend = st.sidebar.checkbox("Connect to Backend API", value=False)
if use_backend:
    st.sidebar.info(f"Backend URL: {BACKEND_URL}")
    # Test backend connection
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=2)
        if response.status_code == 200:
            st.sidebar.success("✅ Backend connected")
        else:
            st.sidebar.error("❌ Backend unhealthy")
            use_backend = False
    except requests.exceptions.RequestException:
        st.sidebar.error("❌ Backend not reachable")
        use_backend = False
else:
    st.sidebar.info("Using mock data")

st.divider()
mode = st.selectbox("Select Mode", ["Solo", "Comparison"])

if mode == "Solo":
    provider = st.selectbox("Choose Provider", ["Cerebras", "Bedrock"])
    model = st.selectbox("Choose Model", ["llama3.1-8b", "qwen-1.5b"])
else:
    model = st.selectbox("Choose Model (applies to both providers)", ["llama3.1-8b", "qwen-1.5b"])

st.divider()


def call_backend_api(endpoint: str, payload: dict) -> dict:
    """Call the backend API with error handling"""
    try:
        response = requests.post(f"{BACKEND_URL}/{endpoint}", json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Backend API error: {str(e)}")
        return None


if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

        # Solo response
        if msg.get("provider") and msg.get("response"):
            display_response_block(msg["provider"], msg["response"])

        # Comparison responses
        elif msg.get("mode") == "Comparison" and msg.get("responses"):
            col1, col2 = st.columns(2)
            with col1:
                display_response_block("Cerebras", msg["responses"]["Cerebras"])
            with col2:
                display_response_block("Bedrock", msg["responses"]["Bedrock"])

            st.divider()
            display_comparison_chart(
                msg["responses"]["Cerebras"]["metrics"],
                msg["responses"]["Bedrock"]["metrics"]
            )

if prompt := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        if use_backend:
            with st.spinner("Calling backend API..."):
                if mode == "Solo":
                    # Call solo endpoint
                    payload = {
                        "provider": provider.lower(),
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}]
                    }
                    response = call_backend_api("chat/solo", payload)
                    
                    if response:
                        # Add metrics if not present (backend might not include them)
                        if "metrics" not in response:
                            response["metrics"] = {"latency_ms": 0, "ttfb_ms": 0, "payload_size_kb": 0}
                        
                        display_response_block(provider, response)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"Response from {provider}",
                            "provider": provider,
                            "response": response,
                        })
                else:
                    # Call comparison endpoint
                    payload = {
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}]
                    }
                    response = call_backend_api("chat/compare", payload)
                    
                    if response:
                        # Format response for comparison display
                        # Note: Backend needs to be updated to return comparison format
                        cerebras_resp = response.copy()
                        bedrock_resp = response.copy()
                        
                        # Add mock metrics if not present
                        if "metrics" not in cerebras_resp:
                            cerebras_resp["metrics"] = {"latency_ms": 320, "ttfb_ms": 110, "payload_size_kb": 4}
                        if "metrics" not in bedrock_resp:
                            bedrock_resp["metrics"] = {"latency_ms": 410, "ttfb_ms": 140, "payload_size_kb": 5}
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            display_response_block("Cerebras", cerebras_resp)
                        with col2:
                            display_response_block("Bedrock", bedrock_resp)

                        st.divider()
                        display_comparison_chart(
                            cerebras_resp["metrics"],
                            bedrock_resp["metrics"]
                        )

                        st.session_state.messages.append({
                            "role": "assistant",
                            "mode": "Comparison",
                            "content": "Comparison between Cerebras and Bedrock",
                            "responses": {
                                "Cerebras": cerebras_resp,
                                "Bedrock": bedrock_resp
                            }
                        })
        else:
            # Use mock data (original behavior)
            with st.spinner("Fetching mock responses..."):
                time.sleep(1)  

                if mode == "Solo":
                    response = MOCK_RESPONSE_CEREBRAS if provider == "Cerebras" else MOCK_RESPONSE_BEDROCK
                    display_response_block(provider, response)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Response from {provider}",
                        "provider": provider,
                        "response": response,
                    })

                else:  
                    col1, col2 = st.columns(2)
                    with col1:
                        display_response_block("Cerebras", MOCK_RESPONSE_CEREBRAS)
                    with col2:
                        display_response_block("Bedrock", MOCK_RESPONSE_BEDROCK)

                    st.divider()
                    display_comparison_chart(
                        MOCK_RESPONSE_CEREBRAS["metrics"],
                        MOCK_RESPONSE_BEDROCK["metrics"]
                    )

                    st.session_state.messages.append({
                        "role": "assistant",
                        "mode": "Comparison",
                        "content": "Comparison between Cerebras and Bedrock",
                        "responses": {
                            "Cerebras": MOCK_RESPONSE_CEREBRAS,
                            "Bedrock": MOCK_RESPONSE_BEDROCK
                        }
                    })