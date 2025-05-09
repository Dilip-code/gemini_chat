from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os
import anthropic

# Load environment variables
load_dotenv()
CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def get_chat(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "chat_history": []})

@app.post("/", response_class=HTMLResponse)
async def post_chat(request: Request, user_input: str = Form(...)):
    # Send message to Claude model
    response = client.messages.create(
        model="claude-3-haiku-20240307",  # or use `claude-3-sonnet-20240229` or `opus`
        max_tokens=1024,
        messages=[
            {"role": "user", "content": user_input}
        ]
    )

    bot_reply = response.content[0].text  # extract plain text from structured response

    return templates.TemplateResponse("index.html", {
        "request": request,
        "chat_history": [{"user": user_input, "bot": bot_reply}]
    })
