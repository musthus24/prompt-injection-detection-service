# Graph Report - .  (2026-07-05)

## Corpus Check
- 8 files · ~5,791 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 173 nodes · 297 edges · 14 communities (12 shown, 2 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 29 edges (avg confidence: 0.71)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Detection Model & Scanner|Detection Model & Scanner]]
- [[_COMMUNITY_Tool Registry|Tool Registry]]
- [[_COMMUNITY_ChatScan API Schemas|Chat/Scan API Schemas]]
- [[_COMMUNITY_JWT Auth Tests|JWT Auth Tests]]
- [[_COMMUNITY_Core App Middleware|Core App Middleware]]
- [[_COMMUNITY_Chat Flow Auth Tests|Chat Flow Auth Tests]]
- [[_COMMUNITY_Docs & CI|Docs & CI]]
- [[_COMMUNITY_Custom Model Example|Custom Model Example]]
- [[_COMMUNITY_Quickstart Example|Quickstart Example]]
- [[_COMMUNITY_Misc|Misc]]

## God Nodes (most connected - your core abstractions)
1. `Scanner` - 17 edges
2. `create_access_token()` - 15 edges
3. `FakeModel` - 13 edges
4. `DetectionModel` - 10 edges
5. `chat()` - 9 edges
6. `build_default_registry()` - 9 edges
7. `BaseTool` - 9 edges
8. `DefaultModel` - 9 edges
9. `get_jwt_secret()` - 8 edges
10. `verify_token()` - 7 edges

## Surprising Connections (you probably didn't know these)
- `Publish to PyPI Workflow` --references--> `FastAPI Gateway Service`  [AMBIGUOUS]
  .github/workflows/publish.yml → README.md
- `test_default_model_loads()` --calls--> `Scanner`  [INFERRED]
  tests/test_scanner.py → src/prompt_injection_detector/scanner.py
- `Project README` --conceptually_related_to--> `Python Requirements`  [INFERRED]
  README.md → requirements.txt
- `test_scan_with_valid_token_succeeds()` --calls--> `create_access_token()`  [EXTRACTED]
  tests/test_auth_http.py → app/security/jwt.py
- `test_scan_benign_prompt_returns_200()` --calls--> `create_access_token()`  [EXTRACTED]
  tests/test_scan_http.py → app/security/jwt.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **SDK Detection Components** — readme_scanner, readme_detectionmodel, docs_design_scan_endpoint [INFERRED 0.75]
- **Chat Policy Enforcement Flow** — docs_design_chat_endpoint, docs_design_policy_contract, docs_design_tool_boundary, readme_jwt_auth [EXTRACTED 0.85]
- **Prompt Injection Threat Surfaces** — docs_threat_model_indirect_injection, docs_design_policy_contract, docs_design_tool_boundary [INFERRED 0.70]

## Communities (14 total, 2 thin omitted)

### Community 0 - "Detection Model & Scanner"
Cohesion: 0.09
Nodes (22): Protocol, DefaultModel, Built-in logistic regression + TF-IDF detection model., Prompt injection detection for LLM-powered applications., DetectionModel, Protocol that custom detection models must implement., Result of a prompt injection scan., ScanResult (+14 more)

### Community 1 - "Tool Registry"
Cohesion: 0.15
Nodes (16): build_default_registry(), BaseTool, Any, BaseModel, A tool is just:       - a stable name (string)       - an ArgsModel (Pydantic sc, Central allowlist. Only tools registered here can run.     Also enforces strict, ToolRegistry, UnknownToolError (+8 more)

### Community 2 - "Chat/Scan API Schemas"
Cohesion: 0.19
Nodes (19): chat(), map_scan_to_gateway_policy(), Request, Converts scan output -> gateway decision + action_taken.     scan_decision: allo, scan(), ChatMessage, ChatRequest, ChatResponse (+11 more)

### Community 3 - "JWT Auth Tests"
Cohesion: 0.19
Nodes (14): validate_security_config(), create_access_token(), get_jwt_secret(), test_scan_with_valid_token_succeeds(), test_create_access_token_contains_expected_claims(), test_tampered_token_fails_verification(), _extract_metric_value(), Extracts the first numeric value for a metric line like:     metric_name 123 (+6 more)

### Community 4 - "Core App Middleware"
Cohesion: 0.16
Nodes (10): http_exception_handler(), Exception, Request, unhandled_exception_handler(), validation_exception_handler(), configure_logging(), Request, RequestContextMiddleware (+2 more)

### Community 5 - "Chat Flow Auth Tests"
Cohesion: 0.13
Nodes (9): Purpose: enforce that requests include a valid Bearer token.      Returns:, verify_token(), HTTPAuthorizationCredentials, HTTPException, TestClient, client(), client_no_auth(), client() (+1 more)

### Community 6 - "Docs & CI"
Cohesion: 0.18
Nodes (16): LLM Security Gateway Design Document, POST /v1/chat Enforcement Endpoint, Policy Decision Contract, POST /v1/scan Advisory Endpoint, Tool Execution Boundary, Detection Notes, Threat Model, Indirect Prompt Injection via RAG (+8 more)

### Community 7 - "Custom Model Example"
Cohesion: 0.33
Nodes (3): KeywordModel, Bring your own detection model., A simple keyword-based detector (for demonstration).

## Ambiguous Edges - Review These
- `Publish to PyPI Workflow` → `FastAPI Gateway Service`  [AMBIGUOUS]
  .github/workflows/publish.yml · relation: references

## Knowledge Gaps
- **5 isolated node(s):** `CI Workflow`, `Publish to PyPI Workflow`, `Graphify Project Instructions`, `JWT Bearer Authentication`, `Detection Notes`
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Publish to PyPI Workflow` and `FastAPI Gateway Service`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **Why does `build_default_registry()` connect `Tool Registry` to `Chat/Scan API Schemas`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Why does `UnknownToolError` connect `Tool Registry` to `Chat/Scan API Schemas`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `Scanner` (e.g. with `DefaultModel` and `DetectionModel`) actually correct?**
  _`Scanner` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `DetectionModel` (e.g. with `Scanner` and `test_custom_model_protocol()`) actually correct?**
  _`DetectionModel` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Converts scan output -> gateway decision + action_taken.     scan_decision: allo`, `Client asks the gateway to invoke a named tool with arguments.     We keep args`, `What happened with the tool attempt.     executed=False means we refused or skip` to the rest of the system?**
  _25 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Detection Model & Scanner` be split into smaller, more focused modules?**
  _Cohesion score 0.09446693657219973 - nodes in this community are weakly interconnected._