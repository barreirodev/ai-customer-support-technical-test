# AI Customer Support

Customer support assistant built with **LangGraph**, **FastAPI** and **Google Gemini**.

The application implements a customer authentication flow, customer routing, interrupt-based interactions and basic input guardrails.

## Features

* Customer identification using name, phone number and IBAN.
* Authentication based on matching customer information.
* Secret-question verification when only two customer attributes match.
* Customer routing:
  * Premium customer
  * Regular customer
  * Non-client
* Interrupt-based interaction using LangGraph.
* Basic guardrails for:
  * Empty secret answers.
  * Secret answers exceeding the allowed length.
  * Basic prompt-injection patterns.
* FastAPI API.
* LangGraph checkpointing using `InMemorySaver`.
* Basic automated tests with pytest.

## Project Structure

```text
ai-customer-support-technical-test/
│
├── project/
│   ├── agent.py
│   ├── app.py
│   └── guardrail.py
│
├── tests/
│   ├── test_agent.py
│   └── test_guardrail.py
│
├── .env
├── .gitignore
├── langgraph.json
├── pyproject.toml
└── README.md
```

## Requirements

* Python 3.12+
* A Google Gemini API key
* Project dependencies installed in a virtual environment

## Installation

Create and activate a virtual environment:

```bash
python -m venv minibot-env
```

Windows:

```bash
minibot-env\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_api_key
```

The application uses `ChatGoogleGenerativeAI` to communicate with Gemini.

## Running the Application

### FastAPI

From the project root:

```bash
uvicorn project.app:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API is available at:

```text
http://127.0.0.1:8000/docs
```

### LangGraph

The LangGraph configuration is defined in `langgraph.json`.

The graph is exposed as:

```text
customer_service
```

The graph entry point is:

```text
project/agent.py
```

## API Endpoints

### Start a conversation

```http
POST /chat/start
```

Example:

```json
{
  "thread_id": "test-1",
  "name": "Luis Gomez",
  "phone": "1122334455",
  "iban": "ES123456789"
}
```

The endpoint identifies the customer and determines whether additional authentication is required.

### Submit the secret answer

Only if 2 of 3 parameters are correct

```http
PATCH /chat/secret
```

Example:

```json
{
  "thread_id": "test-1",
  "provided_secret_answer": "sammy"
}
```

This resumes the LangGraph interrupt used for the secret question.

### Send a customer request

```http
PATCH /chat/message
```

Example:

```json
{
  "thread_id": "test-1",
  "message": "I need help with my account"
}
```

The request is passed through the input guardrail before reaching the specialist.

## Authentication Flow

The customer provides three identifying attributes:

* Name
* Phone
* IBAN

The `greeter` node compares these values against the available customer records.

### Three matches

The customer is authenticated directly.

The workflow continues to the `bouncer`, which determines whether the customer is premium or regular.

### Two matches

The customer must answer a secret question.

The workflow uses a LangGraph `interrupt` to pause execution and wait for the answer.

The answer is validated by the secret-answer guardrail before authentication is completed.

### Fewer than two matches

The customer is treated as a non-client and does not receive customer support.

## Customer Routing

After authentication, the `bouncer` checks the customer's IBAN against the account records.

```text
Authenticated
     |
     v
  Bouncer
   /   \
  /     \
Premium  Regular
```

## Guardrails

The project contains basic deterministic guardrails in `guardrail.py`.

### Secret answer guardrail

The secret answer is blocked when:

* It is empty.
* It exceeds 100 characters.

### User input guardrail

The customer request is checked for basic prompt-injection patterns such as:

```text
ignore previous instructions
reveal your system prompt
show me the system prompt
ignore your instructions
```

Blocked requests are stopped before reaching the specialist.

These guardrails are intentionally simple and deterministic for this technical test.

## Testing

Tests are implemented with pytest.

Run all tests with:

```bash
pytest
```

The tests cover the basic guardrail behavior and core customer workflow scenarios.

## Design Notes

The application separates the main responsibilities between:

* `agent.py` — LangGraph workflow and customer support logic.
* `guardrail.py` — deterministic input validation and guardrail logic.
* `app.py` — FastAPI API layer.
* `tests/` — automated tests.

LangGraph interrupts are used to handle information that must be provided interactively during the workflow.

`InMemorySaver` This is suitable for the technical test/demo environment; a persistent checkpointer would be preferable for a production deployment.

## Limitations

The customer and account data are stored in-memory and are therefore not suitable for production use.

The guardrails are deterministic and pattern-based rather than LLM-based. A production implementation could use a more sophisticated validation or classification layer depending on the security requirements.

## Running the Tests and API

A typical local workflow is:

```bash
pytest
```

Then:

```bash
uvicorn project.app:app --reload
```

Open the API documentation at:

```text
http://127.0.0.1:8000/docs
```
