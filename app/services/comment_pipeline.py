from app.services.youtube_fetcher import fetch_comments
from app.worker.tasks import scan_comment_batch


def process_video_comments(video_id: str):

    comments = fetch_comments(video_id)

    if not comments:
        return {
            "queued_count": 0,
            "task_ids": [],
        }

    task_result = scan_comment_batch.delay(comments, video_id)

    return {
        "queued_count": len(comments),
        "task_ids": [task_result.id],
    }
