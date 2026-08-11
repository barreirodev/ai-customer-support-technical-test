
from typing import Annotated, TypedDict

from langgraph.graph import add_messages


class State(TypedDict):
    #Accumulate messages in the state
    messages: Annotated[list, add_messages]
    #Data provided by the customer
    provided_name: str
    provided_phone: str
    provided_iban: str

    #verified customer data
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

    guardrail_reason: str
    input_allowed: bool

