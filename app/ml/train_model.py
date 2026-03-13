import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from app.core.config import get_settings
from app.services.dataset_service import export_comments_dataset
from app.services.spam_filter import reload_model


def _load_dataframe(path: str):
    try:
        dataframe = pd.read_csv(path)
    except FileNotFoundError:
        return pd.DataFrame(columns=["CONTENT", "CLASS"])
    if dataframe.empty:
        return dataframe
    return dataframe.dropna(subset=["CONTENT", "CLASS"])


def build_training_dataframe(include_base_dataset: bool = True, require_moderated_labels: bool = False):
    settings = get_settings()
    frames = []

    if include_base_dataset:
        frames.append(_load_dataframe(settings["base_dataset_path"]))

    exported = export_comments_dataset(require_moderated_labels=require_moderated_labels)
    frames.append(_load_dataframe(exported["path"]))

    combined = pd.concat([frame for frame in frames if not frame.empty], ignore_index=True)
    return combined.drop_duplicates(subset=["CONTENT", "CLASS"])


def train_and_save_model(include_base_dataset: bool = True, require_moderated_labels: bool = False):
    settings = get_settings()
    dataframe = build_training_dataframe(
        include_base_dataset=include_base_dataset,
        require_moderated_labels=require_moderated_labels,
    )

    if dataframe.empty:
        raise RuntimeError("No training data available. Collect or import comments before training.")
    if len(set(dataframe["CLASS"])) < 2:
        raise RuntimeError("Training data needs both spam and non-spam labels.")

    X = dataframe["CONTENT"]
    y = dataframe["CLASS"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y if len(set(y)) > 1 else None,
    )

    model = Pipeline(
        [
            ("tfidf", TfidfVectorizer(stop_words="english")),
            ("classifier", MultinomialNB()),
        ]
    )
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    report = classification_report(y_test, predictions, output_dict=False)

    joblib.dump(model, settings["model_path"])
    reload_model()

    return {
        "rows": len(dataframe),
        "model_path": settings["model_path"],
        "report": report,
    }


if __name__ == "__main__":
    result = train_and_save_model()
    print(result["report"])
    print(f"Model trained and saved to {result['model_path']} with {result['rows']} rows.")
