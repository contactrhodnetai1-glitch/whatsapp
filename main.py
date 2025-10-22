from fastapi import FastAPI, Form
from twilio.rest import Client
import openai
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Twilio setup
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")
twilio_client = Client(TWILIO_SID, TWILIO_AUTH)

# OpenAI setup
OPENAI_KEY = os.getenv("OPENAI_KEY")
openai.api_key = OPENAI_KEY

@app.get("/")
def home():
    return {"status": "WhatsApp Bot Running ✅"}

@app.post("/webhook")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...)
):
    try:
        print(f"Incoming message from {From}: {Body}")

        # OpenAI >=1.0.0 syntax
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful WhatsApp assistant."},
                {"role": "user", "content": Body}
            ],
            temperature=0.7,
            max_tokens=150
        )

        ai_reply = response.choices[0].message.content.strip()
        print("AI Reply:", ai_reply)

        # Send reply via Twilio
        message = twilio_client.messages.create(
            from_=TWILIO_NUMBER,
            to=f"whatsapp:{From}",
            body=ai_reply
        )
        print("Twilio message SID:", message.sid)

        return {"status": "sent"}

    except Exception as e:
        print("Webhook error:", e)
        return {"status": "error", "detail": str(e)}
