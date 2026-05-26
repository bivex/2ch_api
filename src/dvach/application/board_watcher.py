import asyncio
from typing import AsyncIterator, Set, Optional
from loguru import logger
from ..domain.entities import Thread
from ..domain.interfaces import I2chClient

class BoardWatcher:
    def __init__(
        self, 
        client: I2chClient, 
        board_code: str, 
        interval: float = 30.0
    ):
        self.client = client
        self.board_code = board_code
        self.interval = interval
        self._seen_thread_ids: Set[int] = set()
        self._running = False

    async def watch(self) -> AsyncIterator[Thread]:
        self._running = True
        
        # Initialize with current threads
        logger.info(f"Initializing board watcher for /{self.board_code}/")
        try:
            current_threads = await self.client.get_threads(self.board_code)
            self._seen_thread_ids = {t.id for t in current_threads}
            logger.info(f"Started monitoring board /{self.board_code}/ (initial count: {len(self._seen_thread_ids)})")
        except Exception as e:
            logger.error(f"Failed to initialize board watcher: {e}")

        while self._running:
            try:
                await asyncio.sleep(self.interval)
                current_threads = await self.client.get_threads(self.board_code)
                
                for thread in current_threads:
                    if thread.id not in self._seen_thread_ids:
                        self._seen_thread_ids.add(thread.id)
                        yield thread
                        
            except Exception as e:
                logger.error(f"Error while watching board: {e}")

    def stop(self):
        self._running = False