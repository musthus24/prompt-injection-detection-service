from prompt_injection_detector import DetectionModel, Scanner, ScanResult


class FakeModel:
    """A minimal model that returns a fixed risk score."""

    def __init__(self, score: float):
        self._score = score

    @property
    def version(self) -> str:
        return "fake-v1"

    def predict_risk(self, text: str) -> float:
        return self._score


def test_scan_returns_scan_result():
    scanner = Scanner(model=FakeModel(0.1))
    result = scanner.scan("hello")
    assert isinstance(result, ScanResult)
    assert hasattr(result, "decision")
    assert hasattr(result, "risk_score")
    assert hasattr(result, "model_version")


def test_low_score_allows():
    scanner = Scanner(model=FakeModel(0.2))
    result = scanner.scan("hello")
    assert result.decision == "allow"
    assert result.risk_score == 0.2
    assert result.model_version == "fake-v1"


def test_mid_score_reviews():
    scanner = Scanner(model=FakeModel(0.6))
    result = scanner.scan("hello")
    assert result.decision == "review"


def test_high_score_flags():
    scanner = Scanner(model=FakeModel(0.9))
    result = scanner.scan("hello")
    assert result.decision == "high_risk"


def test_boundary_at_review_threshold():
    scanner = Scanner(model=FakeModel(0.5))
    result = scanner.scan("hello")
    assert result.decision == "allow"


def test_boundary_at_high_risk_threshold():
    scanner = Scanner(model=FakeModel(0.8))
    result = scanner.scan("hello")
    assert result.decision == "review"


def test_custom_thresholds():
    scanner = Scanner(model=FakeModel(0.3), review_threshold=0.2, high_risk_threshold=0.4)
    result = scanner.scan("hello")
    assert result.decision == "review"


def test_custom_model_protocol():
    model = FakeModel(0.1)
    assert isinstance(model, DetectionModel)


def test_default_model_loads():
    scanner = Scanner()
    result = scanner.scan("What is the weather today?")
    assert result.decision in ("allow", "review", "high_risk")
    assert 0.0 <= result.risk_score <= 1.0
    assert result.model_version == "lr-tfidf-v1"
