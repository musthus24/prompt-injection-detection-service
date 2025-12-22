Prompt Injection Detection Service (MVP)

A small, production-minded FastAPI microservice that scores prompts for prompt-injection risk and returns an advisory decision for LLM applications.

This is a detection signal, not a full prevention system.

------------------------------------------------------------

WHAT IT DOES

Given an input prompt, the service:

1. Vectorizes the prompt using a TF-IDF model
2. Computes a risk score using Logistic Regression (P(injection))
3. Maps the score to a decision band:
   - allow
   - review
   - high_risk
4. Returns a structured JSON response

------------------------------------------------------------

NON-GOALS

This service intentionally does not:

- Block prompts automatically (it is advisory by design)
- Guarantee detection of all jailbreaks or obfuscated attacks
- Store raw prompts by default

------------------------------------------------------------

THREAT MODEL (SUMMARY)

This service assumes an adversary may:

- Attempt instruction override and role-based prompt injection
- Obfuscate text to evade simple detectors
- Probe the system to learn thresholds and behavior

The service mitigates by:

- Returning only a score and decision band (no raw prompt persistence)
- Enforcing strict input validation (length bounds)
- Providing a consistent, testable API contract

Known blind spots:

- Highly novel jailbreak techniques and multi-turn context not present in a single prompt
- Encoded or heavily obfuscated payloads that avoid token-level patterns

------------------------------------------------------------

API

Health Check

Method: GET
Endpoint: /health

Example request:
curl -s http://localhost:8000/health

Example response:
{
  "status": "ok"
}

------------------------------------------------------------

Scan Prompt

Method: POST
Endpoint: /v1/scan

Request body:
{
  "prompt": "Summarize the causes of World War I."
}

Response body:
{
  "decision": "allow",
  "risk_score": 0.12,
  "model_version": "0.1.0"
}

Notes:

- prompt is required and must be between 1 and 8000 characters
- risk_score is a float between 0.0 and 1.0
- decision is one of: allow, review, high_risk
- thresholds are an internal policy choice and can be tuned without changing the API contract
- validation errors return HTTP 422

------------------------------------------------------------

LOCAL DEVELOPMENT

Requirements:

- Python 3
- Dependencies listed in requirements.txt

Setup:

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Run the service:

uvicorn app.main:app --reload

Then open:

Swagger UI: http://localhost:8000/docs

------------------------------------------------------------

TESTS

HTTP-level tests are implemented using pytest.

Run:

pytest -q

------------------------------------------------------------

REPOSITORY STRUCTURE

app/main.py        - FastAPI app entrypoint
app/api/           - API routes
app/services/      - detection logic and orchestration
app/model/         - model-related code
artifacts/         - trained model artifacts (TF-IDF + Logistic Regression)
docs/              - design notes and threat model
tests/             - HTTP-level API tests

------------------------------------------------------------

SECURITY AND PRIVACY DEFAULTS

- Do not log raw prompts
- Do not persist raw prompts by default
- Treat the model output as a signal to be combined with other controls such as authentication, rate limiting, and monitoring

------------------------------------------------------------

STATUS

MVP complete through:

- Design and threat modeling
- API contract and validation
- ML inference integration
- HTTP-level tests

------------------------------------------------------------

NEXT PLANNED HARDENING

- Structured logging and basic metrics
- Authentication
- Rate limiting
- Optional hashed prompt storage for investigation workflows (no raw prompt persistence)
