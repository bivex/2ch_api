import asyncio
from typing import AsyncIterator, Optional
from loguru import logger
from ..domain.entities import Post
from ..domain.interfaces import I2chClient

class ThreadWatcher:
    def __init__(
        self, 
        client: I2chClient, 
        board_code: str, 
        thread_id: int, 
        interval: float = 10.0,
        initial_last_id: Optional[int] = None
    ):
        self.client = client
        self.board_code = board_code
        self.thread_id = thread_id
        self.interval = interval
        self.last_post_id = initial_last_id
        self._running = False

    async def watch(self) -> AsyncIterator[Post]:
        self._running = True
        
        # If no last_post_id provided, fetch current posts and set it to the last one
        if self.last_post_id is None:
            logger.info(f"Initializing watcher for /{self.board_code}/{self.thread_id}")
            posts = await self.client.get_thread_posts(self.board_code, self.thread_id)
            if posts:
                self.last_post_id = posts[-1].id
                logger.info(f"Started monitoring from post {self.last_post_id}")
            else:
                logger.warning("Thread appears to be empty or non-existent")

        while self._running:
            try:
                new_posts = await self.client.get_new_posts(
                    self.board_code, 
                    self.thread_id, 
                    self.last_post_id or 0
                )
                
                for post in new_posts:
                    if self.last_post_id is None or post.id > self.last_post_id:
                        self.last_post_id = post.id
                        yield post
                
                await asyncio.sleep(self.interval)
            except Exception as e:
                logger.error(f"Error while watching thread: {e}")
                await asyncio.sleep(self.interval)

    def stop(self):
        self._running = False
