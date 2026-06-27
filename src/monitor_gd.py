#!/usr/bin/env python3
import asyncio
import argparse
from datetime import datetime
from dvach.infrastructure.client import DvachClient
from dvach.application.board_service import BoardService
from dvach.shared.utils import strip_html


def format_timestamp(dt: datetime) -> str:
    now = datetime.now()
    diff = now - dt
    if diff.days > 0:
        return f"{diff.days}d ago"
    hours = diff.seconds // 3600
    if hours > 0:
        return f"{hours}h ago"
    minutes = (diff.seconds % 3600) // 60
    return f"{minutes}m ago"


def matches_keywords(thread, keywords: list) -> bool:
    if not keywords:
        return True
    text = ((thread.subject or "") + " " + strip_html(thread.op_post.comment)).lower()
    return any(kw.lower() in text for kw in keywords)


async def main():
    parser = argparse.ArgumentParser(
        description="Monitor /gd/ board for game dev activity"
    )
    parser.add_argument("--limit", type=int, default=20, help="Max threads to show")
    parser.add_argument(
        "--sort",
        choices=["posts", "creation", "activity"],
        default="activity",
        help="Sort order",
    )
    parser.add_argument(
        "--keywords",
        type=str,
        default="",
        help="Comma-separated keywords to filter (e.g., заказ,фриланс,ищу)",
    )
    parser.add_argument(
        "--all", action="store_true", help="Show all threads (ignore keywords)"
    )
    args = parser.parse_args()

    keywords = (
        [k.strip() for k in args.keywords.split(",") if k.strip()]
        if args.keywords
        else []
    )

    client = DvachClient()
    service = BoardService(client)

    try:
        threads = await service.get_top_threads("gd", limit=200, sort_by=args.sort)
        filtered = [t for t in threads if args.all or matches_keywords(t, keywords)]
        shown = filtered[: args.limit]

        if not shown:
            print("No threads found matching criteria.")
            return

        print(f"\n{'=' * 30} /gd/ MONITOR {'=' * 30}")
        print(f"Keywords: {', '.join(keywords) if keywords else 'ALL'}")
        print(f"Total qualifying threads: {len(filtered)}")
        print()

        for i, t in enumerate(shown, 1):
            subject = t.subject if t.subject else "(no subject)"
            content = strip_html(t.op_post.comment).replace("\n", " ")
            if len(content) > 250:
                content = content[:250] + "..."

            print(f"{i}. 🔥 {t.posts_count} posts | 👁 {format_timestamp(t.last_hit)}")
            print(f"   ID: {t.id}")
            print(f"   Title: {subject}")
            print(f"   Preview: {content}")
            print(f"   URL: https://2ch.org/gd/res/{t.id}.html")
            print("-" * 80)

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
