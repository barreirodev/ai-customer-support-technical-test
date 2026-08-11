from project.agent import greeter


def test_greeter_authenticates_customer_with_three_matches():
    state = {
        "provided_name": "Luis Gomez",
        "provided_phone": "1122334455",
        "provided_iban": "ES123456789",
    }

    result = greeter(state)

    assert result["matches"] == 3
    assert result["authenticated"] is True
    assert result["customer_name"] == "Luis Gomez"

def test_greeter_requires_secret_question_with_two_matches():
    state = {
        "provided_name": "Luis Gomez",
        "provided_phone": "1122334455",
        "provided_iban": "wrong-iban",
    }

    result = greeter(state)

    assert result["matches"] == 2
    assert result["authenticated"] is False
    assert result["waiting_for_secret_answer"] is True