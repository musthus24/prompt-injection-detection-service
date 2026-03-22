from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class ScanResult:
    """Result of a prompt injection scan."""

    decision: str  # "allow" | "review" | "high_risk"
    risk_score: float  # 0.0 - 1.0
    model_version: str


@runtime_checkable
class DetectionModel(Protocol):
    """Protocol that custom detection models must implement."""

    @property
    def version(self) -> str: ...

    def predict_risk(self, text: str) -> float: ...
