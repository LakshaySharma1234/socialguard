from fastapi import APIRouter, HTTPException
from googleapiclient.errors import HttpError
from app.models.schemas import CommentRequest
from app.services.spam_filter import detect_spam
from app.services.comment_pipeline import process_video_comments
from app.services.youtube_moderation import ensure_authenticated_youtube
from app.core.database import SessionLocal
from app.models.comment import Comment


router = APIRouter()


@router.post("/detect-spam")
def detect(comment: CommentRequest):

    result = detect_spam(comment.text)

    return {
        "comment": comment.text,
        "spam": result["spam"],
        "score": result["score"],
        "reason": result["reason"]
    }


@router.post("/scan-video")
def scan_video(video_id: str):
    try:
        queue_result = process_video_comments(video_id)
    except HttpError as exc:
        if getattr(exc, "status_code", None) == 404:
            raise HTTPException(status_code=404, detail="Video not found") from exc
        raise HTTPException(status_code=502, detail="YouTube API request failed") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "status": "comments queued for scanning",
        "video_id": video_id,
        "queued_count": queue_result["queued_count"],
        "task_ids": queue_result["task_ids"],
    }


@router.post("/youtube-auth")
def youtube_auth():
    try:
        ensure_authenticated_youtube()
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"status": "youtube oauth ready"}


@router.get("/comments")
def get_comments():

    db = SessionLocal()

    comments = db.query(Comment).all()

    db.close()

    return comments
