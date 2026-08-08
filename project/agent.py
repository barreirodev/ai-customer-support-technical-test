from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END, add_messages
from typing import TypedDict, Annotated
from langchain_core.messages import  SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

class State(TypedDict):
    #Accumulate messages in the state
    messages: Annotated[list, add_messages]

llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite"
)

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

builder.add_node("chatbot", chatbot)

builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

graph = builder.compile()