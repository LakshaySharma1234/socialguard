import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.database import init_database
from app.services.comment_pipeline import process_video_comments


def main():
    parser = argparse.ArgumentParser(description="Collect and queue YouTube comments for one video.")
    parser.add_argument("video_id", help="YouTube video ID to scan")
    parser.add_argument("--query", dest="discovery_query", help="Optional query that discovered the video")
    parser.add_argument("--max-results", type=int, default=100, help="Maximum comments to fetch")
    parser.add_argument(
        "--auto-moderate",
        action="store_true",
        help="Delete comments classified as spam during processing",
    )
    args = parser.parse_args()

    init_database()
    result = process_video_comments(
        video_id=args.video_id,
        discovery_query=args.discovery_query,
        auto_moderate=args.auto_moderate,
        max_results=args.max_results,
    )
    print(result)


if __name__ == "__main__":
    main()
