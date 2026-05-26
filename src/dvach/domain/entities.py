from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

@dataclass(frozen=True)
class Attachment:
    path: str
    thumbnail: str
    size: int
    width: int
    height: int
    name: str

    @property
    def url(self) -> str:
        return f"https://2ch.org{self.path}"

    @property
    def thumbnail_url(self) -> str:
        return f"https://2ch.org{self.thumbnail}"

@dataclass(frozen=True)
class Post:
    id: int
    comment: str
    timestamp: datetime
    attachments: List[Attachment] = field(default_factory=list)
    subject: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    trip: Optional[str] = None

@dataclass(frozen=True)
class Thread:
    id: int
    board_code: str
    op_post: Post
    posts_count: int
    files_count: int
    last_hit: datetime
    subject: Optional[str] = None

@dataclass(frozen=True)
class Board:
    code: str
    name: str
    description: str
