import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from dvach.domain.entities import Post, Attachment
from dvach.application.watcher import ThreadWatcher

@pytest.mark.asyncio
async def test_thread_watcher_yields_new_posts():
    # Setup
    mock_client = AsyncMock()
    board = "b"
    thread_id = 123
    
    initial_posts = [
        Post(id=1, comment="first", timestamp=datetime.now(), attachments=[])
    ]
    new_posts = [
        Post(id=2, comment="second", timestamp=datetime.now(), attachments=[])
    ]
    
    mock_client.get_thread_posts.return_value = initial_posts
    mock_client.get_new_posts.side_effect = [new_posts, []] # Yield one post, then nothing
    
    watcher = ThreadWatcher(mock_client, board, thread_id, interval=0.1)
    
    # Execute
    gen = watcher.watch()
    post = await anext(gen)
    
    # Verify
    assert post.id == 2
    assert post.comment == "second"
    assert watcher.last_post_id == 2
    
    watcher.stop()

@pytest.mark.asyncio
async def test_thread_watcher_handles_no_initial_last_id():
    mock_client = AsyncMock()
    mock_client.get_thread_posts.return_value = []
    mock_client.get_new_posts.return_value = [
        Post(id=1, comment="new", timestamp=datetime.now(), attachments=[])
    ]
    
    watcher = ThreadWatcher(mock_client, "b", 123, interval=0.1)
    gen = watcher.watch()
    post = await anext(gen)
    
    assert post.id == 1
    watcher.stop()
