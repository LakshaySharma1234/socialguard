from app.core.database import SessionLocal
from app.models.comment import Comment
from app.services.spam_filter import detect_spam
from app.services.youtube_moderation import delete_comment
from app.worker.celery_app import celery


@celery.task
def scan_comment_batch(comments, video_id):
    db = SessionLocal()

    try:
        for comment in comments:
            text = comment["text"]
            comment_id = comment["id"]

            result = detect_spam(text)

            if result["spam"]:
                delete_comment(comment_id)

            db_comment = Comment(
                video_id=video_id,
                text=text,
                spam=result["spam"],
                score=result["score"],
            )
            db.add(db_comment)

        db.commit()
        return {"processed": len(comments)}
    finally:
        db.close()
