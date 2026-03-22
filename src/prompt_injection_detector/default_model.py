from pathlib import Path

import joblib

_ARTIFACTS_DIR = Path(__file__).parent / "artifacts"


class DefaultModel:
    """Built-in logistic regression + TF-IDF detection model."""

    def __init__(self):
        self._model = None
        self._vectorizer = None

    def _load(self):
        if self._model is None:
            self._model = joblib.load(_ARTIFACTS_DIR / "model.pkl")
            self._vectorizer = joblib.load(_ARTIFACTS_DIR / "vectorizer.pkl")

    @property
    def version(self) -> str:
        return "lr-tfidf-v1"

    def predict_risk(self, text: str) -> float:
        self._load()
        X = self._vectorizer.transform([text])
        return float(self._model.predict_proba(X)[0][1])
