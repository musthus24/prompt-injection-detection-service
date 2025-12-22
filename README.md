# Prompt Injection Detection Service (MVP)

A small, production-minded FastAPI microservice that scores prompts for prompt-injection risk and returns an **advisory decision** for LLM applications.

This is a **detection signal**, not a full prevention system.

---

## What it does

Given an input prompt, the service:

1. Vectorizes the prompt using a TF-IDF model  
2. Computes a risk score using Logistic Regression (`P(injection)`)  
3. Maps the score to a decision band:
   - `allow`
   - `review`
   - `high_risk`
4. Returns a structured JSON response  

---

## Non-goals

This service intentionally does **not**:

- Block prompts automatically (it is advisory by design)
- Guarantee detection of all jailbreaks or obfuscated attacks
- Store raw prompts by default

---

## Threat model (summary)

This service assumes an adversary may:

- Attempt instruction override and role-based prompt injection
- Obfuscate text to evade simple detectors
- Probe the system to learn thresholds and behavior

The service mitigates by:

- Returning only a score and decision band (no raw prompt persistence)
- Enforcing strict input validation (length bounds)
- Providing a consistent, testable API contract

**Known blind spots:**

- Highly novel jailbreak techniques and multi-turn context not present in a single prompt
- Encoded or heavily obfuscated payloads that avoid token-level patterns

---

## API

### Health check

**GET** `/health`

Example:
```bash
curl -s http://localhost:8000/health
```

Response:
```json
{
  "status": "ok"
}
```

---

### Scan prompt

**POST** `/v1/scan`

#### Request
```json
{
  "prompt": "Summarize the causes of World War I."
}
```

#### Response
```json
{
  "decision": "allow",
  "risk_score": 0.12,
  "model_version": "0.1.0"
}
```

#### Notes

- `prompt` is required and must be between **1 and 8000 characters**
- `risk_score` is a float in **[0.0, 1.0]**
- `decision` is one of: `allow`, `review`, `high_risk`
- Thresholds are an internal policy choice and can be tuned without changing the API contract
- Validation errors return **HTTP 422**

---

## Local development

### Requirements

- Python 3
- Dependencies listed in `requirements.txt`

### Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run the service

```bash
uvicorn app.main:app --reload
```

Then open:

- Swagger UI: http://localhost:8000/docs

---

## Tests

HTTP-level tests are implemented using `pytest`.

Run:
```bash
pytest -q
```

---

## Repository structure

- `app/main.py` — FastAPI app entrypoint  
- `app/api/` — API routes  
- `app/services/` — detection logic and orchestration  
- `app/model/` — model-related code  
- `artifacts/` — trained model artifacts (TF-IDF + Logistic Regression)  
- `docs/` — design notes and threat model  
- `tests/` — HTTP-level API tests  

---

## Security and privacy defaults

- Do not log raw prompts
- Do not persist raw prompts by default
- Treat the model output as a **signal** to be combined with other controls (authentication, rate limiting, monitoring)

---

## Status

**MVP complete through:**

- Design and threat modeling
- API contract and validation
- ML inference integration
- HTTP-level tests

---

## Next planned hardening

- Structured logging and basic metrics
- Authentication
- Rate limiting
- Optional hashed prompt storage for investigation workflows (no raw prompt persistence)
