from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END, add_messages
from typing import TypedDict, Annotated
from langchain_core.messages import  SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.types import interrupt
from langgraph.checkpoint.memory import InMemorySaver

CUSTOMERS = [
{
    "name": "Luis Gomez",
    "phone": "1122334455",
    "iban": "ES123456789",
    "secret_question":"Childhood pet's name?",
    "secret_answer":"Sammy",
    "customer_type": "premium"
},
{
    "name": "Sara Lopez",
    "phone": "123456789",
    "iban": "ES1122334455",
    "secret_question":"Favourite color?",
    "secret_answer":"Blue",
    "customer_type": "regular"
}
]
    
load_dotenv()

class State(TypedDict):
    #Accumulate messages in the state
    messages: Annotated[list, add_messages]
    customer_name: str
    customer_phone: str
    customer_iban: str
    customer_type: str

    matches: int

    secret_question: str
    secret_answer: str
    provided_secret_answer: str

    authenticated: bool
    waiting_for_secret_answer: bool

llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite"
)

def greeter(state: State):
    customer_name = state["customer_name"]
    customer_phone = state["customer_phone"]
    customer_iban = state["customer_iban"]

    for customer in CUSTOMERS:
        matches = 0
        if customer["name"] == customer_name:
            matches += 1
        if customer["phone"] == customer_phone:
            matches += 1
        if customer["iban"] == customer_iban:
            matches += 1

        if matches >= 2:
            return {
                "matches": matches,
                "secret_question": customer["secret_question"],
                "secret_answer": customer["secret_answer"],
                "customer_type": customer["customer_type"],
                "authenticated": matches == 3,
                "waiting_for_secret_answer": matches == 2
            }

    return {
        "matches": 0,
        "authenticated": False,
        "waiting_for_secret_answer": False
    }

def route_after_greeter(state: State):
     if state["matches"] == 3:
        return "authenticated"

     if state["matches"] == 2:
        return "secret_question"

     return "rejected"

def ask_secret_question(state: State):
    answer = interrupt({
        "question": state["secret_question"]
    })
    provided_answer = answer.strip().lower()
    correct_answer = state["secret_answer"].strip().lower()

    return {
        "authenticated": provided_answer == correct_answer,
        "provided_secret_answer": provided_answer,
        "waiting_for_secret_answer": False
    }

def chatbot(state: State):
    response = llm.invoke(
        [
            SystemMessage(
                content="You are a helpful customer support assistant."
            )
        ]
        + state["messages"]
    )

    return {
        "messages": [response]
    }


builder = StateGraph(State)

builder.add_node("greeter", greeter)
builder.add_node("ask_secret_question", ask_secret_question)

builder.add_edge(START, "greeter")
builder.add_conditional_edges(
    "greeter", 
    route_after_greeter,
    {
        "authenticated": END,
        "secret_question": "ask_secret_question",
        "rejected": END,
    }
)
builder.add_edge("ask_secret_question", END)

checkpoint_saver = InMemorySaver() #Save and restore states betweern requests. Only for demonstration purposes, in production you would use a persistent saver.
graph = builder.compile(checkpointer=checkpoint_saver)