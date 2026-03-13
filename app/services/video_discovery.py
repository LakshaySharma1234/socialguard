from app.services.comment_pipeline import process_video_comments
from app.services.youtube_fetcher import search_videos


def discover_and_process_videos(
    queries: list[str],
    max_videos_per_query: int = 25,
    comments_per_video: int = 100,
    auto_moderate: bool = False,
):
    results = []
    seen_video_ids = set()

    for query in queries:
        print(f"discovering query={query} max_videos={max_videos_per_query}", flush=True)
        video_ids = search_videos(query, max_results=max_videos_per_query)
        print(f"query={query} discovered={len(video_ids)}", flush=True)
        for video_id in video_ids:
            if video_id in seen_video_ids:
                print(f"skipping duplicate video_id={video_id}", flush=True)
                continue

            seen_video_ids.add(video_id)
            print(
                f"queueing video_id={video_id} query={query} comments_per_video={comments_per_video}",
                flush=True,
            )
            queue_result = process_video_comments(
                video_id=video_id,
                discovery_query=query,
                auto_moderate=auto_moderate,
                max_results=comments_per_video,
            )
            results.append(
                {
                    "query": query,
                    "video_id": video_id,
                    "queued_count": queue_result["queued_count"],
                    "task_ids": queue_result["task_ids"],
                }
            )

    return {
        "queries": queries,
        "videos_processed": len(results),
        "results": results,
    }
