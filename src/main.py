import asyncio
import sys
import argparse
from loguru import logger
from dvach.infrastructure.client import DvachClient
from dvach.application.watcher import ThreadWatcher
from dvach.application.board_service import BoardService
from dvach.shared.utils import strip_html

async def list_top_threads(board: str, limit: int, sort: str):
    client = DvachClient()
    service = BoardService(client)
    
    logger.info(f"Fetching top {limit} threads from /{board}/ sorted by {sort}...")
    
    try:
        threads = await service.get_top_threads(board, limit, sort)
        print(f"\n{'#'*10} TOP THREADS ON /{board}/ {'#'*10}")
        for i, t in enumerate(threads, 1):
            subject = t.subject if t.subject else strip_html(t.op_post.comment)[:60] + "..."
            print(f"{i}. [{t.posts_count} posts] ID: {t.id}")
            print(f"   Subject: {subject}")
            print(f"   Last Activity: {t.last_hit}")
            print("-" * 40)
    finally:
        await client.close()

async def watch_thread(board: str, thread_id: int):
    client = DvachClient()
    watcher = ThreadWatcher(client, board, thread_id)

    logger.info(f"Monitoring /{board}/{thread_id}. Press Ctrl+C to stop.")

    try:
        async for post in watcher.watch():
            print("-" * 40)
            print(f"Post ID: {post.id} | Time: {post.timestamp}")
            clean_comment = strip_html(post.comment)
            print(f"\n{clean_comment}")
            print("-" * 40)
    except KeyboardInterrupt:
        logger.info("Stopping watcher...")
    finally:
        await client.close()

def main():
    parser = argparse.ArgumentParser(description="2ch.org API CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Watch command
    watch_parser = subparsers.add_parser("watch", help="Monitor a thread")
    watch_parser.add_argument("board", help="Board code (e.g., b)")
    watch_parser.add_argument("thread", type=int, help="Thread ID")

    # Top command
    top_parser = subparsers.add_parser("top", help="List top threads")
    top_parser.add_argument("board", help="Board code (e.g., b)")
    top_parser.add_argument("--limit", type=int, default=10, help="Number of threads")
    top_parser.add_argument("--sort", choices=["posts", "creation", "activity"], default="posts", help="Sorting criteria")

    args = parser.parse_args()

    if args.command == "watch":
        asyncio.run(watch_thread(args.board, args.thread))
    elif args.command == "top":
        asyncio.run(list_top_threads(args.board, args.limit, args.sort))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
