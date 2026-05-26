from typing import List
from ..domain.entities import Thread
from ..domain.interfaces import I2chClient

class BoardService:
    def __init__(self, client: I2chClient):
        self.client = client

    async def get_top_threads(
        self, 
        board_code: str, 
        limit: int = 10, 
        sort_by: str = "posts"
    ) -> List[Thread]:
        """
        Fetch and sort threads from a board.
        sort_by can be: 'posts' (default), 'creation', 'activity' (last hit)
        """
        threads = await self.client.get_threads(board_code)
        
        if sort_by == "posts":
            # Sort by number of posts (most discussed first)
            threads.sort(key=lambda t: t.posts_count, reverse=True)
        elif sort_by == "creation":
            # Sort by creation date (newest first)
            threads.sort(key=lambda t: t.op_post.timestamp, reverse=True)
        elif sort_by == "activity":
            # Sort by last hit / bump (most recent activity first)
            threads.sort(key=lambda t: t.last_hit, reverse=True)
            
        return threads[:limit]
