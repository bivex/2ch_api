import asyncio
import sys
from loguru import logger
from dvach.infrastructure.client import DvachClient
from dvach.application.watcher import ThreadWatcher
from dvach.shared.utils import strip_html

async def main():
    if len(sys.argv) < 3:
        print("Usage: python src/main.py <board> <thread_id>")
        sys.exit(1)

    board = sys.argv[1]
    thread_id = int(sys.argv[2])

    client = DvachClient()
    watcher = ThreadWatcher(client, board, thread_id)

    logger.info(f"Monitoring /{board}/{thread_id}. Press Ctrl+C to stop.")

    try:
        async for post in watcher.watch():
            print("-" * 40)
            print(f"Post ID: {post.id} | Time: {post.timestamp}")
            if post.subject:
                print(f"Subject: {post.subject}")
            
            clean_comment = strip_html(post.comment)
            print(f"\n{clean_comment}")
            
            if post.attachments:
                print(f"\nAttachments: {len(post.attachments)}")
                for att in post.attachments:
                    print(f"  - {att.url}")
            print("-" * 40)
    except KeyboardInterrupt:
        logger.info("Stopping watcher...")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
