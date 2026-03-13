from typing import Optional

from app.services.youtube_fetcher import fetch_comments
from app.worker.tasks import scan_comment_batch


def process_video_comments(
    video_id: str,
    discovery_query: Optional[str] = None,
    auto_moderate: bool = False,
    max_results: int = 100,
):
    comments = fetch_comments(video_id, max_results=max_results)

    if not comments:
        return {
            "queued_count": 0,
            "task_ids": [],
        }

    task_result = scan_comment_batch.delay(comments, video_id, discovery_query, auto_moderate)

    return {
        "queued_count": len(comments),
        "task_ids": [task_result.id],
    }
