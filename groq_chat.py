from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os
import requests

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama3-70b-8192"

@app.get("/", response_class=HTMLResponse)
async def get_chat(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "chat_history": []})

@app.post("/", response_class=HTMLResponse)
async def post_chat(request: Request, user_input: str = Form(...)):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        bot_reply = response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as err:
        bot_reply = f"Error from Groq API: {err}\nDetails: {response.text}"

    return templates.TemplateResponse("index.html", {
        "request": request,
        "chat_history": [{"user": user_input, "bot": bot_reply}]
    })
