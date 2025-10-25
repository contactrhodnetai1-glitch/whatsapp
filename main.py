from fastapi import FastAPI, Request
import requests
import openai
import os

app = FastAPI()

VERIFY_TOKEN = "secure_whatsapp_bot"
ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
openai.api_key = os.getenv("OPENAI_KEY")

@app.get("/webhook")
async def verify(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)
    return {"error": "Verification failed"}

@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()
    print(data)

    try:
        messages = data["entry"][0]["changes"][0]["value"].get("messages", [])
        if not messages:
            return {"status": "no messages"}

        message = messages[0]
        sender = message["from"]
        text = message["text"]["body"]

        print(f"User ({sender}) said: {text}")

        # OpenAI reply
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful WhatsApp assistant."},
                {"role": "user", "content": text}
            ]
        )
        ai_reply = response.choices[0].message.content.strip()

        # Ensure + is added
        if not sender.startswith("+"):
            sender = f"+{sender}"

        # Send reply via WhatsApp Cloud API
        url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": sender,
            "text": {"body": ai_reply}
        }
        r = requests.post(url, headers=headers, json=payload)
        print("Meta API response:", r.status_code, r.text)

    except Exception as e:
        print("Error:", e)

    return {"status": "received"}
