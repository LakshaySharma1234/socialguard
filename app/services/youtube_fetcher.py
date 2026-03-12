import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from googleapiclient.discovery import build


ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=ENV_PATH)


@lru_cache(maxsize=1)
def _get_youtube_client():
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "YOUTUBE_API_KEY is not set. Add it to your environment before calling /scan-video."
        )
    return build("youtube", "v3", developerKey=api_key)


def fetch_comments(video_id):
    youtube = _get_youtube_client()

    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=20,
        textFormat="plainText"
    )

    response = request.execute()

    comments = []

    for item in response["items"]:

        comment_id = item["snippet"]["topLevelComment"]["id"]

        text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]

        comments.append({
            "id": comment_id,
            "text": text
        })

    return comments