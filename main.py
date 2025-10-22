from fastapi import FastAPI, Form, Request
from twilio.rest import Client
import cohere
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Twilio & Cohere setup
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")
COHERE_KEY = os.getenv("COHERE_KEY")

twilio_client = Client(TWILIO_SID, TWILIO_AUTH)
co = cohere.Client(COHERE_KEY)


@app.get("/")
def home():
    return {"status": "WhatsApp Bot Running ✅"}


@app.post("/webhook")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...)
):
    user_message = Body.strip()
    print(f"Incoming message from {From}: {user_message}")

    # Generate AI reply using Cohere
    response = co.generate(
        model="command-r-plus",
        prompt=f"User: {user_message}\nReply as a polite, helpful assistant.",
        max_tokens=150,
        temperature=0.7
    )
    ai_reply = response.generations[0].text.strip()

    # Send message back to WhatsApp user
    twilio_client.messages.create(
        from_=TWILIO_NUMBER,
        to=From,
        body=ai_reply
    )

    return {"status": "reply sent"}