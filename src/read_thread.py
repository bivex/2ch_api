#!/usr/bin/env python3
import asyncio
import argparse
import urllib.request
import json
from html.parser import HTMLParser
from typing import List, Optional


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []

    def handle_data(self, data):
        self.fed.append(data)

    def get_data(self):
        return "".join(self.fed)


def strip_html(text: str) -> str:
    s = MLStripper()
    s.feed(text)
    return s.get_data()


async def fetch_thread(
    board: str, thread_id: int, limit: Optional[int] = None
) -> List[dict]:
    url = f"https://2ch.org/{board}/res/{thread_id}.json"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())

    threads = data.get("threads", [])
    posts = threads[0].get("posts", []) if threads else data.get("posts", [])
    if limit:
        posts = posts[:limit]
    return posts


async def main():
    parser = argparse.ArgumentParser(description="Read 2ch thread posts")
    parser.add_argument("board", help="Board code (e.g., po, news)")
    parser.add_argument("thread", type=int, help="Thread ID")
    parser.add_argument("--limit", type=int, default=None, help="Max posts to show")
    parser.add_argument("--raw", action="store_true", help="Show original HTML")
    args = parser.parse_args()

    posts = await fetch_thread(args.board, args.thread, args.limit)
    print(f"Total posts: {len(posts)}\n")

    for p in posts:
        num = p.get("num", "?")
        comment = p.get("comment", "") if args.raw else strip_html(p.get("comment", ""))
        comment = comment.replace("\n", " ")
        if len(comment) > 600:
            comment = comment[:600] + "..."
        print(f"--- POST {num} ---")
        print(comment)
        print()


if __name__ == "__main__":
    asyncio.run(main())
