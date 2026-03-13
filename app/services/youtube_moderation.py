from app.services.youtube_auth import get_authenticated_service


def delete_comment(comment_id):
    youtube = get_authenticated_service()

    youtube.comments().setModerationStatus(
        id=comment_id,
        moderationStatus="rejected"
    ).execute()

    return {"status": "comment removed"}
