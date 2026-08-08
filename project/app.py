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
    message: str

@app.post("/chat")
def chat(request: ChatRequest):

    result = graph.invoke(
        {
            "messages": [
                HumanMessage(content=request.message)
            ]
        }
    )

    return {
        "responses": result["messages"][-1].text
    }

