from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import requests
import os
import json
from serpapi import GoogleSearch

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

chat_history = []

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + os.getenv("GEMINI_API_KEY")

def search_google(query):
    params = {
        "engine": "google",
        "q": query,
        "api_key": os.getenv("SERPAPI_KEY")
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    snippets = []

    for result in results.get("organic_results", [])[:3]:
        title = result.get("title", "")
        link = result.get("link", "")
        snippet = result.get("snippet", "")
        snippets.append(f"🔗 {title}\n{snippet}\n{link}\n")

    return "\n".join(snippets) if snippets else "No results found."

@app.get("/", response_class=HTMLResponse)
async def get_chat(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "chat_history": chat_history
    })

@app.post("/", response_class=HTMLResponse)
async def post_chat(request: Request, user_input: str = Form(...)):
    global chat_history
    headers = {"Content-Type": "application/json"}

    # Detect if live info is needed
    if any(kw in user_input.lower() for kw in ["latest", "today", "news", "current"]):
        search_results = search_google(user_input)
        prompt = f"Here are some live search results:\n{search_results}\n\nGive a helpful summary."
    else:
        prompt = user_input

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    response = requests.post(GEMINI_URL, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        try:
            data = response.json()
            bot_reply = data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            bot_reply = f"Error parsing Gemini reply: {e}"
    else:
        bot_reply = f"API Error: {response.status_code} - {response.text}"

    chat_history.append({"user": user_input, "bot": bot_reply})

    return templates.TemplateResponse("index.html", {
        "request": request,
        "chat_history": chat_history
    })
