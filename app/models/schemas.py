from pydantic import BaseModel

class CommentRequest(BaseModel):
    text: str