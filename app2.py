import chainlit as cl
import requests
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('application_token')

BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "96d01e9c-33d4-408c-8e38-a5e192e32cbe"
FLOW_ID = "e190b233-3a53-4dad-b242-17571d90031f"
APPLICATION_TOKEN = os.getenv('APPLICATION_TOKEN')
ENDPOINT = FLOW_ID  # Default to FLOW_ID

def run_flow(message: str) -> str:
    """
    Sends a message to the chatbot API and extracts the text response.
    """
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{ENDPOINT}"
    payload = {
        "input_value": message,
        "output_type": "chat",
        "input_type": "chat"
    }
    headers = {"Authorization": f"Bearer {APPLICATION_TOKEN}", "Content-Type": "application/json"}

    response = requests.post(api_url, json=payload, headers=headers)
    data = response.json()

    try:
        # Extracting response text from nested JSON
        return data["outputs"][0]["outputs"][0]["results"]["message"]["text"]
    except (KeyError, IndexError):
        return "Error: Unable to extract chatbot response."

@cl.on_message
async def main(message: cl.Message):
    """
    Handles user messages and returns the chatbot's response.
    """
    bot_reply = run_flow(message.content)
    await cl.Message(content=bot_reply).send()
