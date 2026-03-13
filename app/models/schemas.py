from typing import Optional

from pydantic import BaseModel, Field


class CommentRequest(BaseModel):
    text: str


class ScanVideoRequest(BaseModel):
    video_id: str
    discovery_query: Optional[str] = None
    auto_moderate: bool = False
    max_results: int = Field(default=100, ge=1, le=500)


class DiscoverVideosRequest(BaseModel):
    queries: list[str]
    max_videos_per_query: int = Field(default=25, ge=1, le=50)
    comments_per_video: int = Field(default=100, ge=1, le=500)
    auto_moderate: bool = False


class TrainModelRequest(BaseModel):
    export_path: Optional[str] = None
    include_base_dataset: bool = True
    require_moderated_labels: bool = False
