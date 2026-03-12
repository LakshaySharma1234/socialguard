import joblib
import re

from app.utils.similarity import is_repeated

model = joblib.load("app/ml/spam_model.pkl")


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

    # link detection
    if detect_links(text):
        score += 1
        reasons.append("link detected")

    # unicode / spaced detection
    if detect_spaced_spam(text):
        score += 1
        reasons.append("unicode spam")

    # repeated comment detection
    if is_repeated(text):
        score += 1
        reasons.append("repeated comment")

    # ML classifier
    ml_probability = model.predict_proba([text])[0][1]

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