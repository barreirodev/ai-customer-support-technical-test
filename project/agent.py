from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import  AIMessage
from project.bouncer import bouncer, route_after_bouncer
from project.greeter import ask_secret_question, greeter, route_after_greeter, router_after_secret_answer_guardrail, secret_answer_guardrail_node, verify_secret_answer
from project.guardrail import guardrail_message
from project.specialist import ask_request, ask_request_guardrail, route_after_request_guardrail, specialist
from project.state import State

def non_client_response(state: State):
    return{
        "messages": [
            AIMessage(
                content=(
                    "Thank you for reaching out. It seems that you are not " \
                    "a currently client of our services. Unfortunately, we cannot provide support." \
                )
            )
        ]
    }

def blocked_response(state: State):
    return{
        "messages": [
            guardrail_message()
        ]
    }

builder = StateGraph(State)

builder.add_node("greeter", greeter)
builder.add_node("ask_secret_question", ask_secret_question)
builder.add_node("secret_answer_guardrail", secret_answer_guardrail_node)
builder.add_node("verify_secret_answer", verify_secret_answer)

builder.add_node("bouncer", bouncer)

builder.add_node("ask_request", ask_request)
builder.add_node("ask_request_guardrail", ask_request_guardrail)

builder.add_node("specialist", specialist)

builder.add_node("blocked_response", blocked_response)
builder.add_node("non_client_response", non_client_response)

builder.add_edge(START, "greeter")
builder.add_conditional_edges(
    "greeter", 
    route_after_greeter,
    {
        "bouncer": "bouncer",
        "secret_question": "ask_secret_question"
    }
)
builder.add_edge("ask_secret_question","secret_answer_guardrail")
builder.add_conditional_edges(
    "secret_answer_guardrail",
    router_after_secret_answer_guardrail,
    {
        "verify": "verify_secret_answer",
        "blocked": "blocked_response"
    }
)
builder.add_edge("verify_secret_answer","bouncer")

builder.add_conditional_edges(
    "bouncer",
    route_after_bouncer,
    {
        "ask_request": "ask_request",
        "non_client": "non_client_response",
    }
)
builder.add_edge("ask_request","ask_request_guardrail")
builder.add_conditional_edges(
    "ask_request_guardrail",
    route_after_request_guardrail,
    {
        "specialist": "specialist",
        "blocked_response": "blocked_response"
    }
)

builder.add_edge("specialist", END)
builder.add_edge("blocked_response", END)
builder.add_edge("non_client_response", END)

def create_graph(checkpointer = None):
    if checkpointer is None:
        return builder.compile()

    return builder.compile(checkpointer=checkpointer)

graph = create_graph()