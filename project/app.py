from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from agent import create_graph
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

app = FastAPI()
checkpoint_saver = InMemorySaver() #Save and restore states betweern requests. Only for demonstration purposes, in production would use a persistent saver. LangSmith doesn't need it
graph = create_graph(checkpointer=checkpoint_saver)


@app.get("/")
def root():
    return {
        "status": "ok"
    }

class CustomerRequest(BaseModel):
    thread_id: str
    name: str
    phone: str
    iban: str

class SecretAnswerRequest(BaseModel):
    thread_id: str
    provided_secret_answer: str

@app.post("/chat/start")
def start_chat(request: CustomerRequest):

    config = {
        "configurable":{
            "thread_id": request.thread_id
        }
    }

    result = graph.invoke(
         {
            "messages": [],
            "customer_name": request.name,
            "customer_phone": request.phone,
            "customer_iban": request.iban,
            "customer_type": "",
            "matches": 0,
            "secret_question": "",
            "secret_answer": "",
            "provided_secret_answer": "",
            "authenticated": False,
            "waiting_for_secret_answer": False,
        },
        
        config = config
    )   

    state = graph.get_state(config)

    response = ""
    if result.get("messages"):
        response = result["messages"][-1].content

    waiting_answer = state.values.get("waiting_for_secret_answer", False)
    return {
        "response": response,
        "authenticated": state.values.get("authenticated", False),
        "waiting_for_secret_answer": waiting_answer,
        "secret_question": state.values.get("secret_question", "") if waiting_answer else ""
    }

@app.patch("/chat/secret")
def secret_answer(request: SecretAnswerRequest):

    config = {
        "configurable":{
            "thread_id": request.thread_id
        }
    }
    result = graph.invoke(
         Command(
             resume = request.provided_secret_answer
         ),
        config = config
    )

    response = ""
    if result.get("messages"):
        response = result["messages"][-1].content

    return {
        "response": response,
        "authenticated": result.get("authenticated", False),
        "customer_type": result.get("customer_type"),
    }