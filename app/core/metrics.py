from prometheus_client import Counter, Histogram

SCAN_REQUESTS_TOTAL = Counter(
    "scan_requests_total",
    "Total number of /v1/scan requests",
    ["decision"],
)

SCAN_LATENCY_SECONDS = Histogram(
    "scan_request_latency_seconds",
    "Latency for /v1/scan requests in seconds",
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0),
)
