from abc import ABC, abstractmethod
from typing import List, AsyncIterator
from .entities import Board, Thread, Post

class I2chClient(ABC):
    @abstractmethod
    async def get_boards(self) -> List[Board]:
        pass

    @abstractmethod
    async def get_threads(self, board_code: str) -> List[Thread]:
        pass

    @abstractmethod
    async def get_thread_posts(self, board_code: str, thread_id: int) -> List[Post]:
        pass

    @abstractmethod
    async def get_new_posts(self, board_code: str, thread_id: int, last_post_id: int) -> List[Post]:
        pass
