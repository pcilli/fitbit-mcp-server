import os
import streamlit as st
import requests
from dotenv import load_dotenv
import json
import google.generativeai as genai

# Load .env variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
USER_ID = os.getenv("FITBIT_USER_ID")

st.set_page_config(page_title="Fitbit Gemini Chatbot", page_icon="🏃", layout="centered")
st.title("Fitbit Gemini Chatbot")

if not GEMINI_API_KEY:
    st.error("No Gemini API key found in environment variable 'GEMINI_API_KEY'!")
    st.stop()
if not USER_ID:
    st.error("No Fitbit User ID found in environment variable 'FITBIT_USER_ID'!")
    st.stop()

st.caption(f"Chatting as Fitbit User ID: `{USER_ID}`")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Prompt-to-metric mapping
KEYWORD_TO_METRIC = {
    "steps": "steps",
    "distance": "distance",
    "calories": "calories",
    "restingheartrate": "restingHeartRate",
    "heartrate": "restingHeartRate",
    "sleep": "minutesAsleep",
    "minutes slept": "minutesAsleep",
    "sleep minutes": "minutesAsleep",
    "minutesslept": "minutesAsleep",
    "sleepscore": "sleepScore",
    "sleep score": "sleepScore",
}

def extract_metrics_from_prompt(prompt):
    prompt_lower = prompt.lower().replace(" ", "")
    found_metrics = set()
    for keyword, metric in KEYWORD_TO_METRIC.items():
        if keyword.replace(" ", "") in prompt_lower:
            found_metrics.add(metric)
    return list(found_metrics)

def fetch_fitbit_metrics(user_id, metrics, start_date, end_date):
    params = {
        "user_id": user_id,
        "metrics": ",".join(metrics),
        "start_date": start_date,
        "end_date": end_date
    }
    try:
        with st.spinner("Fetching Fitbit data..."):
            r = requests.get(f"{BACKEND_URL}/fitbit/activity-range", params=params)
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 429:
            return {"error": "Fitbit rate limit reached."}
        else:
            return {"error": f"Backend error: {r.status_code} - {r.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

def build_gemini_history(messages):
    history = []
    for msg in messages:
        if msg["role"] == "user":
            history.append({"role": "user", "parts": [msg["content"]]})
        elif msg["role"] == "assistant":
            history.append({"role": "model", "parts": [msg["content"]]})
        elif msg["role"] == "function":
            history.append({"role": "user", "parts": [f"Fitbit data: {msg['content']}"]})
    return history

# Main chat interaction
prompt = st.chat_input("e.g. 'Show me steps for 2022-01-01'")
if prompt:
    st.session_state["messages"].append({"role": "user", "content": prompt})

    metrics = extract_metrics_from_prompt(prompt)
    start_date = "2022-01-01" 
    end_date = "2022-01-01"

    if metrics:
        fitbit_data = fetch_fitbit_metrics(USER_ID, metrics, start_date, end_date)
        st.session_state["messages"].append({
            "role": "function",
            "name": "fetch_fitbit_metrics",
            "content": json.dumps(fitbit_data)
        })

    # Build history for Gemini
    history = build_gemini_history(st.session_state["messages"])

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.5-pro")
    with st.spinner("Thinking..."):
        try:
            response = model.generate_content(history)
            reply = response.text
        except Exception as e:
            reply = f"Gemini error: {str(e)}"

    st.session_state["messages"].append({"role": "assistant", "content": reply})

# Display chat history (hide function/tool calls)
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    elif msg["role"] == "assistant":
        st.chat_message("assistant").write(msg["content"])
