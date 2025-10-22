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
async def whatsapp_webhook(From: str = Form(...), Body: str = Form(...)):
    print(f"Incoming: {From}, {Body}")
    twilio_client.messages.create(
        from_=TWILIO_NUMBER,
        to=f"whatsapp:{From}",
        body="Hello! This is a test reply."
    )
    return {"status": "sent"}