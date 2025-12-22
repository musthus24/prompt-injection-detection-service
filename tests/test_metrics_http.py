def _extract_metric_value(metrics_text: str, metric_name: str) -> float:
    """
    Extracts the first numeric value for a metric line like:
    metric_name 123
    metric_name{label="x"} 123
    """
    for line in metrics_text.splitlines():
        if line.startswith("#"):
            continue
        if line.startswith(metric_name):
            # Split on whitespace and take the last token as the value
            parts = line.strip().split()
            if len(parts) >= 2:
                return float(parts[-1])
    raise AssertionError(f"Metric not found: {metric_name}")


def test_metrics_increment_after_scan(client):
    before_text = client.get("/metrics").text
    before_latency_count = _extract_metric_value(before_text, "scan_request_latency_seconds_count")

    request = client.post("/v1/scan", json={"prompt": "hello"})
    assert request.status_code == 200

    after_text = client.get("/metrics").text
    after_latency_count = _extract_metric_value(after_text, "scan_request_latency_seconds_count")

    assert after_latency_count == before_latency_count + 1
    assert "scan_requests_total" in after_text
