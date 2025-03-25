import requests
import streamlit as st
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# API Configuration
BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "daaa6830-a230-4c5d-89bb-fa0c261dbdc0"
FLOW_ID = "48c2495a-bc13-4ac4-869b-ea99c998b6f7"
APPLICATION_TOKEN = os.getenv("APPLICATION_TOKEN")

if not APPLICATION_TOKEN:
    st.error("⚠️ Error: Missing API Token. Check your .env file.")

ENDPOINT = FLOW_ID

def run_flow(message: str, history: list) -> str:
    """
    Sends a request to the chatbot API and returns the response message.
    Maintains conversation history.
    """
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{ENDPOINT}"
    headers = {
        "Authorization": f"Bearer {APPLICATION_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "input_value": message,
        "history": history,  # Send conversation history
        "output_type": "chat",
        "input_type": "chat",
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=120)

        # Debugging Logs
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text[:500]}")  # Show first 500 chars

        # Handle API Errors
        if response.status_code == 401:
            return "⚠️ Error: Unauthorized request. Check your API token."
        elif response.status_code == 504:
            return "⚠️ Error: API timeout. Please try again later."
        elif response.status_code != 200:
            return f"⚠️ Error: API request failed with status {response.status_code}"

        # Ensure Response is JSON
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            return "⚠️ Error: Received an invalid JSON response from the API."

        # Extract and Return Message
        return data.get("outputs", [{}])[0].get("outputs", [{}])[0].get("results", {}).get("message", {}).get("text", "⚠️ Error: Unexpected API response format.")

    except requests.exceptions.RequestException as e:
        return f"⚠️ Error: Request failed - {str(e)}"

def main():
    st.title("YOTTA GRC Chatbot")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Chat Interface
    st.write("What can I help with?")
    
    # Display chat history
    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(chat["user"])
        with st.chat_message("assistant"):
            st.write(chat["bot"])

    # User Input
    message = st.chat_input("Type your message here...")

    if message:
        with st.spinner("Generating AI response..."):
            bot_reply = run_flow(message, st.session_state.chat_history)

        # Append new conversation to history
        st.session_state.chat_history.append({"user": message, "bot": bot_reply})

        # Display new messages
        with st.chat_message("user"):
            st.write(message)
        with st.chat_message("assistant"):
            st.write(bot_reply)

    # Clear Chat Button
    if st.button("🗑️Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

if __name__ == "__main__":
    main()
