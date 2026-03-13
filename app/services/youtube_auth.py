from functools import lru_cache
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from app.core.config import get_settings


SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]


def _resolve_client_secret_file() -> str:
    configured_path = get_settings()["youtube_client_secret_file"]
    if configured_path and Path(configured_path).exists():
        return configured_path

    project_root = Path(__file__).resolve().parents[2]
    direct_match = project_root / "client_secret.json"
    if direct_match.exists():
        return str(direct_match)

    candidates = sorted(project_root.glob("client_secret*.json"))
    if candidates:
        return str(candidates[0])

    raise RuntimeError(
        "YouTube OAuth client secret file not found. Set YOUTUBE_CLIENT_SECRET_FILE or add client_secret.json."
    )


def _resolve_token_file() -> Path:
    configured_path = get_settings()["youtube_oauth_token_file"]
    return Path(configured_path).expanduser().resolve()


@lru_cache(maxsize=1)
def get_authenticated_service():
    token_path = _resolve_token_file()
    credentials = None

    if token_path.exists():
        credentials = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        token_path.write_text(credentials.to_json())

    if not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            _resolve_client_secret_file(),
            SCOPES
        )
        credentials = flow.run_local_server(host="localhost", port=0)
        token_path.write_text(credentials.to_json())

    youtube = build("youtube", "v3", credentials=credentials)

    return youtube


def ensure_authenticated_youtube():
    get_authenticated_service()
    return {"status": "youtube oauth ready"}
