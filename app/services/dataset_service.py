from pathlib import Path
from typing import Optional

import pandas as pd

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models.comment import Comment


def export_comments_dataset(
    export_path: Optional[str] = None,
    require_moderated_labels: bool = False,
):
    settings = get_settings()
    resolved_export_path = Path(export_path or settings["export_dataset_path"])
    resolved_export_path.parent.mkdir(parents=True, exist_ok=True)

    db = SessionLocal()
    try:
        query = db.query(Comment)
        if require_moderated_labels:
            query = query.filter(
                (Comment.was_deleted.is_(True)) | (Comment.moderation_status == "clean")
            )
        comments = query.all()
    finally:
        db.close()

    records = []
    for comment in comments:
        label = 1 if (comment.was_deleted or comment.spam) else 0
        records.append(
            {
                "CONTENT": comment.text,
                "CLASS": label,
                "video_id": comment.video_id,
                "youtube_comment_id": comment.youtube_comment_id,
                "author": comment.author,
                "like_count": comment.like_count or 0,
                "reply_count": comment.reply_count or 0,
                "published_at": comment.published_at.isoformat() if comment.published_at else None,
                "moderation_status": comment.moderation_status,
                "discovery_query": comment.discovery_query,
            }
        )

    dataframe = pd.DataFrame.from_records(
        records,
        columns=[
            "CONTENT",
            "CLASS",
            "video_id",
            "youtube_comment_id",
            "author",
            "like_count",
            "reply_count",
            "published_at",
            "moderation_status",
            "discovery_query",
        ],
    )
    dataframe.to_csv(resolved_export_path, index=False)
    return {
        "path": str(resolved_export_path),
        "rows": len(dataframe),
    }
