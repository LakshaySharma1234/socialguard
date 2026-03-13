from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models.comment import Comment
from app.services.spam_filter import detect_spam
from app.services.youtube_moderation import delete_comment
from app.worker.celery_app import celery


def _parse_published_at(value):
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _upsert_comment(db, payload):
    youtube_comment_id = payload["youtube_comment_id"]
    existing = db.query(Comment).filter(Comment.youtube_comment_id == youtube_comment_id).first()
    if existing:
        for key, value in payload.items():
            setattr(existing, key, value)
        return existing

    db_comment = Comment(**payload)
    db.add(db_comment)
    return db_comment


@celery.task
def scan_comment_batch(comments, video_id, discovery_query=None, auto_moderate=None):
    db = SessionLocal()
    delete_spam = get_settings()["auto_delete_spam_comments"] if auto_moderate is None else auto_moderate
    deleted_count = 0

    try:
        for comment in comments:
            text = comment["text"]
            comment_id = comment["id"]
            result = detect_spam(text)

            moderation_status = "clean"
            was_deleted = False
            if result["spam"]:
                moderation_status = "flagged"
                if delete_spam:
                    try:
                        delete_comment(comment_id)
                        moderation_status = "deleted"
                        was_deleted = True
                        deleted_count += 1
                    except Exception:
                        moderation_status = "delete_failed"

            _upsert_comment(
                db,
                {
                    "youtube_comment_id": comment_id,
                    "video_id": video_id,
                    "discovery_query": discovery_query,
                    "text": text,
                    "author": comment.get("author"),
                    "like_count": comment.get("like_count", 0),
                    "reply_count": comment.get("reply_count", 0),
                    "published_at": _parse_published_at(comment.get("published_at")),
                    "spam": result["spam"],
                    "score": result["score"],
                    "ml_score": result["ml_score"],
                    "detection_reasons": ",".join(result["reason"]),
                    "moderation_status": moderation_status,
                    "was_deleted": was_deleted,
                },
            )

        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    finally:
        db.close()

    return {"processed": len(comments), "deleted_count": deleted_count}
