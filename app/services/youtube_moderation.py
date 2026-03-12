import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=ENV_PATH)

YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]


def _default_client_secret_path():
    root = Path(__file__).resolve().parents[2]
    matches = sorted(root.glob("client_secret*.json"))
    return matches[0] if matches else None


@lru_cache(maxsize=1)
def _get_authenticated_youtube_client():
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise RuntimeError(
            "YouTube moderation requires google-auth-oauthlib and google-api-python-client."
        ) from exc

    root = Path(__file__).resolve().parents[2]
    token_path = Path(os.getenv("YOUTUBE_OAUTH_TOKEN_FILE", root / "youtube_token.json"))
    client_secret = os.getenv("YOUTUBE_CLIENT_SECRET_FILE")
    client_secret_path = Path(client_secret) if client_secret else _default_client_secret_path()

    credentials = None
    if token_path.exists():
        credentials = Credentials.from_authorized_user_file(str(token_path), YOUTUBE_SCOPES)

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    elif not credentials or not credentials.valid:
        if not client_secret_path or not client_secret_path.exists():
            raise RuntimeError(
                "YouTube moderation needs OAuth client credentials. "
                "Set YOUTUBE_CLIENT_SECRET_FILE or place a client_secret*.json file in the project root."
            )

        flow = InstalledAppFlow.from_client_secrets_file(str(client_secret_path), YOUTUBE_SCOPES)
        credentials = flow.run_local_server(port=0)
        token_path.write_text(credentials.to_json())

    return build("youtube", "v3", credentials=credentials)


def delete_comment(comment_id: str):
    youtube = _get_authenticated_youtube_client()
    youtube.comments().setModerationStatus(
        id=comment_id,
        moderationStatus="rejected",
    ).execute()


def ensure_authenticated_youtube():
    _get_authenticated_youtube_client()
