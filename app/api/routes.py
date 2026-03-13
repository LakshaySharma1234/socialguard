from fastapi import APIRouter, HTTPException
from googleapiclient.errors import HttpError

from app.core.database import SessionLocal
from app.ml.train_model import train_and_save_model
from app.models.comment import Comment
from app.models.schemas import (
    CommentRequest,
    DiscoverVideosRequest,
    ScanVideoRequest,
    TrainModelRequest,
)
from app.services.comment_pipeline import process_video_comments
from app.services.dataset_service import export_comments_dataset
from app.services.spam_filter import detect_spam
from app.services.video_discovery import discover_and_process_videos
from app.services.youtube_moderation import delete_comment
from app.services.youtube_auth import ensure_authenticated_youtube


router = APIRouter()


@router.post("/detect-spam")
def detect(comment: CommentRequest):
    result = detect_spam(comment.text)
    return {
        "comment": comment.text,
        "spam": result["spam"],
        "score": result["score"],
        "reason": result["reason"],
        "ml_score": result["ml_score"],
    }


@router.post("/scan-video")
def scan_video(request: ScanVideoRequest):
    try:
        queue_result = process_video_comments(
            video_id=request.video_id,
            discovery_query=request.discovery_query,
            auto_moderate=request.auto_moderate,
            max_results=request.max_results,
        )
    except HttpError as exc:
        if getattr(exc.resp, "status", None) == 404:
            raise HTTPException(status_code=404, detail="Video not found") from exc
        raise HTTPException(status_code=502, detail="YouTube API request failed") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "status": "comments queued for scanning",
        "video_id": request.video_id,
        "queued_count": queue_result["queued_count"],
        "task_ids": queue_result["task_ids"],
    }


@router.post("/discover-videos")
def discover_videos(request: DiscoverVideosRequest):
    try:
        return discover_and_process_videos(
            queries=request.queries,
            max_videos_per_query=request.max_videos_per_query,
            comments_per_video=request.comments_per_video,
            auto_moderate=request.auto_moderate,
        )
    except HttpError as exc:
        raise HTTPException(status_code=502, detail="YouTube API request failed") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/youtube-auth")
def youtube_auth():
    try:
        return ensure_authenticated_youtube()
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/train-model")
def train_model(request: TrainModelRequest):
    try:
        export_result = export_comments_dataset(
            export_path=request.export_path,
            require_moderated_labels=request.require_moderated_labels,
        )
        train_result = train_and_save_model(
            include_base_dataset=request.include_base_dataset,
            require_moderated_labels=request.require_moderated_labels,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "status": "model trained",
        "dataset_path": export_result["path"],
        "exported_rows": export_result["rows"],
        "training_rows": train_result["rows"],
        "model_path": train_result["model_path"],
        "report": train_result["report"],
    }


@router.get("/comments/export")
def export_comments():
    return export_comments_dataset()


@router.post("/comments/{comment_id}/delete")
def moderate_comment(comment_id: str):
    try:
        return {"comment_id": comment_id, **delete_comment(comment_id)}
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/comments")
def get_comments():
    db = SessionLocal()
    try:
        return db.query(Comment).all()
    finally:
        db.close()
