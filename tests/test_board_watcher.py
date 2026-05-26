import pytest
import asyncio
from unittest.mock import AsyncMock
from dvach.domain.entities import Thread, Post
from dvach.application.board_watcher import BoardWatcher
from datetime import datetime

@pytest.mark.asyncio
async def test_board_watcher_yields_new_threads():
    # Setup
    mock_client = AsyncMock()
    board = "b"
    
    op_post = Post(id=1, comment="OP", timestamp=datetime.now(), attachments=[])
    
    initial_threads = [
        Thread(id=1, board_code=board, op_post=op_post, posts_count=1, files_count=0)
    ]
    new_threads = [
        Thread(id=2, board_code=board, op_post=op_post, posts_count=1, files_count=0)
    ]
    
    mock_client.get_threads.side_effect = [initial_threads, new_threads, []]
    
    watcher = BoardWatcher(mock_client, board, interval=0.1)
    
    # Execute
    gen = watcher.watch()
    thread = await anext(gen)
    
    # Verify
    assert thread.id == 2
    assert thread.board_code == "b"
    
    watcher.stop()
