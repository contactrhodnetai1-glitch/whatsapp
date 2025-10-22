from fastapi import FastAPI, Form, BackgroundTasks
from twilio.rest import Client
import cohere
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")
COHERE_KEY = os.getenv("COHERE_KEY")

twilio_client = Client(TWILIO_SID, TWILIO_AUTH)
co = cohere.Client(COHERE_KEY)

@app.post("/webhook")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...),
    background_tasks: BackgroundTasks = None
):
    try:
        print(f"Incoming message from {From}: {Body}")

        # Background task to avoid timeout
        def send_ai_reply(from_number, message):
            try:
                # Cohere AI
                response = co.generate(
                    model="command-r-plus",
                    prompt=f"User: {message}\nReply as a polite, helpful assistant.",
                    max_tokens=150,
                    temperature=0.7
                )
                ai_reply = response.generations[0].text.strip()
                print("AI Reply:", ai_reply)

                # Twilio send
                twilio_client.messages.create(
                    from_=TWILIO_NUMBER,
                    to=f"whatsapp:{from_number}",
                    body=ai_reply
                )
            except Exception as e:
                print("Error in background task:", e)

        background_tasks.add_task(send_ai_reply, From, Body)

        return {"status": "processing"}

    except Exception as e:
        print("Webhook error:", e)
        return {"status": "error", "detail": str(e)}