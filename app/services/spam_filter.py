import joblib
import re
from pathlib import Path

from app.core.config import get_settings
from app.utils.similarity import is_repeated


SUSPICIOUS_KEYWORDS = [
    "telegram",
    "whatsapp",
    "contact me",
    "investment advisor",
    "dm me",
    "guaranteed profit",
    "trading bot",
]

_model = None


def _get_model():
    global _model
    if _model is not None:
        return _model

    model_path = Path(get_settings()["model_path"])
    if not model_path.exists():
        return None

    _model = joblib.load(model_path)
    return _model


def reload_model():
    global _model
    _model = None
    return _get_model()


def detect_links(text):

    link_pattern = r"(https?://|www\.)"
    return bool(re.search(link_pattern, text))


def detect_spaced_spam(text):

    spaced_patterns = [
        r"t\s*e\s*l\s*e\s*g\s*r\s*a\s*m",
        r"w\s*h\s*a\s*t\s*s\s*a\s*p\s*p",
        r"c\s*r\s*y\s*p\s*t\s*o"
    ]

    for pattern in spaced_patterns:
        if re.search(pattern, text.lower()):
            return True

    return False


def detect_spam(comment: str):
    text = comment.lower()
    score = 0
    reasons = []

    if detect_links(text):
        score += 1
        reasons.append("link detected")

    if detect_spaced_spam(text):
        score += 1
        reasons.append("spaced keyword spam")

    if any(keyword in text for keyword in SUSPICIOUS_KEYWORDS):
        score += 1
        reasons.append("suspicious keyword")

    if is_repeated(text):
        score += 1
        reasons.append("repeated comment")

    ml_probability = 0.0
    model = _get_model()
    if model is not None:
        ml_probability = float(model.predict_proba([text])[0][1])
        if ml_probability > 0.7:
            score += 1
            reasons.append("ml spam prediction")

    spam = score >= 1

    return {
        "spam": spam,
        "score": score,
        "ml_score": float(ml_probability),
        "reason": reasons if reasons else ["clean"]
    }
