
from project.state import State


ACCOUNTS = [
    {
        "iban": "ES123456789",
        "premium": True,
    },
    {
        "iban": "ES1122334455",
        "premium": False,
    },
]
    
def bouncer(state: State):
    if not state["authenticated"]:
        return {
            "customer_type": "non_client"
        }
    customer_iban = state["customer_iban"]
    for account in ACCOUNTS:
        if account["iban"] == customer_iban:
            if account["premium"]:
                return {
                    "customer_type": "premium"
                }
            else:
                return {
                    "customer_type": "regular"
                }
    return {
        "customer_type": "non_client"
    }

def route_after_bouncer(state: State):
    if state["customer_type"] in ("premium","regular"):
        return "ask_request"

    return "non_client"