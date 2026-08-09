from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from agent import graph

load_dotenv()

app = FastAPI()

@app.get("/")
def root():
    return {
        "status": "ok"
    }

class ChatRequest(BaseModel):
    name: str
    phone: str
    iban: str

@app.post("/chat")
def chat(request: ChatRequest):

    result = graph.invoke(
         {
            "messages": [],
            "customer_name": request.name,
            "customer_phone": request.phone,
            "customer_iban": request.iban,
            "authenticated": False,
        }
    )

    return {
        "authenticated": result["authenticated"]
    }

