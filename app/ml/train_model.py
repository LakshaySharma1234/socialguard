import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

# load dataset
df = pd.read_csv("data/youtube_spam.csv")

# dataset columns usually look like:
# CONTENT = comment text
# CLASS = spam label (1 spam, 0 normal)

X = df["CONTENT"]
y = df["CLASS"]

# split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ML pipeline
model = Pipeline([
    ("tfidf", TfidfVectorizer(stop_words="english")),
    ("classifier", MultinomialNB())
])

# train
model.fit(X_train, y_train)

# evaluate
predictions = model.predict(X_test)

print(classification_report(y_test, predictions))

# save model
joblib.dump(model, "app/ml/spam_model.pkl")

print("Model trained and saved.")