from prompt_injection_detector import Scanner

_scanner = Scanner()


def scan_prompt(prompt: str):
    result = _scanner.scan(prompt)
    return (result.decision, result.risk_score, result.model_version)
