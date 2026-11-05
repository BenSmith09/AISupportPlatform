
import os

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    raise ValueError("ANTHROPIC_API_KEY is missing from .env")

client = Anthropic(api_key=api_key)

ticket = (
    "Dahua NVR showing cameras offline "
    "after changing the network switch."
)

print("Sending support ticket to Claude...", flush=True)

response = client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=250,
    messages=[
        {
            "role": "user",
            "content": (
                "You are a technical support assistant "
                "for a security equipment wholesaler. "
                "Analyse this fictional support ticket. "
                "Identify the likely issue and suggest "
                "two troubleshooting steps. "
                "Keep your answer concise.\n\n"
                f"Ticket: {ticket}"
            )
        }
    ]
)

for block in response.content:
    if block.type == "text":
        print("\nClaude's analysis:\n")
        print(block.text)
