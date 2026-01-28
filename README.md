# Secure LLM Gateway (Prompt Injection Detection + Policy Enforcement)

A production minded FastAPI service that sits in front of an LLM application and enforces a simple, testable security policy over untrusted user input.

This project started as a prompt injection detector. It is now a gateway that turns detection into enforcement decisions, with clear behavior for allow, review, and block outcomes.

## Why this exists

LLM apps break in predictable ways:
- Prompt injection attempts to override system intent
- Abuse attempts to trigger tool use or data exfiltration
- Unsafe inputs should not automatically reach downstream systems

This gateway treats the LLM boundary as a security boundary:
- Scan input
- Map scan output to an explicit policy decision
- Enforce deterministic behavior
- Only allow privileged capabilities (tools) when policy allows it

## Core behavior

For a chat request, the gateway produces:
- `decision`: `ALLOW` | `REQUIRE_HUMAN_REVIEW` | `BLOCK`
- `action_taken`: `PROCEEDED_NORMAL` | `PROCEEDED_NO_CONTEXT` | `RETURNED_REVIEW` | `BLOCKED`

Enforcement rules:
- `BLOCK` returns HTTP 403 with `POLICY_BLOCK`
- `REQUIRE_HUMAN_REVIEW` can either:
  - return no model output (`RETURNED_REVIEW`), strict review path
  - proceed without context (`PROCEEDED_NO_CONTEXT`), if `review_fallback=respond_without_context`
- `ALLOW` proceeds normally

The gateway currently returns a deterministic stub model output (`stubbed_response`) so the enforcement behavior is easy to test and reason about.

## Tool execution boundary (capability gating)

The request can optionally include a `tool_request`:
```json
{
  "tool_request": {
    "name": "web_search",
    "args": { "query": "roblox", "top_k": 2 }
  }
}
```

Security properties:
- Tools are allowlisted via a registry, unknown tools are rejected
- Each tool has a strict Pydantic args schema (`extra="forbid"`), so unexpected keys are rejected
- Tools only execute when `decision=ALLOW` and `action_taken=PROCEEDED_NORMAL`
- For review and block outcomes, tool execution is denied and reported in `tool_result`

Stub tools included:
- `web_search` (stubbed output, no network)
- `pdf_read` (doc_id is a Literal allowlist, no filesystem paths)

## API

Base path prefix: `/v1`

### Health
`GET /health`

### Scan
`POST /v1/scan`

Request:
```json
{ "prompt": "Summarize the causes of World War I." }
```

Response:
```json
{
  "decision": "allow",
  "risk_score": 0.12,
  "model_version": "0.1.0"
}
```

### Chat (policy enforcing)
`POST /v1/chat`

Request:
```json
{
  "messages": [
    { "role": "user", "content": "Hello" }
  ],
  "review_fallback": "none"
}
```

Response shape:
```json
{
  "request_id": "optional",
  "decision": "ALLOW",
  "action_taken": "PROCEEDED_NORMAL",
  "risk_score": 0.01,
  "reasons": ["threshold_mapping"],
  "llm_output": "stubbed_response",
  "model_version": "0.1.0",
  "tool_result": null
}
```

### Chat with a tool request
`POST /v1/chat`

Request:
```json
{
  "messages": [
    { "role": "user", "content": "Search something." }
  ],
  "tool_request": {
    "name": "web_search",
    "args": { "query": "roblox", "top_k": 2 }
  }
}
```

If allowed, response will include:
```json
"tool_result": {
  "name": "web_search",
  "executed": true,
  "output": { "results": [ ... ] }
}
```

If denied by policy, response will include:
```json
"tool_result": {
  "name": "web_search",
  "executed": false,
  "reason": "policy_denied"
}
```

## Authentication

The gateway uses JWT bearer auth.

Environment:
```bash
export JWT_SECRET="replace-me"
```

Requests should include:
```bash
-H "Authorization: Bearer <token>"
```

In tests, we intentionally run two modes:
- real auth client for auth specific tests
- auth bypass client for gateway behavior tests

## Observability

- Structured logs for `/v1/scan` and `/v1/chat`
- Logs include request_id, caller_id, decision/action, risk_score, model_version, and latency_ms
- Raw prompts are not logged
- Basic Prometheus style metrics are incremented for scan decisions

## Local development

### Requirements
- Python 3.x

### Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run
```bash
export JWT_SECRET="dev-secret"
uvicorn app.main:app --reload
```

OpenAPI UI:
- `http://localhost:8000/docs`

## Tests

Run:
```bash
python3 -m pytest -q
```

Test coverage includes:
- Auth behavior (401 without token, 200 with token)
- Scan contract and validation
- Chat policy enforcement (block, review, proceed)
- Tool boundary (executes only on allow, denied otherwise)
- Registry strict arg validation

## Repository structure

- `app/main.py` - FastAPI app entrypoint
- `app/api/` - routes and request/response schemas
- `app/security/` - JWT auth helpers
- `app/services/` - detection logic and orchestration
- `app/tools/` - tool registry, stub tools, strict arg schemas
- `app/core/` - metrics and shared utilities
- `artifacts/` - trained model artifacts (TF IDF + logistic regression)
- `docs/` - design notes and threat model
- `tests/` - unit and HTTP level tests

## Threat model (short)

Assume an adversary may:
- attempt prompt injection and instruction override
- probe policy thresholds and responses
- attempt to trigger privileged capability execution via tool requests

Mitigations in this repo:
- explicit policy mapping with deterministic enforcement paths
- strict input validation and bounded fields
- tool capability gating by allowlist and strict arg schemas
- no raw prompt logging

## Non goals

This repo does not claim to:
- guarantee detection of all jailbreaks or obfuscation
- provide complete prevention against prompt injection in every setting
- run real external tools (network, filesystem, database) in the default configuration

## Status

Current focus is a secure baseline gateway with clear boundaries, tests, and deterministic behavior that can be integrated in front of an LLM application.