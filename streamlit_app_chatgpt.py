import os
import streamlit as st
import requests
from openai import OpenAI
from dotenv import load_dotenv
import json

# --- Load environment variables ---
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY_FB")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
USER_ID = os.getenv("FITBIT_USER_ID")

st.set_page_config(page_title="Fitbit ChatGPT Chatbot", page_icon="🏃", layout="centered")
st.title("Fitbit ChatGPT Chatbot")

if not OPENAI_API_KEY:
    st.error("No OpenAI API key found in environment variable 'OPENAI_API_KEY_FB'!")
    st.stop()
if not USER_ID:
    st.error("No Fitbit User ID found in environment variable 'FITBIT_USER_ID'!")
    st.stop()

st.caption(f"Chatting as Fitbit User ID: `{USER_ID}`")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# --- Strong system prompt: always summarize tool output ---
if not st.session_state["messages"] or st.session_state["messages"][0].get("role") != "system":
    st.session_state["messages"].insert(0, {
        "role": "system",
        "content": (
            "You are a helpful assistant. "
            "You can answer questions about fitness and Fitbit data. "
            "When a tool is used, ALWAYS summarize the tool result in clear English for the user. "
            "Never output raw data unless explicitly asked."
        )
    })

functions = [
    {
        "type": "function",
        "function": {
            "name": "fetch_fitbit_metrics",
            "description": "Fetch Fitbit metrics for a date range and metrics. Only call if the data is not already in the chat context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "metrics": {
                        "type": "array",
                        "description": "List of metric names (e.g. steps, sleepScore, restingHeartRate, calories, distance, minutesAsleep)",
                        "items": { "type": "string" }
                    },
                    "start_date": { "type": "string", "description": "YYYY-MM-DD" },
                    "end_date": { "type": "string", "description": "YYYY-MM-DD" }
                },
                "required": ["metrics", "start_date", "end_date"]
            }
        }
    }
]

def safe_json_content(obj):
    if obj is None:
        return ""
    try:
        return json.dumps(obj, indent=2)
    except Exception:
        return str(obj)

def fetch_fitbit_metrics(user_id, metrics, start_date, end_date):
    params = {
        "user_id": user_id,
        "metrics": ",".join(metrics),
        "start_date": start_date,
        "end_date": end_date
    }
    try:
        r = requests.get(f"{BACKEND_URL}/fitbit/activity-range", params=params)
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 429:
            return {"error": "Fitbit rate limit reached."}
        else:
            return {"error": f"Backend error: {r.status_code} - {r.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

# --- Main Chat Logic: "tool call loop" ---
prompt = st.chat_input("e.g. 'Show me steps for 2022-01-01'")
if prompt:
    st.session_state["messages"].append({"role": "user", "content": prompt})
    client = OpenAI(api_key=OPENAI_API_KEY)
    with st.spinner("Thinking..."):
        # Copy of messages so we can add nudges and function results as needed without polluting the chat log
        messages = st.session_state["messages"].copy()
        reply = None
        tool_loop_count = 0
        MAX_TOOL_CALLS = 5  # Prevent accidental infinite loops

        while tool_loop_count < MAX_TOOL_CALLS:
            tool_loop_count += 1
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=functions,
                tool_choice="auto"
            )
            msg = response.choices[0].message

            if hasattr(msg, "tool_calls") and msg.tool_calls:
                tool_call = msg.tool_calls[0]
                tool_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                function_response_content = None

                if tool_name == "fetch_fitbit_metrics":
                    fitbit_data = fetch_fitbit_metrics(
                        USER_ID,
                        args["metrics"],
                        args["start_date"],
                        args["end_date"]
                    )
                    function_response_content = safe_json_content(fitbit_data)
                    messages.append({
                        "role": "function",
                        "name": "fetch_fitbit_metrics",
                        "content": function_response_content
                    })
                    if "error" in fitbit_data:
                        reply = fitbit_data["error"]
                        break

                # Continue the loop: there might be more tool calls or a summary to come
                continue

            # If we get here, there are no more tool calls
            reply = msg.content
            # If reply is blank, add a system nudge and continue once more
            if not reply or reply.strip() == "":
                messages.append({
                    "role": "system",
                    "content": "Summarize the previous tool results in clear English for the user."
                })
                continue
            break

        # Only append non-blank, non-system replies to the actual chat log
        if reply and reply.strip():
            st.session_state["messages"].append({"role": "assistant", "content": reply})

# --- Display Chat History (user and assistant messages only) ---
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    elif msg["role"] == "assistant":
        st.chat_message("assistant").write(msg["content"])
    # To show function/tool results as JSON in chat, uncomment below:
    # elif msg["role"] == "function":
    #     st.chat_message("function").write(msg["content"])
