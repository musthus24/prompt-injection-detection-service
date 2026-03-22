from .default_model import DefaultModel
from .models import DetectionModel, ScanResult

_REVIEW_THRESHOLD = 0.5
_HIGH_RISK_THRESHOLD = 0.8


class Scanner:
    """Scans text for prompt injection attempts.

    Args:
        model: A detection model implementing the ``DetectionModel`` protocol.
            When *None* the built-in logistic-regression + TF-IDF model is used.
        review_threshold: Risk scores above this trigger a "review" decision.
        high_risk_threshold: Risk scores above this trigger a "high_risk" decision.
    """

    def __init__(
        self,
        *,
        model: DetectionModel | None = None,
        review_threshold: float = _REVIEW_THRESHOLD,
        high_risk_threshold: float = _HIGH_RISK_THRESHOLD,
    ):
        self._model = model or DefaultModel()
        self._review_threshold = review_threshold
        self._high_risk_threshold = high_risk_threshold

    def scan(self, text: str) -> ScanResult:
        """Scan *text* and return a ``ScanResult``."""
        risk_score = self._model.predict_risk(text)
        decision = self._classify(risk_score)
        return ScanResult(
            decision=decision,
            risk_score=risk_score,
            model_version=self._model.version,
        )

    def _classify(self, risk_score: float) -> str:
        if risk_score <= self._review_threshold:
            return "allow"
        if risk_score <= self._high_risk_threshold:
            return "review"
        return "high_risk"
