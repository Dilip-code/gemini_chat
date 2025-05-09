from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Load Falcon model and tokenizer
model_name = "tiiuae/falcon-rw-1b"  # or falcon-rw-1b for smaller
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="auto")

@app.get("/", response_class=HTMLResponse)
async def get_chat(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "chat_history": []})

@app.post("/", response_class=HTMLResponse)
async def post_chat(request: Request, user_input: str = Form(...)):
    inputs = tokenizer(user_input, return_tensors="pt").to(model.device)
    output = model.generate(**inputs, max_new_tokens=200, do_sample=True, temperature=0.7)
    response = tokenizer.decode(output[0], skip_special_tokens=True)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "chat_history": [{"user": user_input, "bot": response}]
    })
