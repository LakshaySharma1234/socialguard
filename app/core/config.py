import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=ENV_PATH)


@lru_cache(maxsize=1)
def get_settings():
    return {
        "database_url": os.getenv("DATABASE_URL", "postgresql://localhost/socialguard"),
        "youtube_api_key": os.getenv("YOUTUBE_API_KEY"),
        "youtube_client_secret_file": os.getenv("YOUTUBE_CLIENT_SECRET_FILE"),
        "youtube_oauth_token_file": os.getenv("YOUTUBE_OAUTH_TOKEN_FILE", "youtube_token.json"),
        "youtube_discovery_queries": os.getenv(
            "YOUTUBE_DISCOVERY_QUERIES",
            "crypto investment,earn money online,bitcoin profit,AI trading bot,giveaway winner",
        ),
        "auto_delete_spam_comments": os.getenv("AUTO_DELETE_SPAM_COMMENTS", "false").lower() == "true",
        "model_path": os.getenv("SPAM_MODEL_PATH", "app/ml/spam_model.pkl"),
        "base_dataset_path": os.getenv("SPAM_BASE_DATASET_PATH", "data/youtube_spam.csv"),
        "export_dataset_path": os.getenv(
            "SPAM_EXPORT_DATASET_PATH",
            "data/generated/youtube_comments_dataset.csv",
        ),
    }
