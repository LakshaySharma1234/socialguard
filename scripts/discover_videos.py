import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import get_settings
from app.core.database import init_database
from app.services.video_discovery import discover_and_process_videos


def _default_queries():
    return [query.strip() for query in get_settings()["youtube_discovery_queries"].split(",") if query.strip()]


def main():
    parser = argparse.ArgumentParser(description="Discover YouTube videos and queue comment scans.")
    parser.add_argument(
        "--query",
        dest="queries",
        action="append",
        help="Repeat to provide one or more discovery queries. Defaults to env-configured spam-heavy queries.",
    )
    parser.add_argument("--max-videos", type=int, default=25, help="Videos to scan per query")
    parser.add_argument("--comments-per-video", type=int, default=100, help="Comments to fetch per video")
    parser.add_argument(
        "--auto-moderate",
        action="store_true",
        help="Delete comments classified as spam during processing",
    )
    args = parser.parse_args()

    queries = args.queries or _default_queries()
    print(
        "starting discovery "
        f"queries={queries} max_videos={args.max_videos} "
        f"comments_per_video={args.comments_per_video} auto_moderate={args.auto_moderate}",
        flush=True,
    )
    init_database()
    result = discover_and_process_videos(
        queries=queries,
        max_videos_per_query=args.max_videos,
        comments_per_video=args.comments_per_video,
        auto_moderate=args.auto_moderate,
    )

    for item in result["results"]:
        print(
            f"query={item['query']} video_id={item['video_id']} "
            f"queued={item['queued_count']} tasks={item['task_ids']}"
        )

    print(f"videos_processed={result['videos_processed']}")


if __name__ == "__main__":
    main()
