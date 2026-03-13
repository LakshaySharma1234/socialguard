import os
from functools import lru_cache

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.core.config import get_settings


@lru_cache(maxsize=1)
def get_youtube_client():
    api_key = get_settings()["youtube_api_key"] or os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "YOUTUBE_API_KEY is not set. Add it to your environment before using YouTube discovery or scanning."
        )
    return build("youtube", "v3", developerKey=api_key)


def search_videos(query: str, max_results: int = 50):
    youtube = get_youtube_client()
    video_ids = []
    next_page_token = None

    while len(video_ids) < max_results:
        batch_size = min(50, max_results - len(video_ids))
        request = youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=batch_size,
            pageToken=next_page_token,
            order="relevance",
        )
        response = request.execute()

        for item in response.get("items", []):
            video_id = item.get("id", {}).get("videoId")
            if video_id:
                video_ids.append(video_id)

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return video_ids


def fetch_comments(video_id: str, max_results: int = 100):
    youtube = get_youtube_client()
    comments = []
    next_page_token = None

    while len(comments) < max_results:
        batch_size = min(100, max_results - len(comments))
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=batch_size,
            textFormat="plainText",
            pageToken=next_page_token,
        )

        try:
            response = request.execute()
        except HttpError as exc:
            if getattr(exc.resp, "status", None) == 403:
                return []
            raise

        for item in response.get("items", []):
            top_level_comment = item["snippet"]["topLevelComment"]
            snippet = top_level_comment["snippet"]
            comments.append({
                "id": top_level_comment["id"],
                "text": snippet["textDisplay"],
                "author": snippet.get("authorDisplayName"),
                "like_count": snippet.get("likeCount", 0),
                "reply_count": item["snippet"].get("totalReplyCount", 0),
                "published_at": snippet.get("publishedAt"),
            })

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return comments
