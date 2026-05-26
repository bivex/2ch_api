import httpx
from datetime import datetime
from typing import List
from ..domain.entities import Board, Thread, Post, Attachment
from ..domain.interfaces import I2chClient

class DvachClient(I2chClient):
    BASE_URL = "https://2ch.org"

    def __init__(self, timeout: float = 10.0):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.client = httpx.AsyncClient(base_url=self.BASE_URL, timeout=timeout, headers=headers)

    async def close(self):
        await self.client.aclose()

    async def get_boards(self) -> List[Board]:
        response = await self.client.get("/boards.json")
        response.raise_for_status()
        data = response.json()
        
        boards = []
        for category in data.values():
            if isinstance(category, list):
                for b in category:
                    boards.append(Board(
                        code=b["id"],
                        name=b["name"],
                        description=b.get("info", "")
                    ))
        return boards

    async def get_threads(self, board_code: str) -> List[Thread]:
        response = await self.client.get(f"/{board_code}/threads.json")
        response.raise_for_status()
        data = response.json()
        
        threads = []
        for t in data.get("threads", []):
            threads.append(Thread(
                id=int(t["num"]),
                board_code=board_code,
                op_post=self._map_post(t),
                posts_count=t.get("posts_count", 0),
                files_count=t.get("files_count", 0),
                last_hit=datetime.fromtimestamp(t.get("lasthit", t["timestamp"])),
                subject=t.get("subject")
            ))
        return threads

    async def get_thread_posts(self, board_code: str, thread_id: int) -> List[Post]:
        response = await self.client.get(f"/{board_code}/res/{thread_id}.json")
        response.raise_for_status()
        data = response.json()
        
        thread_data = data.get("threads", [{}])[0]
        return [self._map_post(p) for p in thread_data.get("posts", [])]

    async def get_new_posts(self, board_code: str, thread_id: int, last_post_id: int) -> List[Post]:
        # Using the mobile API for getting posts after a certain ID
        url = f"/api/mobile/v2/after/{board_code}/{thread_id}/{last_post_id}"
        response = await self.client.get(url)
        if response.status_code == 404:
            return [] # Thread might be dead or no new posts
        response.raise_for_status()
        data = response.json()
        
        return [self._map_post(p) for p in data.get("posts", [])]

    def _map_post(self, p: dict) -> Post:
        attachments = []
        for f in p.get("files", []):
            attachments.append(Attachment(
                path=f["path"],
                thumbnail=f["thumbnail"],
                size=f["size"],
                width=f["width"],
                height=f["height"],
                name=f["fullname"]
            ))
            
        return Post(
            id=int(p["num"]),
            comment=p["comment"],
            timestamp=datetime.fromtimestamp(p["timestamp"]),
            attachments=attachments,
            subject=p.get("subject"),
            email=p.get("email"),
            name=p.get("name"),
            trip=p.get("trip")
        )
