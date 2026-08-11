
from project.guardrail import secret_answer_guardrail
from project.state import State
from langgraph.types import interrupt

CUSTOMERS = [
{
    "name": "Luis Gomez",
    "phone": "1122334455",
    "iban": "ES123456789",
    "secret_question":"Childhood pet's name?",
    "secret_answer":"sammy",
},
{
    "name": "Sara Lopez",
    "phone": "123456789",
    "iban": "ES1122334455",
    "secret_question":"Favourite color?",
    "secret_answer":"blue",
}
]

def greeter(state: State):
    provided_name = state["provided_name"]
    provided_phone = state["provided_phone"]
    provided_iban = state["provided_iban"]

    best_customer = None
    best_matches = 0

    for customer in CUSTOMERS:
        matches = 0
        if customer["name"] == provided_name:
            matches += 1
        if customer["phone"] == provided_phone:
            matches += 1
        if customer["iban"] == provided_iban:
            matches += 1

        if matches > best_matches:
            best_matches = matches
            best_customer = customer
 
    if best_customer is None:
        return {
            "matches": 0,
            "authenticated": False,
            "waiting_for_secret_answer": False
        }

    return {
            "matches": best_matches,
            "customer_name": best_customer["name"],
            "customer_phone": best_customer["phone"],
            "customer_iban": best_customer["iban"],
            "secret_question": best_customer["secret_question"],
            "secret_answer": best_customer["secret_answer"],
            "authenticated": best_matches == 3,
            "waiting_for_secret_answer": best_matches == 2
        }

def route_after_greeter(state: State):
     if state["matches"] == 2:
        return "secret_question"
     
     return "bouncer"

def ask_secret_question(state: State):
    answer = interrupt({
        "question": state["secret_question"]
    })
    return {
            "provided_secret_answer": answer,
            "waiting_for_secret_answer": False
    }

def secret_answer_guardrail_node(state: State):
    return secret_answer_guardrail(state["provided_secret_answer"])

def verify_secret_answer(state: State):
    provided_answer = state["provided_secret_answer"].strip().lower()
    correct_answer = state["secret_answer"].strip().lower()
    return {
        "authenticated": provided_answer == correct_answer
    }

def router_after_secret_answer_guardrail(state: State):
    if state["input_allowed"]:
        return "verify"
    return "blocked"