import joblib

model = joblib.load("artifacts/model.pkl")
vectorizer = joblib.load("artifacts/vectorizer.pkl")

REVIEW_THRESHOLD = 0.5
HIGH_RISK_THRESHOLD = 0.8


def scan_prompt(prompt: str):
    model_version = "lr-tfidf-v1"

    X = vectorizer.transform([prompt])

    risk_score = float(model.predict_proba(X)[0][1])
    if risk_score <= REVIEW_THRESHOLD:
        decision = "allow"
    elif risk_score <= HIGH_RISK_THRESHOLD:
        decision = "review"
    else:
        decision = "high_risk"

    result = (decision, risk_score, model_version)
    return result
